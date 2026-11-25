from typing import Any

from app.api.dependencies import verify_application_api_key
from app.core.config import get_settings
from app.cost.pricing_registry import CATALOG
from app.database.models.application import Application
from app.database.models.model import ModelRegistry
from app.database.session import get_db
from app.providers.factory import get_provider_factory
from app.schemas.response import ModelInfo, ModelUpdateRequest, ProviderStatusInfo
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/models", tags=["Model Registry"])

# Initial default model seed metadata
DEFAULT_MODELS: list[dict[str, Any]] = [
    {
        "id": "model_gpt4o",
        "provider": "openai",
        "model_name": "gpt-4o",
        "input_price_per_million": 2.50,
        "output_price_per_million": 10.00,
        "capabilities": {"chat": True, "vision": True, "function_calling": True},
        "context_window": 128000,
        "is_active": True,
        "pricing_version": "2024-11",
    },
    {
        "id": "model_gpt4o_mini",
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "input_price_per_million": 0.15,
        "output_price_per_million": 0.60,
        "capabilities": {"chat": True, "vision": True, "function_calling": True},
        "context_window": 128000,
        "is_active": True,
        "pricing_version": "2024-11",
    },
    {
        "id": "model_claude35_sonnet",
        "provider": "anthropic",
        "model_name": "claude-3-5-sonnet-20241022",
        "input_price_per_million": 3.00,
        "output_price_per_million": 15.00,
        "capabilities": {"chat": True, "vision": True, "function_calling": True},
        "context_window": 200000,
        "is_active": True,
        "pricing_version": "2024-10",
    },
    {
        "id": "model_claude35_haiku",
        "provider": "anthropic",
        "model_name": "claude-3-5-haiku-20241022",
        "input_price_per_million": 0.80,
        "output_price_per_million": 4.00,
        "capabilities": {"chat": True, "vision": False, "function_calling": True},
        "context_window": 200000,
        "is_active": True,
        "pricing_version": "2024-10",
    },
    {
        "id": "model_gemini15_pro",
        "provider": "gemini",
        "model_name": "gemini-1.5-pro",
        "input_price_per_million": 1.25,
        "output_price_per_million": 5.00,
        "capabilities": {"chat": True, "vision": True, "audio": True},
        "context_window": 1000000,
        "is_active": True,
        "pricing_version": "2024-10",
    },
    {
        "id": "model_gemini15_flash",
        "provider": "gemini",
        "model_name": "gemini-1.5-flash",
        "input_price_per_million": 0.075,
        "output_price_per_million": 0.30,
        "capabilities": {"chat": True, "vision": True, "audio": True},
        "context_window": 1000000,
        "is_active": True,
        "pricing_version": "2024-10",
    },
    {
        "id": "model_ollama_llama32",
        "provider": "ollama",
        "model_name": "llama3.2",
        "input_price_per_million": 0.0,
        "output_price_per_million": 0.0,
        "capabilities": {"chat": True, "local": True},
        "context_window": 8192,
        "is_active": True,
        "pricing_version": "local",
    },
]


@router.get("/providers/status", response_model=list[ProviderStatusInfo])
async def get_providers_status(db: AsyncSession = Depends(get_db)) -> list[ProviderStatusInfo]:
    """
    Returns high-level configuration readiness for each LLM provider without ever exposing secret keys.
    """
    settings = get_settings()
    factory = get_provider_factory()
    availability = await factory.get_availability_status()

    # Count models per provider
    stmt = select(ModelRegistry)
    res = await db.execute(stmt)
    db_models = list(res.scalars().all())
    source = db_models if db_models else DEFAULT_MODELS

    counts: dict[str, int] = {}
    for item in source:
        p = item.provider if isinstance(item, ModelRegistry) else item["provider"]
        counts[p] = counts.get(p, 0) + 1

    def _is_key_set(val: str | None) -> bool:
        return bool(val and not val.startswith("your_") and len(val.strip()) > 6)

    configured_map = {
        "openai": _is_key_set(settings.OPENAI_API_KEY) or availability.get("openai", False),
        "anthropic": _is_key_set(settings.ANTHROPIC_API_KEY) or availability.get("anthropic", False),
        "gemini": _is_key_set(settings.GEMINI_API_KEY) or availability.get("gemini", False),
        "ollama": availability.get("ollama", False),
    }

    return [
        ProviderStatusInfo(
            provider=prov,
            configured=configured_map[prov],
            models_count=counts.get(prov, 0),
            status="connected" if configured_map[prov] else "unconfigured",
        )
        for prov in ["openai", "anthropic", "gemini", "ollama"]
    ]


@router.get("", response_model=list[ModelInfo])
async def list_models(
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db),
) -> list[ModelInfo]:
    """Returns list of registered models from database, falling back to default seed if empty."""
    query = select(ModelRegistry)
    if not include_inactive:
        query = query.where(ModelRegistry.is_active == True)
    result = await db.execute(query)
    models = result.scalars().all()

    if not models:
        return [ModelInfo(**m) for m in DEFAULT_MODELS]

    return [
        ModelInfo(
            id=m.id,
            provider=m.provider,
            model_name=m.model_name,
            input_price_per_million=m.input_price_per_million,
            output_price_per_million=m.output_price_per_million,
            capabilities=m.capabilities or {},
            context_window=m.context_window,
            is_active=m.is_active,
            pricing_version=m.pricing_version,
        )
        for m in models
    ]


@router.get("/{model_id}", response_model=ModelInfo)
async def get_model(model_id: str, db: AsyncSession = Depends(get_db)) -> ModelInfo:
    """Fetch details of a specific registered model."""
    query = select(ModelRegistry).where(
        (ModelRegistry.id == model_id) | (ModelRegistry.model_name == model_id)
    )
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        for item in DEFAULT_MODELS:
            if item["id"] == model_id or item["model_name"] == model_id:
                return ModelInfo(**item)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Model '{model_id}' not found",
        )

    return ModelInfo(
        id=model.id,
        provider=model.provider,
        model_name=model.model_name,
        input_price_per_million=model.input_price_per_million,
        output_price_per_million=model.output_price_per_million,
        capabilities=model.capabilities or {},
        context_window=model.context_window,
        is_active=model.is_active,
        pricing_version=model.pricing_version,
    )


@router.patch("/{model_id}", response_model=ModelInfo)
async def update_model(
    model_id: str,
    payload: ModelUpdateRequest,
    _app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> ModelInfo:
    """Updates pricing or active availability status for a model in the registry."""
    query = select(ModelRegistry).where(
        (ModelRegistry.id == model_id) | (ModelRegistry.model_name == model_id)
    )
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        # Ensure defaults are materialized if editing a catalog default for the first time
        matched_default = next(
            (m for m in DEFAULT_MODELS if m["id"] == model_id or m["model_name"] == model_id),
            None,
        )
        if not matched_default:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Model '{model_id}' not found")

        for item in DEFAULT_MODELS:
            exists_q = await db.execute(select(ModelRegistry).where(ModelRegistry.model_name == item["model_name"]))
            if not exists_q.scalar_one_or_none():
                db.add(ModelRegistry(**item))
        await db.flush()

        result = await db.execute(query)
        model = result.scalar_one()

    if payload.input_price_per_million is not None:
        model.input_price_per_million = payload.input_price_per_million
    if payload.output_price_per_million is not None:
        model.output_price_per_million = payload.output_price_per_million
    if payload.is_active is not None:
        model.is_active = payload.is_active
    if payload.pricing_version is not None:
        model.pricing_version = payload.pricing_version

    await db.commit()
    await db.refresh(model)

    if model.model_name in CATALOG:
        CATALOG[model.model_name].input_price_per_million = model.input_price_per_million
        CATALOG[model.model_name].output_price_per_million = model.output_price_per_million

    return ModelInfo(
        id=model.id,
        provider=model.provider,
        model_name=model.model_name,
        input_price_per_million=model.input_price_per_million,
        output_price_per_million=model.output_price_per_million,
        capabilities=model.capabilities or {},
        context_window=model.context_window,
        is_active=model.is_active,
        pricing_version=model.pricing_version,
    )

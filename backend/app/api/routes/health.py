from datetime import UTC, datetime

from app.core.config import get_settings
from app.database.session import get_db
from app.providers.factory import get_provider_factory
from app.schemas.response import HealthResponse, ReadyResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["Health & Status"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Basic health check endpoint returning server liveness status."""
    return HealthResponse(
        status="healthy",
        environment=settings.ENVIRONMENT,
        version="0.1.0",
        timestamp=datetime.now(UTC),
    )


@router.get("/ready", response_model=ReadyResponse, status_code=status.HTTP_200_OK)
async def readiness_check(db: AsyncSession = Depends(get_db)) -> ReadyResponse:
    """Readiness probe checking database connectivity and provider configuration."""
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e!s}"

    provider_factory = get_provider_factory()
    providers_status = await provider_factory.get_availability_status()

    overall_status = "ready" if db_status == "connected" else "degraded"

    return ReadyResponse(
        status=overall_status,
        database=db_status,
        providers=providers_status,
        timestamp=datetime.now(UTC),
    )

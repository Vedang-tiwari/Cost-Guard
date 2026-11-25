import uuid

from app.api.dependencies import verify_application_api_key
from app.database.models.application import Application
from app.database.models.policy import OptimizationPolicy
from app.database.session import get_db
from app.schemas.policy import OptimizationPolicyResponse, OptimizationPolicyUpdate
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/policies", tags=["Optimization Configuration"])


async def _get_or_create_policy(organization_id: str, db: AsyncSession) -> OptimizationPolicy:
    stmt = select(OptimizationPolicy).where(OptimizationPolicy.organization_id == organization_id)
    res = await db.execute(stmt)
    policy = res.scalar_one_or_none()
    if not policy:
        policy = OptimizationPolicy(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)
    return policy


@router.get("", response_model=OptimizationPolicyResponse)
async def get_optimization_policy(
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> OptimizationPolicyResponse:
    """Retrieves the organization's active Cost Guard optimization policy."""
    policy = await _get_or_create_policy(app.organization_id, db)
    return OptimizationPolicyResponse.model_validate(policy)


@router.put("", response_model=OptimizationPolicyResponse)
async def update_optimization_policy(
    payload: OptimizationPolicyUpdate,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> OptimizationPolicyResponse:
    """Updates optimization toggles, routing strategy, cache thresholds, quality gates, and token caps."""
    policy = await _get_or_create_policy(app.organization_id, db)

    update_fields = payload.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(policy, field, value)

    await db.commit()
    await db.refresh(policy)
    return OptimizationPolicyResponse.model_validate(policy)

from app.api.dependencies import verify_application_api_key
from app.database.models.application import Application
from app.database.models.budget import Budget
from app.database.session import get_db
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/budgets", tags=["Budgets & Cost Control"])


def _to_response(b: Budget) -> BudgetResponse:
    rem = max(0.0, b.limit_amount - b.current_spend)
    pct = round((b.current_spend / b.limit_amount * 100), 2) if b.limit_amount > 0 else 0.0
    return BudgetResponse(
        id=b.id,
        organization_id=b.organization_id,
        application_id=b.application_id,
        budget_type=b.budget_type,
        limit_amount=b.limit_amount,
        warning_threshold=b.warning_threshold,
        hard_limit=b.hard_limit,
        period=b.period,
        current_spend=b.current_spend,
        remaining_amount=round(rem, 4),
        spend_percentage=pct,
        status=b.status,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


@router.get("", response_model=list[BudgetResponse])
async def list_budgets(
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[BudgetResponse]:
    """Lists all configured budgets for the authenticated organization."""
    stmt = select(Budget).where(Budget.organization_id == app.organization_id)
    res = await db.execute(stmt)
    budgets = res.scalars().all()
    return [_to_response(b) for b in budgets]


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> BudgetResponse:
    """Creates a new spending budget for organization or application."""
    org_id = payload.organization_id or app.organization_id
    budget = Budget(
        organization_id=org_id,
        application_id=payload.application_id,
        budget_type=payload.budget_type,
        limit_amount=payload.limit_amount,
        warning_threshold=payload.warning_threshold,
        hard_limit=payload.hard_limit,
        period=payload.period,
    )
    db.add(budget)
    await db.commit()
    await db.refresh(budget)
    return _to_response(budget)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: str,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> BudgetResponse:
    """Retrieves budget details by ID."""
    stmt = select(Budget).where(Budget.id == budget_id, Budget.organization_id == app.organization_id)
    res = await db.execute(stmt)
    budget = res.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return _to_response(budget)


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: str,
    payload: BudgetUpdate,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> BudgetResponse:
    """Updates budget parameters such as limit, warning threshold, or active status."""
    stmt = select(Budget).where(Budget.id == budget_id, Budget.organization_id == app.organization_id)
    res = await db.execute(stmt)
    budget = res.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    if payload.limit_amount is not None:
        budget.limit_amount = payload.limit_amount
    if payload.warning_threshold is not None:
        budget.warning_threshold = payload.warning_threshold
    if payload.hard_limit is not None:
        budget.hard_limit = payload.hard_limit
    if payload.period is not None:
        budget.period = payload.period
    if payload.status is not None:
        budget.status = payload.status

    await db.commit()
    await db.refresh(budget)
    return _to_response(budget)

import logging
from dataclasses import dataclass

from app.budgets.alerts import alert_manager
from app.core.exceptions import BudgetExceededError
from app.database.models.budget import Budget
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("costguard.budgets.manager")


@dataclass
class BudgetCheckResult:
    allowed: bool
    budget_id: str | None = None
    current_spend: float = 0.0
    limit_amount: float = 0.0
    spend_percentage: float = 0.0
    warning: bool = False
    warning_message: str | None = None


class BudgetManager:
    """Manages budget enforcement, spend tracking, and alert triggers."""

    async def get_active_budgets(
        self,
        session: AsyncSession,
        organization_id: str,
        application_id: str | None = None,
    ) -> list[Budget]:
        """Fetches active budgets applicable to the given org and application."""
        stmt = select(Budget).where(
            Budget.organization_id == organization_id,
            Budget.status.in_(["active", "warning"]),
        )
        result = await session.execute(stmt)
        all_budgets = list(result.scalars().all())

        matching: list[Budget] = []
        for b in all_budgets:
            if b.budget_type == "organization":
                matching.append(b)
            elif b.budget_type == "application" and application_id and b.application_id == application_id:
                matching.append(b)

        return matching

    async def check_budget(
        self,
        session: AsyncSession,
        organization_id: str,
        application_id: str | None = None,
        estimated_cost: float = 0.0,
    ) -> BudgetCheckResult:
        """
        Validates whether request can proceed under active budget limits.
        Raises BudgetExceededError if hard limit is breached.
        """
        budgets = await self.get_active_budgets(session, organization_id, application_id)
        if not budgets:
            return BudgetCheckResult(allowed=True)

        for budget in budgets:
            projected = budget.current_spend + estimated_cost
            spend_pct = projected / budget.limit_amount if budget.limit_amount > 0 else 1.0

            # 1. Hard limit breach
            if projected > budget.limit_amount and budget.hard_limit:
                alert_manager.trigger_exceeded(
                    budget.id,
                    organization_id,
                    application_id,
                    projected,
                    budget.limit_amount,
                )
                budget.status = "exceeded"
                await session.flush()
                raise BudgetExceededError(
                    f"Budget limit of ${budget.limit_amount:.2f} exceeded for {budget.budget_type}. "
                    f"Current spend: ${budget.current_spend:.4f}, projected: ${projected:.4f}."
                )

            # 2. Warning threshold
            if spend_pct >= budget.warning_threshold:
                alert_manager.trigger_warning(
                    budget.id,
                    organization_id,
                    application_id,
                    projected,
                    budget.limit_amount,
                    budget.warning_threshold,
                )
                if budget.status == "active":
                    budget.status = "warning"
                    await session.flush()

                return BudgetCheckResult(
                    allowed=True,
                    budget_id=budget.id,
                    current_spend=budget.current_spend,
                    limit_amount=budget.limit_amount,
                    spend_percentage=round(spend_pct * 100, 2),
                    warning=True,
                    warning_message=f"Spend has reached {spend_pct * 100:.1f}% of ${budget.limit_amount:.2f} budget.",
                )

        primary = budgets[0]
        spend_pct = (primary.current_spend / primary.limit_amount * 100) if primary.limit_amount > 0 else 0.0
        return BudgetCheckResult(
            allowed=True,
            budget_id=primary.id,
            current_spend=primary.current_spend,
            limit_amount=primary.limit_amount,
            spend_percentage=round(spend_pct, 2),
        )

    async def record_spend(
        self,
        session: AsyncSession,
        organization_id: str,
        application_id: str | None = None,
        actual_cost: float = 0.0,
    ) -> None:
        """Increments spend on applicable active budgets."""
        if actual_cost <= 0.0:
            return

        budgets = await self.get_active_budgets(session, organization_id, application_id)
        for budget in budgets:
            budget.current_spend = round(budget.current_spend + actual_cost, 6)
            if budget.current_spend >= budget.limit_amount and budget.hard_limit:
                budget.status = "exceeded"
            elif budget.current_spend >= (budget.limit_amount * budget.warning_threshold):
                budget.status = "warning"
        await session.flush()


budget_manager = BudgetManager()

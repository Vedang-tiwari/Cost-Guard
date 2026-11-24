import pytest
from app.budgets.alerts import BudgetAlertManager
from app.budgets.budget_manager import BudgetManager
from app.core.exceptions import BudgetExceededError
from app.database.models.budget import Budget
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_budget_check_allowed_under_limit(db_session: AsyncSession):
    manager = BudgetManager()
    budget = Budget(
        organization_id="org_test_b1",
        budget_type="organization",
        limit_amount=10.0,
        warning_threshold=0.8,
        hard_limit=True,
        current_spend=2.0,
        status="active",
    )
    db_session.add(budget)
    await db_session.commit()

    check = await manager.check_budget(
        session=db_session,
        organization_id="org_test_b1",
        estimated_cost=1.0,
    )
    assert check.allowed is True
    assert check.warning is False


@pytest.mark.asyncio
async def test_budget_warning_threshold(db_session: AsyncSession):
    manager = BudgetManager()
    budget = Budget(
        organization_id="org_test_b2",
        budget_type="organization",
        limit_amount=10.0,
        warning_threshold=0.8,
        hard_limit=True,
        current_spend=7.5,
        status="active",
    )
    db_session.add(budget)
    await db_session.commit()

    # 7.5 + 1.0 = 8.5 (85% >= 80% warning threshold)
    check = await manager.check_budget(
        session=db_session,
        organization_id="org_test_b2",
        estimated_cost=1.0,
    )
    assert check.allowed is True
    assert check.warning is True
    assert "85.0%" in (check.warning_message or "")


@pytest.mark.asyncio
async def test_budget_hard_limit_exceeded(db_session: AsyncSession):
    manager = BudgetManager()
    budget = Budget(
        organization_id="org_test_b3",
        budget_type="organization",
        limit_amount=5.0,
        warning_threshold=0.8,
        hard_limit=True,
        current_spend=4.8,
        status="active",
    )
    db_session.add(budget)
    await db_session.commit()

    # 4.8 + 0.5 = 5.3 > 5.0 -> BudgetExceededError
    with pytest.raises(BudgetExceededError) as exc_info:
        await manager.check_budget(
            session=db_session,
            organization_id="org_test_b3",
            estimated_cost=0.5,
        )
    assert "Budget limit of $5.00 exceeded" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_budget_record_spend(db_session: AsyncSession):
    manager = BudgetManager()
    budget = Budget(
        organization_id="org_test_b4",
        budget_type="organization",
        limit_amount=20.0,
        warning_threshold=0.8,
        hard_limit=True,
        current_spend=5.0,
        status="active",
    )
    db_session.add(budget)
    await db_session.commit()

    await manager.record_spend(
        session=db_session,
        organization_id="org_test_b4",
        actual_cost=2.5,
    )
    assert budget.current_spend == 7.5


def test_budget_alert_manager():
    alerts = BudgetAlertManager()
    alert_w = alerts.trigger_warning(
        budget_id="b1",
        organization_id="org1",
        application_id=None,
        current_spend=8.5,
        limit_amount=10.0,
        warning_threshold=0.8,
    )
    assert alert_w.alert_level == "warning"
    assert alert_w.spend_pct == 85.0

    alert_e = alerts.trigger_exceeded(
        budget_id="b1",
        organization_id="org1",
        application_id=None,
        current_spend=10.5,
        limit_amount=10.0,
    )
    assert alert_e.alert_level == "exceeded"
    assert len(alerts.active_alerts) == 2

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

logger = logging.getLogger("costguard.budgets.alerts")


@dataclass
class BudgetAlert:
    budget_id: str
    organization_id: str
    application_id: str | None
    current_spend: float
    limit_amount: float
    spend_pct: float
    threshold_pct: float
    alert_level: str  # "warning" | "exceeded"
    timestamp: datetime = datetime.now(UTC)


class BudgetAlertManager:
    """Manages and logs budget warning and violation alerts."""

    def __init__(self) -> None:
        self.active_alerts: list[BudgetAlert] = []

    def trigger_warning(
        self,
        budget_id: str,
        organization_id: str,
        application_id: str | None,
        current_spend: float,
        limit_amount: float,
        warning_threshold: float,
    ) -> BudgetAlert:
        spend_pct = round((current_spend / limit_amount) * 100, 1)
        thresh_pct = round(warning_threshold * 100, 1)
        alert = BudgetAlert(
            budget_id=budget_id,
            organization_id=organization_id,
            application_id=application_id,
            current_spend=round(current_spend, 4),
            limit_amount=round(limit_amount, 2),
            spend_pct=spend_pct,
            threshold_pct=thresh_pct,
            alert_level="warning",
        )
        logger.warning(
            f"BUDGET WARNING: Org '{organization_id}' (App: {application_id}) reached "
            f"{spend_pct}% of ${limit_amount:.2f} budget (threshold: {thresh_pct}%). "
            f"Current spend: ${current_spend:.4f}"
        )
        self.active_alerts.append(alert)
        return alert

    def trigger_exceeded(
        self,
        budget_id: str,
        organization_id: str,
        application_id: str | None,
        current_spend: float,
        limit_amount: float,
    ) -> BudgetAlert:
        spend_pct = round((current_spend / limit_amount) * 100, 1)
        alert = BudgetAlert(
            budget_id=budget_id,
            organization_id=organization_id,
            application_id=application_id,
            current_spend=round(current_spend, 4),
            limit_amount=round(limit_amount, 2),
            spend_pct=spend_pct,
            threshold_pct=100.0,
            alert_level="exceeded",
        )
        logger.error(
            f"BUDGET EXCEEDED: Org '{organization_id}' (App: {application_id}) has exceeded "
            f"${limit_amount:.2f} budget! Current spend: ${current_spend:.4f} ({spend_pct}%)"
        )
        self.active_alerts.append(alert)
        return alert


alert_manager = BudgetAlertManager()

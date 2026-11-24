from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BudgetBase(BaseModel):
    limit_amount: float = Field(..., gt=0.0, description="Budget cap in USD")
    warning_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Ratio threshold to fire alerts")
    hard_limit: bool = Field(default=True, description="Whether to block requests once exceeded")
    period: str = Field(default="monthly", description="Budget cycle: daily, weekly, monthly")


class BudgetCreate(BudgetBase):
    organization_id: str
    application_id: str | None = None
    budget_type: str = Field(default="organization", description="'organization' or 'application'")


class BudgetUpdate(BaseModel):
    limit_amount: float | None = Field(default=None, gt=0.0)
    warning_threshold: float | None = Field(default=None, ge=0.0, le=1.0)
    hard_limit: bool | None = None
    period: str | None = None
    status: str | None = None


class BudgetResponse(BudgetBase):
    id: str
    organization_id: str
    application_id: str | None = None
    budget_type: str
    current_spend: float
    remaining_amount: float
    spend_percentage: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

import uuid
from datetime import datetime

from app.database.base import Base, utc_now
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    application_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), nullable=True, index=True)
    budget_type: Mapped[str] = mapped_column(String(50), default="organization", nullable=False)  # "organization" | "application"
    limit_amount: Mapped[float] = mapped_column(Float, nullable=False)  # In USD
    warning_threshold: Mapped[float] = mapped_column(Float, default=0.8, nullable=False)  # 0.8 = 80%
    hard_limit: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    period: Mapped[str] = mapped_column(String(50), default="monthly", nullable=False)  # "daily", "weekly", "monthly"
    current_spend: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)  # "active", "warning", "exceeded", "paused"
    reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organization = relationship("Organization")
    application = relationship("Application")

import uuid
from datetime import datetime
from typing import Any

from app.database.base import Base, utc_now
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    reference_model: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_model: Mapped[str] = mapped_column(String(255), nullable=False)
    total_cases: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overall_quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    quality_retention: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_reference_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_candidate_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cost_savings_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    category_breakdown: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

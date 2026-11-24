import uuid
from datetime import datetime
from typing import Any

from app.database.base import Base, utc_now
from sqlalchemy import JSON, Boolean, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    reference_model: Mapped[str] = mapped_column(String(255), nullable=False)
    candidate_model: Mapped[str] = mapped_column(String(255), nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False)
    evaluation_method: Mapped[str] = mapped_column(String(100), nullable=False)  # "semantic_similarity", "llm_judge", "hybrid", "exact_match"
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    metrics: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

import uuid
from datetime import datetime

from app.database.base import Base, utc_now
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class OptimizationPolicy(Base):
    __tablename__ = "optimization_policies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    intelligent_routing: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    routing_strategy: Mapped[str] = mapped_column(String(50), default="complexity_based", nullable=False)
    semantic_cache: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    cache_similarity_threshold: Mapped[float] = mapped_column(Float, default=0.88, nullable=False)
    prompt_optimization: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quality_gate_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    minimum_quality_score: Mapped[float] = mapped_column(Float, default=0.85, nullable=False)
    fallback_to_premium: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=1024, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

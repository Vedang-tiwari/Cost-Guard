import uuid
from datetime import datetime
from typing import Any

from app.database.base import Base, utc_now
from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class CacheEntry(Base):
    __tablename__ = "cache_entries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("applications.id", ondelete="CASCADE"), index=True, nullable=False)
    organization_id: Mapped[str] = mapped_column(String(36), ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    cache_key: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    # Stored as JSON array of floats for cross-dialect compatibility (SQLite test suite + PostgreSQL)
    embedding: Mapped[list[float]] = mapped_column(JSON, nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_content: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(50), default="v1", nullable=False)
    metadata_info: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    tokens_saved: Mapped[int] = mapped_column(Float, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True)

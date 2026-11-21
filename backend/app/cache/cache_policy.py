from datetime import UTC, datetime, timedelta

from app.schemas.request import ChatCompletionRequest
from pydantic import BaseModel, Field


class CachePolicy(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 86400  # 24 hours default
    similarity_threshold: float = Field(default=0.88, ge=0.5, le=1.0)
    max_temperature_for_cache: float = 0.7  # Non-deterministic high-temp requests shouldn't be cached
    allow_cross_model: bool = True


def is_request_cacheable(request: ChatCompletionRequest, policy: CachePolicy) -> tuple[bool, str]:
    """
    Validates whether an incoming request satisfies caching policy rules.
    Returns (is_cacheable, reason).
    """
    if not policy.enabled:
        return False, "Caching is globally disabled"

    if request.optimization and not request.optimization.semantic_cache:
        return False, "Semantic cache is disabled for this request"

    # Temperature threshold check
    temp = request.temperature if request.temperature is not None else 0.7
    if temp > policy.max_temperature_for_cache:
        return False, f"Temperature {temp} exceeds cacheable threshold ({policy.max_temperature_for_cache})"

    # Streamed requests handled separately
    if request.stream:
        return False, "Streaming requests bypass cache in Phase 2"

    return True, "Request is cacheable"


def compute_expiration(ttl_seconds: int) -> datetime:
    """Calculates UTC expiration timestamp based on TTL."""
    return datetime.now(UTC) + timedelta(seconds=ttl_seconds)

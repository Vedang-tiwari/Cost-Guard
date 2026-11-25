from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OptimizationPolicyUpdate(BaseModel):
    intelligent_routing: bool | None = None
    routing_strategy: str | None = Field(default=None, pattern="^(complexity_based|rule_based|explicit)$")
    semantic_cache: bool | None = None
    cache_similarity_threshold: float | None = Field(default=None, ge=0.5, le=0.99)
    prompt_optimization: bool | None = None
    quality_gate_enabled: bool | None = None
    minimum_quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    fallback_to_premium: bool | None = None
    max_output_tokens: int | None = Field(default=None, ge=64, le=32768)


class OptimizationPolicyResponse(BaseModel):
    id: str
    organization_id: str
    intelligent_routing: bool
    routing_strategy: str
    semantic_cache: bool
    cache_similarity_threshold: float
    prompt_optimization: bool
    quality_gate_enabled: bool
    minimum_quality_score: float
    fallback_to_premium: bool
    max_output_tokens: int
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

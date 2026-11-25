from typing import Literal

from pydantic import BaseModel, Field


class PlaygroundCompareRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    system_prompt: str | None = None
    fixed_model: str = Field(default="gpt-4o")
    semantic_cache: bool = Field(default=True)
    prompt_optimization: bool = Field(default=True)
    intelligent_routing: bool = Field(default=True)
    routing_strategy: str = Field(default="complexity_based")
    minimum_quality_score: float = Field(default=0.85, ge=0.0, le=1.0)
    max_tokens: int = Field(default=512, ge=16, le=8192)
    execution_mode: Literal["live", "simulate"] = Field(default="simulate")


class PlaygroundSideResult(BaseModel):
    model: str
    provider: str
    response_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    baseline_cost: float
    savings: float
    savings_percentage: float
    latency_ms: float
    cache_hit: bool
    prompt_optimized: bool
    tokens_saved_by_prompt: int = 0
    optimized_prompt_preview: str | None = None
    complexity_score: float
    task_type: str
    routing_strategy: str
    routing_reason: str
    quality_score: float | None = None
    fallback_used: bool = False


class PlaygroundCompareResponse(BaseModel):
    execution_mode: str
    fixed: PlaygroundSideResult
    optimized: PlaygroundSideResult

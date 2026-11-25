from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssistantMessage(BaseModel):
    role: str = Field(default="assistant")
    content: str = Field(..., description="Generated text content")


class UsageInfo(BaseModel):
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)


class CostInfo(BaseModel):
    estimated_cost: float = Field(default=0.0, ge=0.0)
    baseline_cost: float = Field(default=0.0, ge=0.0)
    savings: float = Field(default=0.0)
    savings_percentage: float = Field(default=0.0)


class OptimizationInfo(BaseModel):
    cache_hit: bool = Field(default=False)
    routing_strategy: str = Field(default="explicit")
    complexity_score: float = Field(default=0.0)
    prompt_optimized: bool = Field(default=False)
    fallback_used: bool = Field(default=False)
    quality_score: float | None = Field(default=None)


class ChatCompletionResponse(BaseModel):
    request_id: str = Field(..., description="Unique request tracking identifier")
    model: str = Field(..., description="Model that processed the request")
    provider: str = Field(..., description="Provider that processed the request")
    response: AssistantMessage = Field(..., description="Assistant response payload")
    usage: UsageInfo = Field(..., description="Token usage details")
    cost: CostInfo = Field(..., description="Cost calculations")
    optimization: OptimizationInfo = Field(..., description="Optimization telemetry")


class ModelInfo(BaseModel):
    id: str
    provider: str
    model_name: str
    input_price_per_million: float
    output_price_per_million: float
    capabilities: dict[str, Any]
    context_window: int
    is_active: bool
    pricing_version: str


class ModelUpdateRequest(BaseModel):
    input_price_per_million: float | None = Field(default=None, ge=0.0)
    output_price_per_million: float | None = Field(default=None, ge=0.0)
    is_active: bool | None = None
    pricing_version: str | None = None


class ProviderStatusInfo(BaseModel):
    provider: str
    configured: bool
    models_count: int
    status: str


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str = "0.1.0"
    timestamp: datetime


class ReadyResponse(BaseModel):
    status: str
    database: str
    providers: dict[str, bool]
    timestamp: datetime

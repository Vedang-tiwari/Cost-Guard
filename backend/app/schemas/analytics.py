from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class OverviewStats(BaseModel):
    total_requests: int
    total_spend: float
    baseline_cost: float
    total_savings: float
    savings_percentage: float
    avg_cost_per_request: float = 0.0
    cache_hit_rate: float
    avg_quality_score: float = 0.0
    avg_latency_ms: float
    p95_latency_ms: float
    fallback_rate: float


class CostTimePoint(BaseModel):
    date: str
    actual_cost: float
    baseline_cost: float
    savings: float
    requests_count: int


class CostAnalytics(BaseModel):
    total_spend: float
    baseline_spend: float
    total_savings: float
    breakdown: list[CostTimePoint]
    by_provider: list[dict[str, Any]] = Field(default_factory=list)
    by_model: list[dict[str, Any]] = Field(default_factory=list)
    by_application: list[dict[str, Any]] = Field(default_factory=list)
    token_costs: dict[str, float] = Field(default_factory=dict)


class ModelStat(BaseModel):
    model: str
    provider: str
    request_count: int
    share_pct: float
    input_tokens: int
    output_tokens: int
    total_cost: float
    avg_latency_ms: float
    avg_quality_score: float | None = None


class ModelAnalytics(BaseModel):
    total_models_used: int
    models: list[ModelStat]


class SavingsSourceBreakdown(BaseModel):
    cache_savings: float
    compression_savings: float
    routing_savings: float


class SavingsAnalytics(BaseModel):
    total_savings: float
    savings_percentage: float
    sources: SavingsSourceBreakdown
    monthly_projected_savings: float


class RequestLogItem(BaseModel):
    request_id: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    actual_cost: float
    savings: float
    latency_ms: float
    cache_hit: bool
    complexity_score: float
    routing_strategy: str
    quality_score: float | None = None
    fallback_used: bool
    status: str
    created_at: datetime

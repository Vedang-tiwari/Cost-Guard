from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_requests: int
    total_spend: float
    baseline_cost: float
    total_savings: float
    savings_percentage: float
    cache_hit_rate: float
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


class ModelStat(BaseModel):
    model: str
    provider: str
    request_count: int
    share_pct: float
    input_tokens: int
    output_tokens: int
    total_cost: float
    avg_latency_ms: float


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

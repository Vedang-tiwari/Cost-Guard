from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BenchmarkRunRequest(BaseModel):
    candidate_models: list[str] = Field(
        default=["gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022"]
    )
    reference_model: str = Field(default="gpt-4o")


class BenchmarkRunResponse(BaseModel):
    id: str
    reference_model: str
    candidate_model: str
    total_cases: int
    overall_quality_score: float
    quality_retention: float
    total_reference_cost: float
    total_candidate_cost: float
    cost_savings_pct: float
    category_breakdown: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRunRequest(BaseModel):
    candidate_response: str = Field(..., description="The response to evaluate")
    reference_response: str | None = Field(default=None, description="Ground truth or reference response")
    expected_output: str | None = Field(default=None, description="Expected exact or target output")
    prompt: str = Field(default="", description="The user prompt that generated the response")
    task_type: str = Field(default="general", description="Task category for specialized rubrics")
    expected_schema: dict[str, Any] | None = Field(default=None, description="Expected JSON schema if applicable")
    method: str = Field(default="auto", description="'auto', 'exact_match', 'semantic', 'schema', 'llm_judge', 'rubric'")
    threshold: float | None = Field(default=None, ge=0.0, le=1.0, description="Passing score threshold")


class EvaluationResponse(BaseModel):
    id: str | None = None
    request_id: str | None = None
    reference_model: str | None = None
    candidate_model: str | None = None
    quality_score: float
    passed: bool
    evaluation_method: str
    metrics: dict[str, Any] = Field(default_factory=dict)
    reasoning: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

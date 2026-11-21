import re
from typing import Any

from app.analyzer.task_classifier import classify_task
from app.analyzer.token_estimator import estimate_tokens
from app.schemas.request import ChatMessage
from pydantic import BaseModel, Field


class ComplexityAnalysisResult(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Complexity score between 0 and 100")
    tier: str = Field(..., description="Complexity tier: low, medium, or high")
    task_type: str = Field(..., description="Classified task category")
    confidence: float = Field(..., description="Classification confidence")
    factors: dict[str, Any] = Field(default_factory=dict, description="Contributing score factors")


# Base score per task category
TASK_BASE_SCORES: dict[str, float] = {
    "classification": 15.0,
    "conversational": 20.0,
    "extraction": 35.0,
    "summarization": 40.0,
    "math": 60.0,
    "code": 70.0,
    "reasoning": 75.0,
}


def analyze_complexity(messages: list[ChatMessage]) -> ComplexityAnalysisResult:
    """
    Evaluates request complexity on a scale of 0 to 100 based on:
    - Task type baseline
    - Prompt length / token volume
    - Instruction density (step-by-step instructions, multiple constraints)
    - Structural constraints (JSON schema, format restrictions)
    - Reasoning indicators
    """
    combined_prompt = " ".join([m.content for m in messages if m.role in ("user", "system")])
    user_prompt = " ".join([m.content for m in messages if m.role == "user"])

    task_class = classify_task(user_prompt or combined_prompt)
    base_score = TASK_BASE_SCORES.get(task_class.task_type, 30.0)

    factors: dict[str, Any] = {
        "task_type": task_class.task_type,
        "task_base_score": base_score,
    }

    # Factor 1: Token volume factor (up to +20 points)
    token_count = estimate_tokens(combined_prompt)
    length_penalty = 0.0
    if token_count > 2000:
        length_penalty = 20.0
    elif token_count > 1000:
        length_penalty = 15.0
    elif token_count > 500:
        length_penalty = 10.0
    elif token_count > 200:
        length_penalty = 5.0
    factors["length_score"] = length_penalty

    # Factor 2: Instruction density (numbered lists, bullet points) (up to +15 points)
    instruction_points = min(15.0, len(re.findall(r"(?m)^\s*(?:\d+[\.\)]|[-*])\s+", combined_prompt)) * 3.0)
    factors["instruction_density_score"] = instruction_points

    # Factor 3: Constraints and format requirements (up to +15 points)
    constraint_matches = len(re.findall(
        r"\b(must not|do not|never|strictly|only|always|format:|schema:)\b",
        combined_prompt,
        re.IGNORECASE
    ))
    constraint_points = min(15.0, constraint_matches * 3.0)
    factors["constraint_score"] = constraint_points

    # Factor 4: Deep reasoning markers (up to +15 points)
    reasoning_matches = len(re.findall(
        r"\b(step by step|chain of thought|first principles|trade-offs|implications|in-depth)\b",
        combined_prompt,
        re.IGNORECASE
    ))
    reasoning_points = min(15.0, reasoning_matches * 5.0)
    factors["reasoning_score"] = reasoning_points

    raw_score = base_score + length_penalty + instruction_points + constraint_points + reasoning_points
    final_score = round(max(0.0, min(100.0, raw_score)), 1)

    # Determine tier based on instruction.md thresholds:
    # Low: 0-30, Medium: 31-65, High: 66-100
    if final_score <= 30.0:
        tier = "low"
    elif final_score <= 65.0:
        tier = "medium"
    else:
        tier = "high"

    return ComplexityAnalysisResult(
        score=final_score,
        tier=tier,
        task_type=task_class.task_type,
        confidence=task_class.confidence,
        factors=factors,
    )

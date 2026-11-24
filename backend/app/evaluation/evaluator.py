from typing import Any

from app.evaluation.llm_judge import LLMJudge
from app.evaluation.quality_metrics import (
    exact_match,
    json_schema_validity,
    length_consistency,
    semantic_similarity,
    task_rubric_score,
)
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0, description="Overall quality score between 0.0 and 1.0")
    passed: bool = Field(..., description="Whether score meets the required threshold")
    method: str = Field(..., description="Evaluation method used")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Detailed dimension metrics")
    reasoning: str = Field(default="", description="Explanation or summary of the evaluation")


class QualityEvaluator:
    """
    Unified quality evaluation engine.
    Scores responses across dimensions (correctness, adherence, format, completeness)
    and validates outputs against thresholds.
    """

    def __init__(self, default_threshold: float = 0.8, provider_factory: Any | None = None) -> None:
        self.default_threshold = default_threshold
        self.llm_judge = LLMJudge(provider_factory=provider_factory)

    async def evaluate(
        self,
        candidate: str,
        reference: str | None = None,
        expected_output: str | None = None,
        prompt: str = "",
        task_type: str = "general",
        expected_schema: dict[str, Any] | None = None,
        method: str = "auto",
        threshold: float | None = None,
    ) -> EvaluationResult:
        """
        Evaluates a candidate response.
        Available methods:
        - "auto": dynamically selects appropriate evaluation strategy
        - "exact_match": exact string equivalence
        - "semantic": cosine similarity of embedding vectors
        - "schema": JSON validity and schema conformance
        - "llm_judge": multi-dimension LLM judge (or deterministic heuristic fallback)
        - "rubric": task-specific rubric scoring
        """
        min_threshold = threshold if threshold is not None else self.default_threshold
        target_ref = reference or expected_output

        # 1. Exact Match Method
        if method == "exact_match":
            score = exact_match(candidate, target_ref or "")
            return EvaluationResult(
                score=score,
                passed=score >= min_threshold,
                method="exact_match",
                metrics={"exact_match": score},
                reasoning=f"Exact match check: {score == 1.0}",
            )

        # 2. Schema Validation Method
        if method == "schema" or expected_schema is not None or task_type == "structured_output":
            schema_score, schema_details = json_schema_validity(candidate, expected_schema)
            # If reference is available, blend schema validity with semantic content
            if target_ref:
                sem = semantic_similarity(candidate, target_ref)
                composite = round(0.5 * schema_score + 0.5 * sem, 4)
            else:
                composite = schema_score

            return EvaluationResult(
                score=composite,
                passed=composite >= min_threshold,
                method="schema",
                metrics={"schema_score": schema_score, "details": schema_details},
                reasoning=f"JSON schema validity score: {schema_score:.2f}",
            )

        # 3. LLM Judge Method
        if method == "llm_judge" and target_ref:
            judge_res = await self.llm_judge.judge(candidate, target_ref, prompt=prompt)
            score = judge_res["score"]
            return EvaluationResult(
                score=score,
                passed=score >= min_threshold,
                method=judge_res.get("method", "llm_judge"),
                metrics=judge_res.get("dimensions", {}),
                reasoning=judge_res.get("reasoning", "LLM Judge evaluation completed."),
            )

        # 4. Semantic Similarity Method
        if method == "semantic" and target_ref:
            sim = semantic_similarity(candidate, target_ref)
            return EvaluationResult(
                score=sim,
                passed=sim >= min_threshold,
                method="semantic",
                metrics={"semantic_similarity": sim},
                reasoning=f"Semantic embedding similarity: {sim:.2f}",
            )

        # 5. Rubric Method
        if method == "rubric":
            rubric = task_rubric_score(candidate, task_type, target_ref)
            return EvaluationResult(
                score=rubric,
                passed=rubric >= min_threshold,
                method="rubric",
                metrics={"rubric_score": rubric, "task_type": task_type},
                reasoning=f"Task rubric score ({task_type}): {rubric:.2f}",
            )

        # 6. Auto / Hybrid Mode (Default)
        if target_ref:
            # Classification task with known target
            if task_type == "classification":
                em = exact_match(candidate, target_ref, case_sensitive=False)
                sim = semantic_similarity(candidate, target_ref)
                score = max(em, sim)
                return EvaluationResult(
                    score=score,
                    passed=score >= min_threshold,
                    method="auto_classification",
                    metrics={"exact_match": em, "semantic_similarity": sim},
                    reasoning=f"Classification score: {score:.2f}",
                )

            # General tasks with reference output
            sim = semantic_similarity(candidate, target_ref)
            length_score = length_consistency(candidate, target_ref)
            rubric = task_rubric_score(candidate, task_type, target_ref)

            composite = round((0.6 * sim) + (0.2 * length_score) + (0.2 * rubric), 4)
            return EvaluationResult(
                score=composite,
                passed=composite >= min_threshold,
                method="auto_hybrid",
                metrics={
                    "semantic_similarity": sim,
                    "length_consistency": length_score,
                    "rubric_score": rubric,
                },
                reasoning=f"Composite quality score: {composite:.2f} (semantic={sim:.2f}, length={length_score:.2f}, rubric={rubric:.2f})",
            )

        # No reference provided: evaluate intrinsic quality rubric
        rubric = task_rubric_score(candidate, task_type)
        return EvaluationResult(
            score=rubric,
            passed=rubric >= min_threshold,
            method="intrinsic_rubric",
            metrics={"rubric_score": rubric, "task_type": task_type},
            reasoning=f"Intrinsic quality rubric ({task_type}): {rubric:.2f}",
        )

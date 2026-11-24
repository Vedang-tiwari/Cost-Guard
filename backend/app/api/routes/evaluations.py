import uuid

from app.api.dependencies import verify_application_api_key
from app.database.models.application import Application
from app.database.models.evaluation import Evaluation
from app.database.session import get_db
from app.evaluation.evaluator import QualityEvaluator
from app.schemas.evaluation import EvaluationResponse, EvaluationRunRequest
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/evaluations", tags=["Quality Evaluations"])
evaluator = QualityEvaluator()


@router.post("/run", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
async def run_evaluation(
    payload: EvaluationRunRequest,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> EvaluationResponse:
    """
    Evaluates candidate model output against reference output or criteria.
    Supports semantic similarity, exact match, JSON schema validity, LLM judge, and rubrics.
    """
    res = await evaluator.evaluate(
        candidate=payload.candidate_response,
        reference=payload.reference_response,
        expected_output=payload.expected_output,
        prompt=payload.prompt,
        task_type=payload.task_type,
        expected_schema=payload.expected_schema,
        method=payload.method,
        threshold=payload.threshold,
    )

    eval_record = Evaluation(
        id=str(uuid.uuid4()),
        request_id=f"eval-{uuid.uuid4().hex[:12]}",
        reference_model="reference",
        candidate_model="candidate",
        quality_score=res.score,
        evaluation_method=res.method,
        passed=res.passed,
        metrics=res.metrics,
    )
    db.add(eval_record)
    await db.commit()
    await db.refresh(eval_record)

    return EvaluationResponse(
        id=eval_record.id,
        request_id=eval_record.request_id,
        reference_model=eval_record.reference_model,
        candidate_model=eval_record.candidate_model,
        quality_score=res.score,
        passed=res.passed,
        evaluation_method=res.method,
        metrics=res.metrics,
        reasoning=res.reasoning,
        created_at=eval_record.created_at,
    )


@router.get("", response_model=list[EvaluationResponse])
async def list_evaluations(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[EvaluationResponse]:
    """Retrieves recent quality evaluation records."""
    stmt = (
        select(Evaluation)
        .order_by(desc(Evaluation.created_at))
        .offset(offset)
        .limit(limit)
    )
    res = await db.execute(stmt)
    records = res.scalars().all()

    return [
        EvaluationResponse(
            id=r.id,
            request_id=r.request_id,
            reference_model=r.reference_model,
            candidate_model=r.candidate_model,
            quality_score=r.quality_score,
            passed=r.passed,
            evaluation_method=r.evaluation_method,
            metrics=r.metrics or {},
            created_at=r.created_at,
        )
        for r in records
    ]

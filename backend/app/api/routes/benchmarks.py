import uuid
from pathlib import Path

from app.api.dependencies import verify_application_api_key
from app.database.models.application import Application
from app.database.models.benchmark_run import BenchmarkRun
from app.database.session import get_db
from app.evaluation.benchmark import BenchmarkSuite
from app.schemas.benchmark import BenchmarkRunRequest, BenchmarkRunResponse
from fastapi import APIRouter, Depends, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/benchmarks", tags=["Benchmark Suite"])


def _dataset_path() -> Path:
    candidates = [
        Path(__file__).resolve().parents[4] / "benchmarks" / "datasets" / "test_prompts.json",
        Path(__file__).resolve().parents[3] / "benchmarks" / "datasets" / "test_prompts.json",
        Path("/benchmarks/datasets/test_prompts.json"),
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


async def _run_and_persist_defaults(org_id: str, db: AsyncSession) -> list[BenchmarkRun]:
    suite = BenchmarkSuite()
    items = suite.load_dataset(_dataset_path())
    if not items:
        return []

    created: list[BenchmarkRun] = []
    for candidate in ["gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022"]:
        summary = await suite.run_benchmark(
            items=items,
            candidate_model=candidate,
            reference_model="gpt-4o",
        )
        run = BenchmarkRun(
            id=str(uuid.uuid4()),
            organization_id=org_id,
            reference_model=summary.reference_model,
            candidate_model=summary.candidate_model,
            total_cases=summary.total_cases,
            overall_quality_score=summary.overall_quality_score,
            quality_retention=summary.quality_retention,
            total_reference_cost=summary.total_reference_cost,
            total_candidate_cost=summary.total_candidate_cost,
            cost_savings_pct=summary.cost_savings_pct,
            category_breakdown=summary.category_breakdown,
        )
        db.add(run)
        created.append(run)

    await db.commit()
    for r in created:
        await db.refresh(r)
    return created


@router.get("/results", response_model=list[BenchmarkRunResponse])
async def get_benchmark_results(
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[BenchmarkRunResponse]:
    """Lists recent benchmark runs; automatically executes initial suite against test_prompts.json if empty."""
    stmt = (
        select(BenchmarkRun)
        .where(BenchmarkRun.organization_id == app.organization_id)
        .order_by(desc(BenchmarkRun.created_at))
        .limit(30)
    )
    res = await db.execute(stmt)
    runs = list(res.scalars().all())

    if not runs:
        runs = await _run_and_persist_defaults(app.organization_id, db)

    return [BenchmarkRunResponse.model_validate(r) for r in runs]


@router.post("/run", response_model=list[BenchmarkRunResponse], status_code=status.HTTP_201_CREATED)
async def trigger_benchmark_run(
    payload: BenchmarkRunRequest,
    app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[BenchmarkRunResponse]:
    """Executes the benchmark dataset across selected candidate models against a reference baseline."""
    suite = BenchmarkSuite()
    items = suite.load_dataset(_dataset_path())
    created: list[BenchmarkRun] = []

    for candidate in payload.candidate_models:
        summary = await suite.run_benchmark(
            items=items,
            candidate_model=candidate,
            reference_model=payload.reference_model,
        )
        run = BenchmarkRun(
            id=str(uuid.uuid4()),
            organization_id=app.organization_id,
            reference_model=summary.reference_model,
            candidate_model=summary.candidate_model,
            total_cases=summary.total_cases,
            overall_quality_score=summary.overall_quality_score,
            quality_retention=summary.quality_retention,
            total_reference_cost=summary.total_reference_cost,
            total_candidate_cost=summary.total_candidate_cost,
            cost_savings_pct=summary.cost_savings_pct,
            category_breakdown=summary.category_breakdown,
        )
        db.add(run)
        created.append(run)

    await db.commit()
    for r in created:
        await db.refresh(r)

    return [BenchmarkRunResponse.model_validate(r) for r in created]

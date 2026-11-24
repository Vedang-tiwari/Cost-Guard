import pytest
from app.analytics.aggregator import AnalyticsAggregator
from app.analytics.reports import ReportGenerator
from app.database.models.request_log import RequestLog
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_analytics_overview_empty(db_session: AsyncSession):
    agg = AnalyticsAggregator()
    overview = await agg.get_overview(db_session, organization_id="org_empty")
    assert overview["total_requests"] == 0
    assert overview["total_spend"] == 0.0
    assert overview["savings_percentage"] == 0.0


@pytest.mark.asyncio
async def test_analytics_overview_with_logs(db_session: AsyncSession):
    agg = AnalyticsAggregator()

    log1 = RequestLog(
        request_id="r1",
        organization_id="org_analytics_1",
        provider="openai",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        estimated_cost=0.010,
        actual_cost=0.001,
        latency_ms=150.0,
        cache_hit=False,
        complexity_score=25.0,
        routing_strategy="complexity_based",
        fallback_used=False,
        status="success",
    )
    log2 = RequestLog(
        request_id="r2",
        organization_id="org_analytics_1",
        provider="cache",
        model="gpt-4o-mini",
        input_tokens=100,
        output_tokens=50,
        estimated_cost=0.010,
        actual_cost=0.0,
        latency_ms=10.0,
        cache_hit=True,
        complexity_score=25.0,
        routing_strategy="semantic_cache",
        fallback_used=False,
        status="success",
    )
    db_session.add_all([log1, log2])
    await db_session.commit()

    overview = await agg.get_overview(db_session, organization_id="org_analytics_1")
    assert overview["total_requests"] == 2
    assert overview["total_spend"] == 0.001
    assert overview["baseline_cost"] == 0.020
    assert overview["total_savings"] == 0.019
    assert overview["savings_percentage"] == 95.0
    assert overview["cache_hit_rate"] == 50.0


@pytest.mark.asyncio
async def test_analytics_models_and_savings(db_session: AsyncSession):
    agg = AnalyticsAggregator()
    log = RequestLog(
        request_id="r3",
        organization_id="org_analytics_2",
        provider="gemini",
        model="gemini-1.5-flash",
        input_tokens=200,
        output_tokens=100,
        estimated_cost=0.020,
        actual_cost=0.002,
        latency_ms=220.0,
        cache_hit=False,
        complexity_score=30.0,
        routing_strategy="complexity_based",
        status="success",
    )
    db_session.add(log)
    await db_session.commit()

    models_res = await agg.get_models(db_session, organization_id="org_analytics_2")
    assert models_res["total_models_used"] == 1
    assert models_res["models"][0]["model"] == "gemini-1.5-flash"
    assert models_res["models"][0]["share_pct"] == 100.0

    savings_res = await agg.get_savings(db_session, organization_id="org_analytics_2")
    assert savings_res["total_savings"] == 0.018
    assert savings_res["savings_percentage"] == 90.0


def test_reports_generator():
    reports = ReportGenerator()
    md = reports.format_summary_markdown({
        "total_requests": 100,
        "total_spend": 5.25,
        "baseline_cost": 25.00,
        "total_savings": 19.75,
        "savings_percentage": 79.0,
        "cache_hit_rate": 35.0,
        "avg_latency_ms": 180.0,
        "p95_latency_ms": 320.0,
        "fallback_rate": 2.0,
    })
    assert "# Cost Guard Analytics Summary" in md
    assert "79.0%" in md

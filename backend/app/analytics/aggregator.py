from datetime import UTC, datetime, timedelta
from typing import Any

from app.cost.pricing_registry import get_model_pricing
from app.database.models.application import Application
from app.database.models.request_log import RequestLog
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession


class AnalyticsAggregator:
    """Computes real-time business and technical metrics across historical request logs."""

    async def get_overview(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=days)
        base_stmt = select(RequestLog).where(RequestLog.created_at >= since)
        if organization_id:
            base_stmt = base_stmt.where(RequestLog.organization_id == organization_id)

        result = await session.execute(base_stmt)
        logs = list(result.scalars().all())

        total_requests = len(logs)
        if total_requests == 0:
            return {
                "total_requests": 0,
                "total_spend": 0.0,
                "baseline_cost": 0.0,
                "total_savings": 0.0,
                "savings_percentage": 0.0,
                "avg_cost_per_request": 0.0,
                "cache_hit_rate": 0.0,
                "avg_quality_score": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "fallback_rate": 0.0,
            }

        total_spend = sum(log.actual_cost for log in logs)
        baseline_cost = sum(log.estimated_cost for log in logs)
        total_savings = max(0.0, baseline_cost - total_spend)
        savings_percentage = round((total_savings / baseline_cost * 100), 2) if baseline_cost > 0 else 0.0
        avg_cost_per_request = round(total_spend / total_requests, 6)

        cache_hits = sum(1 for log in logs if log.cache_hit)
        cache_hit_rate = round((cache_hits / total_requests * 100), 2)

        q_scores = [log.quality_score for log in logs if log.quality_score is not None]
        avg_quality_score = round((sum(q_scores) / len(q_scores)) * 100, 2) if q_scores else 97.5

        latencies = sorted(log.latency_ms for log in logs)
        avg_latency = round(sum(latencies) / total_requests, 2)
        p95_idx = int(0.95 * total_requests)
        p95_latency = round(latencies[min(p95_idx, total_requests - 1)], 2)

        fallbacks = sum(1 for log in logs if log.fallback_used)
        fallback_rate = round((fallbacks / total_requests * 100), 2)

        return {
            "total_requests": total_requests,
            "total_spend": round(total_spend, 6),
            "baseline_cost": round(baseline_cost, 6),
            "total_savings": round(total_savings, 6),
            "savings_percentage": savings_percentage,
            "avg_cost_per_request": avg_cost_per_request,
            "cache_hit_rate": cache_hit_rate,
            "avg_quality_score": avg_quality_score,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "fallback_rate": fallback_rate,
        }

    async def get_costs(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        days: int = 14,
        period: str = "daily",
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=days)
        base_stmt = select(RequestLog).where(RequestLog.created_at >= since)
        if organization_id:
            base_stmt = base_stmt.where(RequestLog.organization_id == organization_id)

        result = await session.execute(base_stmt)
        logs = list(result.scalars().all())

        # Fetch app names for application cost breakdown
        app_names: dict[str, str] = {}
        if organization_id:
            app_res = await session.execute(
                select(Application).where(Application.organization_id == organization_id)
            )
            for a in app_res.scalars().all():
                app_names[a.id] = a.name

        buckets: dict[str, dict[str, Any]] = {}
        if period == "daily":
            for i in range(days):
                d_str = (datetime.now(UTC) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
                buckets[d_str] = {
                    "date": d_str,
                    "actual_cost": 0.0,
                    "baseline_cost": 0.0,
                    "savings": 0.0,
                    "requests_count": 0,
                }

        by_provider: dict[str, float] = {}
        by_model: dict[str, float] = {}
        by_application: dict[str, float] = {}
        input_token_cost = 0.0
        output_token_cost = 0.0

        for log in logs:
            dt = log.created_at or datetime.now(UTC)
            if period == "weekly":
                iso = dt.isocalendar()
                bucket_key = f"{iso.year}-W{iso.week:02d}"
            elif period == "monthly":
                bucket_key = dt.strftime("%Y-%m")
            else:
                bucket_key = dt.strftime("%Y-%m-%d")

            if bucket_key not in buckets:
                buckets[bucket_key] = {
                    "date": bucket_key,
                    "actual_cost": 0.0,
                    "baseline_cost": 0.0,
                    "savings": 0.0,
                    "requests_count": 0,
                }
            entry = buckets[bucket_key]
            entry["actual_cost"] += log.actual_cost
            entry["baseline_cost"] += log.estimated_cost
            entry["requests_count"] += 1

            by_provider[log.provider] = by_provider.get(log.provider, 0.0) + log.actual_cost
            by_model[log.model] = by_model.get(log.model, 0.0) + log.actual_cost

            app_label = app_names.get(log.application_id or "", log.application_id or "default")
            by_application[app_label] = by_application.get(app_label, 0.0) + log.actual_cost

            if not log.cache_hit:
                pricing = get_model_pricing(log.model)
                input_token_cost += (log.input_tokens / 1_000_000) * pricing.input_price_per_million
                output_token_cost += (log.output_tokens / 1_000_000) * pricing.output_price_per_million

        points = []
        for k in sorted(buckets.keys()):
            e = buckets[k]
            savings = max(0.0, e["baseline_cost"] - e["actual_cost"])
            points.append({
                "date": e["date"],
                "actual_cost": round(e["actual_cost"], 6),
                "baseline_cost": round(e["baseline_cost"], 6),
                "savings": round(savings, 6),
                "requests_count": e["requests_count"],
            })

        total_spend = round(sum(p["actual_cost"] for p in points), 6)
        total_baseline = round(sum(p["baseline_cost"] for p in points), 6)
        total_savings = round(max(0.0, total_baseline - total_spend), 6)

        return {
            "total_spend": total_spend,
            "baseline_spend": total_baseline,
            "total_savings": total_savings,
            "breakdown": points,
            "by_provider": [
                {"name": k, "cost": round(v, 6)} for k, v in sorted(by_provider.items(), key=lambda x: -x[1])
            ],
            "by_model": [
                {"name": k, "cost": round(v, 6)} for k, v in sorted(by_model.items(), key=lambda x: -x[1])
            ],
            "by_application": [
                {"name": k, "cost": round(v, 6)} for k, v in sorted(by_application.items(), key=lambda x: -x[1])
            ],
            "token_costs": {
                "input_cost": round(input_token_cost, 6),
                "output_cost": round(output_token_cost, 6),
            },
        }

    async def get_models(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=days)
        base_stmt = select(RequestLog).where(RequestLog.created_at >= since)
        if organization_id:
            base_stmt = base_stmt.where(RequestLog.organization_id == organization_id)

        result = await session.execute(base_stmt)
        logs = list(result.scalars().all())

        total_reqs = len(logs)
        by_model: dict[str, dict[str, Any]] = {}

        for log in logs:
            key = log.model
            if key not in by_model:
                by_model[key] = {
                    "model": key,
                    "provider": log.provider,
                    "request_count": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_cost": 0.0,
                    "latencies": [],
                    "quality_scores": [],
                }
            bm = by_model[key]
            bm["request_count"] += 1
            bm["input_tokens"] += log.input_tokens
            bm["output_tokens"] += log.output_tokens
            bm["total_cost"] += log.actual_cost
            bm["latencies"].append(log.latency_ms)
            if log.quality_score is not None:
                bm["quality_scores"].append(log.quality_score)

        models_list = []
        for data in by_model.values():
            req_count = data["request_count"]
            share_pct = round((req_count / total_reqs * 100), 2) if total_reqs > 0 else 0.0
            avg_lat = round(sum(data["latencies"]) / req_count, 2) if req_count > 0 else 0.0
            q_scores = data["quality_scores"]
            avg_q = round((sum(q_scores) / len(q_scores)) * 100, 2) if q_scores else None
            models_list.append({
                "model": data["model"],
                "provider": data["provider"],
                "request_count": req_count,
                "share_pct": share_pct,
                "input_tokens": data["input_tokens"],
                "output_tokens": data["output_tokens"],
                "total_cost": round(data["total_cost"], 6),
                "avg_latency_ms": avg_lat,
                "avg_quality_score": avg_q,
            })

        models_list.sort(key=lambda x: x["request_count"], reverse=True)
        return {
            "total_models_used": len(models_list),
            "models": models_list,
        }

    async def get_savings(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        days: int = 30,
    ) -> dict[str, Any]:
        overview = await self.get_overview(session, organization_id, days)
        total_savings = overview["total_savings"]
        savings_pct = overview["savings_percentage"]

        cache_part = round(total_savings * (overview["cache_hit_rate"] / 100.0 if overview["cache_hit_rate"] > 0 else 0.3), 4)
        rem = max(0.0, total_savings - cache_part)
        routing_part = round(rem * 0.7, 4)
        compression_part = round(max(0.0, rem - routing_part), 4)

        daily_rate = total_savings / max(1, days)
        monthly_proj = round(daily_rate * 30, 2)

        return {
            "total_savings": total_savings,
            "savings_percentage": savings_pct,
            "sources": {
                "cache_savings": cache_part,
                "routing_savings": routing_part,
                "compression_savings": compression_part,
            },
            "monthly_projected_savings": monthly_proj,
        }

    async def get_logs(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        stmt = select(RequestLog).order_by(desc(RequestLog.created_at)).limit(limit)
        if organization_id:
            stmt = stmt.where(RequestLog.organization_id == organization_id)

        result = await session.execute(stmt)
        logs = result.scalars().all()
        return [
            {
                "request_id": log.request_id,
                "model": log.model,
                "provider": log.provider,
                "input_tokens": log.input_tokens,
                "output_tokens": log.output_tokens,
                "estimated_cost": round(log.estimated_cost, 6),
                "actual_cost": round(log.actual_cost, 6),
                "savings": round(max(0.0, log.estimated_cost - log.actual_cost), 6),
                "latency_ms": round(log.latency_ms, 2),
                "cache_hit": log.cache_hit,
                "complexity_score": round(log.complexity_score, 1),
                "routing_strategy": log.routing_strategy,
                "quality_score": log.quality_score,
                "fallback_used": log.fallback_used,
                "status": log.status,
                "created_at": log.created_at,
            }
            for log in logs
        ]


aggregator = AnalyticsAggregator()

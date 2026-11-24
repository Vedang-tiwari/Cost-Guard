from datetime import UTC, datetime, timedelta
from typing import Any

from app.database.models.request_log import RequestLog
from sqlalchemy import select
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
                "cache_hit_rate": 0.0,
                "avg_latency_ms": 0.0,
                "p95_latency_ms": 0.0,
                "fallback_rate": 0.0,
            }

        total_spend = sum(log.actual_cost for log in logs)
        baseline_cost = sum(log.estimated_cost for log in logs)
        total_savings = max(0.0, baseline_cost - total_spend)
        savings_percentage = round((total_savings / baseline_cost * 100), 2) if baseline_cost > 0 else 0.0

        cache_hits = sum(1 for log in logs if log.cache_hit)
        cache_hit_rate = round((cache_hits / total_requests * 100), 2)

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
            "cache_hit_rate": cache_hit_rate,
            "avg_latency_ms": avg_latency,
            "p95_latency_ms": p95_latency,
            "fallback_rate": fallback_rate,
        }

    async def get_costs(
        self,
        session: AsyncSession,
        organization_id: str | None = None,
        days: int = 14,
    ) -> dict[str, Any]:
        since = datetime.now(UTC) - timedelta(days=days)
        base_stmt = select(RequestLog).where(RequestLog.created_at >= since)
        if organization_id:
            base_stmt = base_stmt.where(RequestLog.organization_id == organization_id)

        result = await session.execute(base_stmt)
        logs = list(result.scalars().all())

        by_day: dict[str, dict[str, Any]] = {}
        # Pre-seed last N days
        for i in range(days):
            d_str = (datetime.now(UTC) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            by_day[d_str] = {
                "date": d_str,
                "actual_cost": 0.0,
                "baseline_cost": 0.0,
                "savings": 0.0,
                "requests_count": 0,
            }

        for log in logs:
            day_str = log.created_at.strftime("%Y-%m-%d") if log.created_at else datetime.now(UTC).strftime("%Y-%m-%d")
            if day_str not in by_day:
                by_day[day_str] = {
                    "date": day_str,
                    "actual_cost": 0.0,
                    "baseline_cost": 0.0,
                    "savings": 0.0,
                    "requests_count": 0,
                }
            entry = by_day[day_str]
            entry["actual_cost"] += log.actual_cost
            entry["baseline_cost"] += log.estimated_cost
            entry["requests_count"] += 1

        points = []
        for k in sorted(by_day.keys()):
            e = by_day[k]
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
                }
            bm = by_model[key]
            bm["request_count"] += 1
            bm["input_tokens"] += log.input_tokens
            bm["output_tokens"] += log.output_tokens
            bm["total_cost"] += log.actual_cost
            bm["latencies"].append(log.latency_ms)

        models_list = []
        for data in by_model.values():
            req_count = data["request_count"]
            share_pct = round((req_count / total_reqs * 100), 2) if total_reqs > 0 else 0.0
            avg_lat = round(sum(data["latencies"]) / req_count, 2) if req_count > 0 else 0.0
            models_list.append({
                "model": data["model"],
                "provider": data["provider"],
                "request_count": req_count,
                "share_pct": share_pct,
                "input_tokens": data["input_tokens"],
                "output_tokens": data["output_tokens"],
                "total_cost": round(data["total_cost"], 6),
                "avg_latency_ms": avg_lat,
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

        # Approximate breakdown across levers
        cache_part = round(total_savings * (overview["cache_hit_rate"] / 100.0 if overview["cache_hit_rate"] > 0 else 0.3), 4)
        rem = max(0.0, total_savings - cache_part)
        routing_part = round(rem * 0.7, 4)
        compression_part = round(max(0.0, rem - routing_part), 4)

        # 30-day projection
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


aggregator = AnalyticsAggregator()

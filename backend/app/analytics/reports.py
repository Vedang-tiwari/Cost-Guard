from typing import Any

from app.analytics.aggregator import AnalyticsAggregator, aggregator


class ReportGenerator:
    """Generates structured analytics reports."""

    def __init__(self, agg: AnalyticsAggregator | None = None) -> None:
        self.aggregator = agg or aggregator

    def format_summary_markdown(self, stats: dict[str, Any]) -> str:
        return f"""# Cost Guard Analytics Summary

- **Total Requests Handled**: {stats.get('total_requests', 0)}
- **Actual LLM Spend**: ${stats.get('total_spend', 0.0):.4f}
- **Baseline Cost**: ${stats.get('baseline_cost', 0.0):.4f}
- **Net Cost Savings**: ${stats.get('total_savings', 0.0):.4f} (**{stats.get('savings_percentage', 0.0)}%**)
- **Cache Hit Rate**: {stats.get('cache_hit_rate', 0.0)}%
- **Average Latency**: {stats.get('avg_latency_ms', 0.0)} ms (P95: {stats.get('p95_latency_ms', 0.0)} ms)
- **Fallback Trigger Rate**: {stats.get('fallback_rate', 0.0)}%
"""


reports = ReportGenerator()

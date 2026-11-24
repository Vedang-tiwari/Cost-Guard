import logging

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

logger = logging.getLogger("costguard.core.metrics")

# 1. Request Counter
REQUESTS_TOTAL = Counter(
    "costguard_requests_total",
    "Total LLM completion requests processed through Cost Guard",
    ["provider", "model", "status", "cache_hit"],
)

# 2. Latency Histogram
REQUEST_DURATION_SECONDS = Histogram(
    "costguard_request_duration_seconds",
    "End-to-end request duration in seconds",
    ["provider", "model"],
    buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# 3. Cost Counters (Dollars)
COST_DOLLARS_TOTAL = Counter(
    "costguard_cost_dollars_total",
    "Total cost incurred and saved in USD",
    ["provider", "model", "type"],  # type: "actual", "baseline", "savings"
)

# 4. Token Counters
TOKENS_TOTAL = Counter(
    "costguard_tokens_total",
    "Total tokens processed by direction",
    ["provider", "model", "direction"],  # direction: "input", "output"
)

# 5. Cache Hits Counter
CACHE_HITS_TOTAL = Counter(
    "costguard_cache_hits_total",
    "Total requests served directly from the semantic cache",
)

# 6. Fallback Counter
FALLBACKS_TOTAL = Counter(
    "costguard_fallbacks_total",
    "Total automated fallback events triggered due to quality or provider failure",
    ["from_model", "to_model", "reason"],
)

# 7. Active Budgets Gauge
BUDGET_UTILIZATION_RATIO = Gauge(
    "costguard_budget_utilization_ratio",
    "Current budget utilization ratio (current_spend / limit_amount)",
    ["organization_id", "budget_id"],
)


def record_request_metrics(
    provider: str,
    model: str,
    status_code: str,
    cache_hit: bool,
    latency_ms: float,
    actual_cost: float,
    baseline_cost: float,
    input_tokens: int,
    output_tokens: int,
    fallback_used: bool = False,
    fallback_from: str | None = None,
) -> None:
    """Records real-time Prometheus operational metrics for a completed gateway request."""
    try:
        c_hit_str = "true" if cache_hit else "false"
        REQUESTS_TOTAL.labels(
            provider=provider,
            model=model,
            status=status_code,
            cache_hit=c_hit_str,
        ).inc()

        REQUEST_DURATION_SECONDS.labels(
            provider=provider,
            model=model,
        ).observe(latency_ms / 1000.0)

        COST_DOLLARS_TOTAL.labels(
            provider=provider,
            model=model,
            type="actual",
        ).inc(actual_cost)

        COST_DOLLARS_TOTAL.labels(
            provider=provider,
            model=model,
            type="baseline",
        ).inc(baseline_cost)

        savings = max(0.0, baseline_cost - actual_cost)
        if savings > 0:
            COST_DOLLARS_TOTAL.labels(
                provider=provider,
                model=model,
                type="savings",
            ).inc(savings)

        TOKENS_TOTAL.labels(
            provider=provider,
            model=model,
            direction="input",
        ).inc(input_tokens)

        TOKENS_TOTAL.labels(
            provider=provider,
            model=model,
            direction="output",
        ).inc(output_tokens)

        if cache_hit:
            CACHE_HITS_TOTAL.inc()

        if fallback_used and fallback_from:
            FALLBACKS_TOTAL.labels(
                from_model=fallback_from,
                to_model=model,
                reason="quality_threshold",
            ).inc()
    except Exception as e:
        logger.warning(f"Error recording Prometheus metrics: {e}")


def get_prometheus_metrics() -> tuple[bytes, str]:
    """Generates the latest Prometheus exposition metrics payload."""
    return generate_latest(), CONTENT_TYPE_LATEST

# Quality Evaluation, Cost Control & Observability

Cost Guard Phase 3 introduces automated quality gating, offline and online benchmarking, flexible budget controls with real-time alerting, full business analytics, and Prometheus observability metrics.

---

## 1. Quality Evaluation Engine

Cost Guard evaluates candidate model outputs to ensure that aggressive cost optimizations (such as down-tiering from `gpt-4o` to `gpt-4o-mini` or `gemini-1.5-flash`) preserve output quality according to defined thresholds.

### Evaluation Methods
- **Exact Match**: Strict or normalized case-insensitive equality check.
- **Semantic Similarity**: Cosine similarity computed over 256-dimensional dense embedding vectors (`app.cache.embeddings`).
- **JSON Schema Validity**: Parses JSON output, strips optional markdown code fences, and validates required keys against a JSON schema specification.
- **Task-Specific Rubrics**:
  - `classification`: Label presence, brevity bonus.
  - `code`: Delimiter balancing, syntax parsing via Python AST, code block formatting.
  - `math`: Equation presence, numerical extraction, final answer equivalence.
  - `reasoning`: Logical connective indicators ("therefore", "because", "step", "since").
  - `summarization`: Informative length ratio and content density.
  - `structured_output`: JSON schema validation and structure conformance.
- **LLM-as-a-Judge**: Evaluates outputs across 4 dimensions (correctness 1-5, adherence 1-5, completeness 1-5, formatting 1-5) using a judge LLM with automated fallback to a deterministic heuristic judge.

### Evaluation API
- `POST /api/v1/evaluations/run`: Evaluates candidate response on demand.
- `GET /api/v1/evaluations`: Retrieves paginated history of evaluation records.

---

## 2. Cascade Routing & Quality-Aware Fallback

When quality gating is enabled in the request:
```json
{
  "model": "auto",
  "messages": [{"role": "user", "content": "..."}],
  "quality": {
    "minimum_score": 0.85,
    "eval_enabled": true
  }
}
```
If the selected candidate model's response scores below `minimum_score`:
1. The gateway automatically triggers a fallback request to the next higher-tier model (e.g. `gpt-4o-mini` -> `gpt-4o`).
2. The response is re-evaluated.
3. The response header / telemetry records `fallback_used: true`.
4. Prometheus metrics counter `costguard_fallbacks_total` is incremented.

---

## 3. Cost Control & Budgets

Organizations and applications can set daily, weekly, or monthly budgets with warning and hard-limit thresholds.

### Enforcement
- **Warning Threshold** (default: 80%): Emits structured warning logs and sets budget status to `warning`.
- **Hard Limit** (default: true): If `current_spend + estimated_cost > limit_amount`, the gateway blocks the request with `HTTP 429 Too Many Requests` (`BudgetExceededError`).

### Budget API Endpoints
- `GET /api/v1/budgets`: List all budgets for the authenticated organization.
- `POST /api/v1/budgets`: Create a new budget cap.
- `GET /api/v1/budgets/{id}`: Retrieve budget details.
- `PATCH /api/v1/budgets/{id}`: Modify budget limit, warning threshold, or active status.

---

## 4. Analytics & Reporting

The analytics backend aggregates historical telemetry from `request_logs`:
- `GET /api/v1/analytics/overview`: High-level metrics (total requests, total spend, baseline cost, total savings, savings percentage, cache hit rate, average latency, P95 latency, fallback rate).
- `GET /api/v1/analytics/costs`: Time-series cost breakdown (daily/weekly/monthly).
- `GET /api/v1/analytics/models`: Distribution of model usage, request share, token counts, and costs.
- `GET /api/v1/analytics/savings`: Savings breakdown across semantic caching, intelligent down-tier routing, and prompt compression, plus 30-day projected savings.

---

## 5. Prometheus Observability

A dedicated exposition endpoint is available at `GET /metrics` exposing Prometheus standard metrics:
- `costguard_requests_total`: Counter by provider, model, status, and cache hit.
- `costguard_request_duration_seconds`: Histogram of latency across providers and models.
- `costguard_cost_dollars_total`: Counter tracking actual spend, baseline cost, and savings in USD.
- `costguard_tokens_total`: Counter tracking input and output tokens.
- `costguard_cache_hits_total`: Counter tracking cache hits.
- `costguard_fallbacks_total`: Counter tracking cascade fallbacks by origin model, destination model, and reason.
- `costguard_budget_utilization_ratio`: Gauge tracking current spend relative to budget limit.

---

## 6. Benchmark Suite

Cost Guard includes an automated benchmark suite (`scripts/run_benchmarks.py`) evaluated across 7 categories (classification, extraction, summarization, code, math, reasoning, structured output) comparing candidate models against baseline `gpt-4o`:

```bash
python scripts/run_benchmarks.py
```

Results are saved to `benchmarks/BENCHMARK_RESULTS.md`.

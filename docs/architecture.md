# Architecture Overview — Cost Guard

## 1. End-to-End Platform Architecture

```text
  [ React + Vite Dashboard ] ──► [ Nginx Reverse Proxy (:3000) ]
                                          │
                                          ▼  /api/* , /metrics , /health
  [ Client SDKs / cURL ] ──────► [ FastAPI Gateway (:8000) ]
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
   [ Auth & Scoped Keys ]        [ Optimization Pipeline ]       [ Management & Analytics ]
    • JWT Sessions (HS256)        • Task & Complexity Scorer      • Analytics Aggregator
    • PBKDF2 Passwords            • Token Estimator (tiktoken)    • Budget Manager & Alerts
    • SHA-256 App API Keys        • Semantic Vector Cache         • Quality Evaluator & LLM Judge
                                  • Prompt Optimizer              • Benchmark Suite
                                  • Intelligent Model Router      • Optimization Policies
                                  • Quality Gate & Cascade
                                          │
                                          ▼
                         [ Unified Provider Abstraction ]
                  (OpenAI • Anthropic • Google Gemini • Ollama)
                                          │
                                          ▼
              [ PostgreSQL 16 + pgvector ]  +  [ Redis ]  +  [ Prometheus / Grafana ]
```

---

## 2. Backend Layers (`backend/app/`)

- `api/routes/`: `auth.py`, `applications.py`, `chat.py`, `models.py`, `analytics.py`, `budgets.py`, `evaluations.py`, `policies.py`, `benchmarks.py`, `playground.py`, `health.py`.
- `api/dependencies.py`: Dual authentication dependency validating either `X-API-Key` (`cg_live_...`) or Dashboard `Authorization: Bearer <jwt>`.
- `gateway/optimization_pipeline.py`: 9-stage intelligent request pipeline orchestrating complexity scoring, token estimation, budget checks, semantic cache lookup/storage, prompt compression, model routing, quality gate cascade fallback, cost accounting, and Prometheus metric emission.
- `analyzer/`, `router/`, `optimization/`, `cache/`, `cost/`: Core optimization modules.
- `evaluation/`, `budgets/`, `analytics/`: Quality preservation engine, spending limit enforcement, and FinOps aggregation queries.
- `database/`: Async SQLAlchemy 2.0 models (`Organization`, `User`, `Application`, `ModelRegistry`, `RequestLog`, `CacheEntry`, `Budget`, `Evaluation`, `OptimizationPolicy`, `BenchmarkRun`) and Alembic migrations `001`–`004`.

## 3. Frontend Architecture (`frontend/src/`)

- `services/api.ts`: Typed HTTP API client managing Bearer JWT and API Key headers.
- `hooks/useAuth.tsx`: Session state provider supporting email/password auth, registration, and direct API key sign-in.
- `charts/`: Recharts data visualization components (`SpendTrendChart`, `ModelDistributionChart`, `BenchmarkBarChart`).
- `pages/`: Overview, API Playground, Cost Analytics, Models & Providers, Optimization Policy, Budgets & Alerts, Benchmarks, Applications & API Keys, Login, and Register.

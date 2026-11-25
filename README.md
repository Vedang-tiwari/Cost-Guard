# Cost Guard
### Intelligent LLM Cost Optimization & Quality Preservation Platform

Cost Guard is a full-stack intelligent LLM gateway and FinOps control plane designed to reduce Large Language Model operational expenditure across **OpenAI, Anthropic, Google Gemini, and Ollama** while preserving output quality through automated evaluation gates and cascade fallbacks.

---

## Key Capabilities

- **Unified LLM Gateway (`POST /api/v1/chat/completions`)**: Pluggable adapters (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `OllamaProvider`) with normalized request/response telemetry and error mapping.
- **Complexity Analyzer & Intelligent Routing**: 0–100 request complexity scoring, 7-category task classification, and cost-aware tier selection (`complexity_based`, `rule_based`, `explicit`).
- **Semantic Caching**: Tenant-isolated vector cache (`pgvector` / dense embeddings + cosine similarity threshold) eliminating duplicate LLM spend.
- **Prompt & Token Optimization**: Safe whitespace/filler compression with measurable input/output token accounting against the `gpt-4o` baseline.
- **Quality Preservation & Cascade Fallback**: Exact match, embedding similarity, JSON schema validation, task rubrics, and LLM-as-a-judge evaluation with automatic escalation on quality threshold failure.
- **Budgets & Spend Alerts**: Daily, weekly, and monthly caps with warning thresholds and automatic `HTTP 429` hard limits.
- **SaaS Analytics Dashboard & API Playground**: React + TypeScript + Tailwind UI with side-by-side comparison playground, Recharts analytics visualizations, model pricing registry, budget management, and benchmark runner.
- **Production Observability**: Prometheus `/metrics` endpoint, pre-provisioned Grafana dashboard, PostgreSQL 16 + Redis Docker Compose stack, and GitHub Actions CI.

---

## Documentation Index

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api.md)
- [Model Routing & Optimization](docs/routing.md)
- [Quality Evaluation, Budgets & Observability](docs/evaluation.md)
- [Docker & Production Deployment](docs/deployment.md)
- [Benchmark Comparison Results](benchmarks/BENCHMARK_RESULTS.md)

---

## Quickstart

### Option 1: Full Docker Compose Stack (Recommended)

```bash
cp .env.example .env
# Optionally set OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY in .env

# Start PostgreSQL, Redis, FastAPI Backend (with auto-migrations), and React Frontend
docker compose up -d --build

# Include Prometheus (:9090) & Grafana (:3001) monitoring stack:
docker compose --profile monitoring up -d --build
```

Access:
- **Web Dashboard**: `http://localhost:3000`
- **Gateway OpenAPI Docs**: `http://localhost:8000/docs`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

### Option 2: Local Development

**1. Backend**
```bash
# Create & activate Python 3.12 virtualenv, then install dependencies
pip install -r backend/requirements.txt

cd backend
alembic upgrade head
python ../scripts/seed_models.py
uvicorn app.main:app --reload --port 8000
```
Seeded demo credentials: `demo@costguard.ai` / `CostGuard2026!` (and API key `cg_test_1234567890abcdef`).

**2. Frontend Dashboard**
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173`.

---

## Benchmarks & Testing

Run the reproducible 14-prompt multi-category benchmark suite:
```bash
python scripts/run_benchmarks.py
```

Run automated linting, backend tests, and frontend verification:
```bash
# Backend
ruff check backend scripts
pytest backend/tests -v

# Frontend
cd frontend
npm run typecheck
npm run build
```

---

## Project Roadmap Status

- [x] **Phase 1**: Core Gateway & Multi-Provider Infrastructure
- [x] **Phase 2**: Intelligent Optimization Engine (Routing, Caching, Compression, Pricing)
- [x] **Phase 3**: Quality Evaluation, Fallback Cascade, Budgets, Analytics & Prometheus
- [x] **Phase 4**: React Dashboard, Auth, API Playground, Docker/Grafana Stack & CI Readiness

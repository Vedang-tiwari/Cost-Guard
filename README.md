# Cost Guard 🛡️
### Intelligent LLM Cost Optimization & Quality Preservation Platform

Cost Guard is an intelligent LLM gateway designed to dramatically reduce the operational expenses of applications consuming Large Language Model APIs (OpenAI, Anthropic, Google Gemini, Ollama) without compromising output quality beyond configurable thresholds.

---

## 🚀 Features (Phase 1 Implemented)

- **Unified LLM Gateway**: OpenAI-compatible chat completion endpoint (`/api/v1/chat/completions`) capable of interacting with OpenAI, Anthropic, Google Gemini, and Ollama.
- **Provider Abstraction Layer**: Pluggable adapters (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `OllamaProvider`) that normalize inputs, outputs, errors, and token usage metrics.
- **Application Authentication**: Secure API key authentication with SHA-256 hashed keys stored in PostgreSQL with organization isolation.
- **Model Registry & Pricing**: Centralized registry tracking model capabilities, pricing per million tokens (input & output), context windows, and active statuses.
- **Usage & Cost Tracking**: Detailed telemetry recording token consumption, latency, baseline cost, actual cost, and request status in PostgreSQL.
- **Containerized Infrastructure**: Production-ready `Dockerfile` and `docker-compose.yml` pre-configured with PostgreSQL and `pgvector`.
- **Health & Readiness Probes**: `/health` and `/ready` endpoints verifying service state, DB connectivity, and provider configurations.

---

## 🛠️ Tech Stack (Phase 1)

- **Runtime**: Python 3.12+
- **API Framework**: FastAPI, Uvicorn
- **ORM & Migrations**: SQLAlchemy 2.0 (asyncio + asyncpg), Alembic
- **Database**: PostgreSQL 16 + pgvector
- **Providers Supported**: OpenAI, Anthropic, Google Gemini, Ollama
- **Testing**: Pytest, Pytest-asyncio, Pytest-mock

---

## 📋 Quickstart

### 1. Environment Configuration

Copy the example environment configuration:
```bash
cp .env.example .env
```
Fill in your API keys (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`).

### 2. Run with Docker Compose

```bash
docker compose up -d
```

### 3. Local Development

```bash
# Activate virtual environment
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations
cd backend
alembic upgrade head

# Seed initial models and test application
python ../scripts/seed_models.py

# Start Gateway
uvicorn app.main:app --reload --port 8000
```

### 4. Send a Request

```bash
curl -X POST http://localhost:8000/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-API-Key: cg_live_your_api_key" \
  -d '{
    "model": "gpt-4o",
    "messages": [
      {"role": "user", "content": "Explain machine learning in simple terms."}
    ]
  }'
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest backend/tests -v
```

---

## 🗺️ Roadmap & Phase Status

- [x] **Phase 1: Core Gateway and Provider Infrastructure** (Completed)
- [x] **Phase 2: Intelligent Optimization Engine** (Completed)
  - Token Estimator (model-compatible estimation)
  - Task Classifier & Complexity Scoring (0-100 scale, Low/Medium/High tiers)
  - Intelligent Model Router (complexity-based, rule-based, explicit)
  - Semantic Caching (dense embeddings, cosine similarity, tenant isolation)
  - Prompt Optimizer (whitespace & filler reduction, token savings metrics)
  - Accurate Pricing Registry & Savings Calculator
  - End-to-End Optimization Pipeline
- [x] **Phase 3: Quality Evaluation and Cost Control** (Completed)
  - Quality Evaluation Engine (exact match, semantic similarity, JSON schema validity, task rubrics)
  - LLM-as-a-Judge & Heuristic Fallback Scoring
  - Quality-Aware Cascade Fallback Routing
  - Multi-tier Budgets & Alerts (daily/weekly/monthly, warning thresholds, hard-limit 429 enforcement)
  - Business & Technical Analytics Backend (`/api/v1/analytics/*`)
  - Prometheus Observability Exporter (`/metrics`)
  - Automated Benchmark Suite (`scripts/run_benchmarks.py` -> 92–96% cost savings with 97.5% quality retention)
- [ ] **Phase 4: Frontend Dashboard & Production Readiness** (Pending authorization: React/Vite UI, Playground, Analytics Dashboard)


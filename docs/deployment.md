# Cost Guard Deployment Guide

This guide covers containerized production deployment, observability setup, database migrations, and environment hardening for Cost Guard.

---

## 1. Environment Configuration

Copy `.env.example` to `.env` before deploying:

```bash
cp .env.example .env
```

Key security settings to customize for production:
- `SECRET_KEY`: High-entropy random string for signing JWT dashboard tokens.
- `POSTGRES_PASSWORD`: Strong database password.
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`: Upstream provider credentials (retained server-side only, never exposed to browsers).

---

## 2. Docker Compose Stack

Launch PostgreSQL (`pgvector/pgvector:pg16`), Redis (`redis:7-alpine`), FastAPI Gateway (`backend:8000`), and the React + Nginx Dashboard (`frontend:3000`):

```bash
docker compose up -d --build
```

The backend container automatically executes `alembic upgrade head` on startup before launching Uvicorn.

### Optional Initial Seed
Populate default models, demo organization, demo developer account, and sample API key:

```bash
docker compose exec backend python -c "import sys; sys.path.append('.'); ..."
# Or from local host against PostgreSQL:
python scripts/seed_models.py
```

---

## 3. Monitoring Stack (Prometheus & Grafana)

Launch the full observability profile alongside the core stack:

```bash
docker compose --profile monitoring up -d
```

Services started:
- **Prometheus** (`http://localhost:9090`): Scrapes `backend:8000/metrics` every 15s using `infrastructure/prometheus/prometheus.yml`.
- **Grafana** (`http://localhost:3001`): Pre-provisioned with Prometheus datasource and the `Cost Guard Gateway Observability` dashboard (`infrastructure/grafana/dashboards/costguard-overview.json`). Default login: `admin` / `admin`.

---

## 4. Health & Readiness Checks

- `GET /health`: Liveness probe for load balancers and Kubernetes probes.
- `GET /ready`: Validates PostgreSQL connectivity (`SELECT 1`) and provider adapter readiness.
- `GET /metrics`: Prometheus text exposition endpoint.

---

## 5. CI/CD Pipeline

`.github/workflows/ci.yml` executes automatically on every push and pull request to `main`:
1. **Backend Job**: Installs Python 3.12 dependencies, runs `ruff check backend scripts`, and executes `pytest backend/tests -v`.
2. **Frontend Job**: Installs Node.js 22 dependencies, verifies `npm run typecheck` (`tsc --noEmit`), and produces the production bundle with `npm run build`.

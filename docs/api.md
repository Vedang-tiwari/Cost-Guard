# Cost Guard API Documentation

## Base URL
- Direct Backend: `http://localhost:8000`
- Via Docker Nginx Proxy: `http://localhost:3000`
- Interactive OpenAPI Docs: `/docs`

---

## 1. Authentication & Applications

### `POST /api/v1/auth/register`
Provisions a new user, organization, default optimization policy, and initial API key.

### `POST /api/v1/auth/login`
Authenticates email/password credentials and issues an HS256 JWT Bearer token.

### `GET /api/v1/auth/me`
Returns authenticated user and organization details.

### `GET /api/v1/applications` | `POST /api/v1/applications` | `DELETE /api/v1/applications/{id}`
Manage scoped application API keys (`cg_live_...`). Raw keys are returned only at creation time and stored exclusively as SHA-256 hashes.

---

## 2. Chat Gateway & Playground

### `POST /api/v1/chat/completions`
Executes chat completions with optional optimization and quality gating. Accepts `X-API-Key: cg_...` or `Authorization: Bearer <token>`.

### `POST /api/v1/playground/compare`
Side-by-side comparison of fixed-model execution versus Cost Guard optimized execution in `"simulate"` (offline engine evaluation) or `"live"` (upstream provider) mode.

---

## 3. Models & Optimization Policies

- `GET /api/v1/models`: List active (or all) models in `models` registry.
- `GET /api/v1/models/{model_id}`: Fetch model details.
- `PATCH /api/v1/models/{model_id}`: Update token prices, pricing version, or active availability.
- `GET /api/v1/models/providers/status`: Inspect server provider key readiness (no secrets returned).
- `GET /api/v1/policies` & `PUT /api/v1/policies`: Read and update organization routing strategy, semantic cache threshold, prompt optimization, quality threshold, fallback behavior, and output token caps.

---

## 4. Analytics, Budgets, Evaluations & Benchmarks

- `GET /api/v1/analytics/overview?days=30`
- `GET /api/v1/analytics/costs?days=14&period=daily|weekly|monthly`
- `GET /api/v1/analytics/models?days=30`
- `GET /api/v1/analytics/savings?days=30`
- `GET /api/v1/analytics/logs?limit=50`
- `GET /api/v1/budgets` | `POST /api/v1/budgets` | `GET /api/v1/budgets/{id}` | `PATCH /api/v1/budgets/{id}`
- `POST /api/v1/evaluations/run` | `GET /api/v1/evaluations`
- `GET /api/v1/benchmarks/results` | `POST /api/v1/benchmarks/run`
- `GET /health` | `GET /ready` | `GET /metrics`

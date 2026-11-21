# COST GUARD
## Intelligent LLM Cost Optimization & Quality Preservation Platform

---

# 1. PROJECT OVERVIEW

## 1.1 Project Name

Cost Guard

## 1.2 Project Description

Cost Guard is an intelligent LLM cost optimization platform designed to reduce the operational expenses of applications that use Large Language Models without compromising their response quality beyond a configurable tolerance.

Modern AI applications rely on multiple LLM providers, including OpenAI, Anthropic, Google, and open-source model providers.

However, most applications send requests directly to expensive models regardless of the complexity of the task.

For example:

- A simple classification task might use GPT-4-class models when a smaller model is sufficient.
- A basic summarization request might consume expensive tokens unnecessarily.
- Repeated questions might trigger identical API calls.
- Large system prompts might be sent repeatedly.
- Applications might use expensive models for requests that require only simple reasoning.
- Developers often have no visibility into which features, users, or endpoints are responsible for their AI spending.

Cost Guard solves these problems through an intelligent optimization layer.

It acts as an intermediary between AI applications and LLM providers.

Instead of directly calling an LLM provider, applications send their requests to Cost Guard.

Cost Guard then:

1. Receives the LLM request.
2. Analyzes the request's complexity.
3. Estimates the expected token consumption and cost.
4. Checks whether an equivalent response exists in the semantic cache.
5. Determines the most suitable model.
6. Optimizes the prompt when appropriate.
7. Routes the request to the selected provider.
8. Evaluates response quality using configurable checks.
9. Records token consumption, latency, and cost.
10. Compares actual spending against the baseline.
11. Continuously improves routing decisions using evaluation data.

## 1.3 Core Objective

Build a production-oriented LLM optimization gateway that minimizes:

- Input token consumption.
- Output token consumption.
- Average cost per request.
- Unnecessary expensive model usage.
- Duplicate API calls.
- Overall AI infrastructure expenses.

While maintaining:

- Response accuracy.
- Semantic correctness.
- Instruction adherence.
- Output consistency.
- Acceptable latency.
- Application-specific quality requirements.

## 1.4 Target Users

- AI application developers.
- SaaS companies using LLM APIs.
- AI startups.
- Enterprise AI teams.
- RAG application developers.
- AI agent developers.
- Companies operating high-volume LLM workloads.

---

# 2. THE PROBLEM COST GUARD SOLVES

## 2.1 Existing Problem

Consider an application processing 100,000 LLM requests every month.

Assume the application uses an expensive model for almost every request.

However, the workload contains:

- 40% simple questions.
- 25% summarization tasks.
- 20% classification and extraction.
- 10% complex reasoning.
- 5% highly specialized tasks.

Using one expensive model for all these requests is inefficient.

Many requests could be handled by smaller, cheaper models.

Additionally, some requests may already have cached answers.

The application is therefore spending money on unnecessary computation.

## 2.2 Cost Guard Solution

Cost Guard introduces intelligent request optimization.

| Problem | Cost Guard Solution |
|---|---|
| Expensive model for simple tasks | Complexity-based routing |
| Repeated API requests | Semantic caching |
| Unnecessarily long prompts | Prompt optimization |
| Excessive output tokens | Output token controls |
| No cost visibility | Cost tracking and analytics |
| Inefficient model selection | Model benchmarking |
| Unexpected AI spending | Budget management |
| Quality degradation | Evaluation and quality gates |
| Provider-specific integrations | Unified LLM gateway |

---

# 3. CORE FEATURES

The following capabilities define the project.

## 3.1 Intelligent Model Routing

This is the central component of Cost Guard.

The router determines which model should process a request.

Instead of always selecting the most expensive model, Cost Guard evaluates the request and selects a suitable model based on:

- Request complexity.
- Task category.
- Context length.
- Expected output length.
- Required reasoning capability.
- Structured output requirements.
- Historical model performance.
- Quality thresholds.
- Model availability.
- Cost constraints.
- Latency requirements.

Example:

A user sends:

"Classify this customer review as positive, negative, or neutral."

Cost Guard identifies this as a low-complexity classification task.

It selects an inexpensive model instead of an unnecessarily expensive reasoning model.

Another request:

"Analyze this financial report, identify inconsistencies, and explain the potential business implications."

This request requires more reasoning.

Cost Guard selects a more capable model.

### Routing Strategies

Implement the following strategies:

**Strategy 1: Rule-Based Routing**

Use configurable rules.

Example:

- Classification → Small model.
- Simple summarization → Small or medium model.
- Complex reasoning → Large model.
- Structured extraction → Model with reliable structured output support.

**Strategy 2: Complexity-Based Routing**

Develop a request complexity analyzer.

Possible input signals:

- Prompt length.
- Number of instructions.
- Task type.
- Required reasoning depth.
- Context length.
- Output requirements.
- Structured output constraints.

Produce a complexity score between 0 and 100.

Example:

| Complexity | Score | Routing |
|---|---:|---|
| Low | 0–30 | Economical model |
| Medium | 31–65 | Balanced model |
| High | 66–100 | Premium model |

These thresholds must be configurable.

Important: complexity classification is a heuristic, not a guarantee of answer quality.

**Strategy 3: Quality-Aware Routing**

Use historical evaluation results to determine which models perform sufficiently well for each task category.

For example:

| Task | Model | Quality | Cost |
|---|---|---:|---:|
| Classification | Model A | 96% | Low |
| Classification | Model B | 97% | High |
| Reasoning | Model A | 72% | Low |
| Reasoning | Model B | 94% | High |

The router should select the least expensive model that satisfies the configured quality threshold.

Do not assume that a model is suitable merely because it is cheaper.

---

## 3.2 Semantic Caching

Repeated requests are a significant source of unnecessary LLM expenditure.

Cost Guard must implement semantic caching.

Traditional caching checks whether the request is exactly identical.

Semantic caching identifies requests with sufficiently similar meanings.

Example:

Request 1:
"What is machine learning?"

Request 2:
"Explain machine learning."

These requests may be semantically similar.

If the cached response is sufficiently relevant, Cost Guard can return it without calling an LLM.

### Implementation

Use:

- Embedding models.
- Vector database.
- Similarity search.
- Configurable similarity thresholds.
- Cache expiration.
- Cache invalidation.
- Namespace isolation.

Recommended technology:

- PostgreSQL.
- pgvector.
- sentence-transformers or a configurable embedding provider.

### Cache Workflow

1. Receive the incoming request.
2. Normalize the cacheable content.
3. Generate an embedding.
4. Search the cache.
5. Retrieve the closest matching entry.
6. Check the similarity threshold.
7. Validate cache compatibility.
8. Return the cached response if it is safe to reuse.
9. Otherwise continue normal routing.

### Cache Compatibility

Do not cache based on the user message alone.

The cache key and compatibility checks must consider:

- System prompt version.
- Model-independent task configuration.
- Conversation context.
- Output format.
- Temperature or generation settings.
- Tenant and application namespace.
- Relevant tool configuration.
- Data freshness requirements.

Do not reuse responses across tenants.

Do not cache sensitive or non-deterministic requests by default.

Provide explicit cache policies for:

- Public knowledge questions.
- Classification.
- Summarization.
- RAG responses.
- Personalized requests.
- Time-sensitive queries.

---

## 3.3 Prompt Optimization

Large prompts consume unnecessary input tokens.

Cost Guard should analyze prompts and identify opportunities to reduce token consumption.

Implement:

1. Redundant instruction detection.
2. Repeated context detection.
3. Unnecessary whitespace and formatting removal.
4. Duplicate content detection.
5. Context reduction.
6. Optional prompt compression.

### Important Rules

Prompt optimization must preserve:

- Original intent.
- Important instructions.
- Constraints.
- Required output format.
- Relevant context.
- Safety instructions.

Never silently remove important instructions.

The original prompt must be retained for auditing.

The optimized prompt must be stored separately.

Every optimization should be measurable.

Record:

- Original token count.
- Optimized token count.
- Tokens saved.
- Optimization method.
- Quality evaluation result.

Prompt optimization must be optional and configurable.

---

## 3.4 Token Optimization

Cost Guard should minimize unnecessary token usage.

Implement:

- Input token estimation.
- Output token limits.
- Context trimming.
- Duplicate context removal.
- Maximum completion token controls.
- Token budget enforcement.

Do not blindly truncate prompts.

Use intelligent context reduction that prioritizes relevant information.

When reducing output tokens, preserve the requested response structure and essential information.

Track estimated versus actual token consumption.

Actual provider usage should take precedence whenever available.

---

## 3.5 LLM Provider Abstraction

Cost Guard should support multiple LLM providers through a unified interface.

Initial provider support:

- OpenAI.
- Anthropic.
- Google Gemini.
- Ollama.

Provider integrations must be modular.

Recommended structure:

```text
providers/
├── base.py
├── openai_provider.py
├── anthropic_provider.py
├── gemini_provider.py
└── ollama_provider.py
```

Create a common provider interface.

Every provider should support the capabilities applicable to it:

- Chat completion.
- Streaming.
- Token usage reporting.
- Model identification.
- Timeout handling.
- Error handling.
- Retry support.
- Structured outputs where supported.

Do not assume every provider supports identical parameters.

Implement provider capability detection and parameter translation.

Never hardcode API keys.

Use environment variables.

---

## 3.6 Quality Preservation Engine

This is one of the most important components.

Reducing cost is meaningless if the application starts producing incorrect answers.

Cost Guard must measure the quality of cheaper model alternatives.

Implement configurable evaluation mechanisms.

### Evaluation Dimensions

1. Semantic similarity.
2. Factual correctness.
3. Instruction adherence.
4. Output format validity.
5. Task-specific accuracy.
6. Completeness.
7. Hallucination indicators where measurable.

### Evaluation Approaches

Use a combination of:

- Exact-match evaluation.
- Rule-based evaluation.
- JSON schema validation.
- Embedding similarity.
- Task-specific metrics.
- LLM-as-a-judge.
- Human-provided feedback.

Do not treat embedding similarity as proof of factual correctness.

LLM-as-a-judge must also be treated as an imperfect measurement.

### Quality Baseline

For every benchmark dataset:

1. Run requests through a reference model.
2. Save reference outputs.
3. Run the same requests through cheaper models.
4. Evaluate the outputs.
5. Compare quality scores.
6. Compare costs.
7. Identify acceptable alternatives.

### Quality Threshold

Example configuration:

```yaml
quality:
  enabled: true
  minimum_score: 0.90
  evaluation_mode: hybrid
  fallback_to_premium: true
```

The threshold is configurable and must be calibrated to the evaluation metric.

A score of 0.90 is not automatically equivalent to 90% factual accuracy.

### Fallback Mechanism

If a cheaper model fails validation:

1. Identify the failure.
2. Record the evaluation result.
3. Retry using an appropriate higher-capability model when permitted.
4. Return the validated response.
5. Record the additional cost.

Do not automatically retry indefinitely.

Implement retry limits and fallback policies.

For production requests, avoid sending every response to an expensive judge model. Use configurable sampling, deterministic checks, and offline evaluations to control evaluation expenditure.

---

## 3.7 Cost Tracking and Analytics

Every request must generate an observability record.

Track:

- Request ID.
- Application ID.
- Tenant ID.
- Selected provider.
- Selected model.
- Input tokens.
- Output tokens.
- Total tokens.
- Estimated cost.
- Actual cost where available.
- Latency.
- Cache hit or miss.
- Routing strategy.
- Complexity score.
- Quality evaluation score.
- Fallback usage.
- Timestamp.
- Error status.

### Cost Calculation

For a model:

```text
Total Cost =
(Input Tokens / 1,000,000 × Input Price Per Million)
+
(Output Tokens / 1,000,000 × Output Price Per Million)
```

Maintain a model pricing registry.

Pricing must be configurable and versioned.

Do not hardcode pricing throughout the application.

Support different pricing rules when applicable, including:

- Input tokens.
- Output tokens.
- Cached input tokens.
- Provider-specific billing.
- Batch pricing.

Distinguish estimated cost from provider-reported or billed cost.

---

## 3.8 Budget Management

Users should be able to configure spending limits.

Examples:

- Daily budget.
- Weekly budget.
- Monthly budget.
- Per-application budget.
- Per-tenant budget.
- Per-model budget.

Implement configurable thresholds.

Example:

```yaml
budget:
  monthly_limit: 100
  warning_threshold: 0.75
  critical_threshold: 0.90
  hard_limit: true
```

When a budget threshold is reached:

- Generate an alert.
- Record the event.
- Apply the configured policy.
- Optionally restrict expensive models.
- Optionally reject new requests after the hard limit.

Never silently switch to a model that violates the application's minimum quality requirements.

---

# 4. SYSTEM ARCHITECTURE

Cost Guard follows a modular gateway architecture.

## 4.1 High-Level Architecture

```text
             CLIENT APPLICATION
                     |
                     |
              API REQUEST
                     |
                     v
             COST GUARD GATEWAY
                     |
                     v
              AUTHENTICATION
                     |
                     v
             REQUEST VALIDATION
                     |
                     v
              REQUEST ANALYZER
                     |
             +-------+-------+
             |               |
             v               v
       TOKEN ESTIMATOR   COMPLEXITY
                         ANALYZER
             |               |
             +-------+-------+
                     |
                     v
              SEMANTIC CACHE
                     |
              +------+------+
              |             |
           CACHE HIT      CACHE MISS
              |             |
              v             v
        RETURN RESPONSE  PROMPT OPTIMIZER
                            |
                            v
                      MODEL ROUTER
                            |
                            v
                    BUDGET VALIDATOR
                            |
                            v
                    PROVIDER ADAPTER
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
           OPENAI        ANTHROPIC      GEMINI
              |             |             |
              +-------------+-------------+
                            |
                            v
                       LLM RESPONSE
                            |
                            v
                    RESPONSE VALIDATOR
                            |
                            v
                    QUALITY EVALUATOR
                            |
                    +-------+-------+
                    |               |
                 PASSED           FAILED
                    |               |
                    |               v
                    |        FALLBACK ROUTER
                    |               |
                    |               v
                    |        PREMIUM MODEL
                    |               |
                    +-------+-------+
                            |
                            v
                    RESPONSE DELIVERY
                            |
                 +----------+----------+
                 |          |          |
                 v          v          v
              COST       METRICS    LOGGING
             TRACKER     ENGINE     ENGINE
                 |          |          |
                 +----------+----------+
                            |
                            v
                     POSTGRESQL
                            |
                            v
                    ANALYTICS API
                            |
                            v
                     WEB DASHBOARD
```

---

# 5. TECHNOLOGY STACK

Use the following stack unless a technical limitation requires a documented alternative.

## 5.1 Backend

| Technology | Purpose |
|---|---|
| Python 3.12+ | Primary language |
| FastAPI | API gateway |
| Pydantic | Validation and configuration |
| SQLAlchemy 2.x | ORM |
| Alembic | Database migrations |
| Uvicorn | ASGI server |
| httpx | Async HTTP communication |

## 5.2 AI / LLM

| Technology | Purpose |
|---|---|
| OpenAI SDK | OpenAI integration |
| Anthropic SDK | Anthropic integration |
| Google GenAI SDK | Gemini integration |
| Ollama API | Local model integration |
| LiteLLM tokenizers/utilities where useful | Model compatibility utilities |
| tiktoken | Token estimation for supported models |
| sentence-transformers | Embeddings |
| Hugging Face | Model and embedding ecosystem |

Avoid introducing multiple orchestration frameworks without a concrete requirement.

Implement the routing logic yourself rather than making the entire product dependent on an existing LLM routing platform.

## 5.3 Database and Caching

| Technology | Purpose |
|---|---|
| PostgreSQL | Primary database |
| pgvector | Semantic caching |
| Redis | Fast caching and distributed state |
| SQLAlchemy | Database operations |

PostgreSQL should be the source of truth.

Redis should be used for temporary and high-speed operations.

## 5.4 Background Processing

| Technology | Purpose |
|---|---|
| Celery | Background jobs |
| Redis | Celery broker |
| Celery Beat | Scheduled tasks |

Use background workers for:

- Evaluation jobs.
- Cost aggregation.
- Analytics processing.
- Cache maintenance.
- Scheduled budget checks.
- Benchmark execution.

Do not introduce Celery for simple synchronous operations.

## 5.5 Frontend

| Technology | Purpose |
|---|---|
| React | Frontend |
| TypeScript | Type safety |
| Vite | Build tooling |
| Tailwind CSS | Styling |
| Recharts | Analytics visualizations |
| TanStack Query | API state management |

## 5.6 Observability

| Technology | Purpose |
|---|---|
| OpenTelemetry | Distributed tracing |
| Prometheus | Metrics |
| Grafana | Monitoring dashboards |
| Python logging | Application logs |

Track:

- Request latency.
- Provider latency.
- Token consumption.
- Cost per request.
- Cache hit rate.
- Routing distribution.
- Fallback rate.
- Error rate.
- Quality score.

## 5.7 DevOps

| Technology | Purpose |
|---|---|
| Docker | Containerization |
| Docker Compose | Local development |
| GitHub Actions | CI/CD |
| Pytest | Backend testing |
| Ruff | Linting and formatting |
| MyPy | Static type checking |

---

# 6. PROJECT DIRECTORY STRUCTURE

Create a clean, modular, production-oriented structure.

```text
cost-guard/
│
├── backend/
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── chat.py
│   │   │   │   ├── models.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── budgets.py
│   │   │   │   ├── evaluations.py
│   │   │   │   └── applications.py
│   │   │   │
│   │   │   └── dependencies.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── logging.py
│   │   │   └── exceptions.py
│   │   │
│   │   ├── gateway/
│   │   │   ├── request_handler.py
│   │   │   ├── request_validator.py
│   │   │   └── response_handler.py
│   │   │
│   │   ├── analyzer/
│   │   │   ├── complexity.py
│   │   │   ├── task_classifier.py
│   │   │   └── token_estimator.py
│   │   │
│   │   ├── router/
│   │   │   ├── model_router.py
│   │   │   ├── routing_rules.py
│   │   │   ├── model_registry.py
│   │   │   └── fallback.py
│   │   │
│   │   ├── providers/
│   │   │   ├── base.py
│   │   │   ├── openai_provider.py
│   │   │   ├── anthropic_provider.py
│   │   │   ├── gemini_provider.py
│   │   │   └── ollama_provider.py
│   │   │
│   │   ├── optimization/
│   │   │   ├── prompt_optimizer.py
│   │   │   ├── context_reducer.py
│   │   │   └── token_optimizer.py
│   │   │
│   │   ├── cache/
│   │   │   ├── semantic_cache.py
│   │   │   ├── cache_keys.py
│   │   │   └── cache_policy.py
│   │   │
│   │   ├── evaluation/
│   │   │   ├── evaluator.py
│   │   │   ├── quality_metrics.py
│   │   │   ├── llm_judge.py
│   │   │   └── benchmark.py
│   │   │
│   │   ├── cost/
│   │   │   ├── calculator.py
│   │   │   ├── pricing_registry.py
│   │   │   └── usage_tracker.py
│   │   │
│   │   ├── budgets/
│   │   │   ├── budget_manager.py
│   │   │   └── alerts.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── aggregator.py
│   │   │   └── reports.py
│   │   │
│   │   ├── database/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   │   └── models/
│   │   │
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   │
│   │   └── schemas/
│   │       ├── request.py
│   │       ├── response.py
│   │       └── analytics.py
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── evaluation/
│   │   └── load/
│   │
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── layouts/
│   │   ├── charts/
│   │   └── types/
│   ├── package.json
│   └── Dockerfile
│
├── benchmarks/
│   ├── datasets/
│   ├── results/
│   └── configs/
│
├── infrastructure/
│   ├── prometheus/
│   ├── grafana/
│   └── docker/
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── routing.md
│   └── evaluation.md
│
├── scripts/
│   ├── seed_models.py
│   └── run_benchmarks.py
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
└── instruction.md
```

Do not create every file as an empty placeholder.

Create files when their implementation becomes necessary.

---

# 7. DATABASE DESIGN

Use PostgreSQL as the primary database.

Design the schema to support multiple applications and tenants.

## 7.1 Users

```text
users
-----
id
email
password_hash
created_at
updated_at
```

## 7.2 Organizations

```text
organizations
-------------
id
name
created_at
```

## 7.3 Applications

```text
applications
------------
id
organization_id
name
api_key_hash
status
created_at
```

## 7.4 Model Registry

```text
models
------
id
provider
model_name
input_price_per_million
output_price_per_million
capabilities
context_window
is_active
pricing_version
created_at
updated_at
```

## 7.5 Request Logs

```text
request_logs
------------
id
request_id
application_id
organization_id
provider
model
input_tokens
output_tokens
estimated_cost
actual_cost
latency_ms
cache_hit
complexity_score
routing_strategy
quality_score
fallback_used
status
created_at
```

## 7.6 Cache Entries

```text
cache_entries
-------------
id
application_id
organization_id
cache_key
embedding
response
model
prompt_version
metadata
expires_at
created_at
```

## 7.7 Budgets

```text
budgets
-------
id
organization_id
application_id
budget_type
limit_amount
warning_threshold
hard_limit
period
created_at
updated_at
```

## 7.8 Evaluations

```text
evaluations
-----------
id
request_id
reference_model
candidate_model
quality_score
evaluation_method
passed
evaluation_metadata
created_at
```

Add appropriate indexes, foreign keys, constraints, and tenant-isolation rules.

Use migrations rather than modifying database tables manually.

---

# 8. API DESIGN

Build a unified API gateway.

The goal is to make Cost Guard easy to integrate into existing AI applications.

## 8.1 Main Chat Endpoint

```http
POST /api/v1/chat/completions
```

Example request:

```json
{
  "model": "auto",
  "messages": [
    {
      "role": "user",
      "content": "Explain what machine learning is."
    }
  ],
  "optimization": {
    "enabled": true,
    "semantic_cache": true,
    "prompt_optimization": true,
    "intelligent_routing": true
  },
  "quality": {
    "minimum_score": 0.90
  },
  "max_tokens": 500
}
```

The `auto` model setting enables intelligent routing.

An explicitly requested model must be respected unless the application has explicitly enabled model substitution.

## 8.2 Response

```json
{
  "request_id": "req_123456",
  "model": "selected-model",
  "provider": "selected-provider",
  "response": {
    "role": "assistant",
    "content": "Machine learning is..."
  },
  "usage": {
    "input_tokens": 120,
    "output_tokens": 85,
    "total_tokens": 205
  },
  "cost": {
    "estimated_cost": 0.00012,
    "baseline_cost": 0.00045,
    "savings": 0.00033,
    "savings_percentage": 73.33
  },
  "optimization": {
    "cache_hit": false,
    "routing_strategy": "complexity_based",
    "complexity_score": 18,
    "prompt_optimized": true,
    "fallback_used": false
  }
}
```

These values are illustrative.

Calculate savings against a defined baseline rather than inventing or assuming baseline expenditure.

## 8.3 Additional Endpoints

```http
GET    /api/v1/models
GET    /api/v1/models/{model_id}

GET    /api/v1/analytics/overview
GET    /api/v1/analytics/costs
GET    /api/v1/analytics/models
GET    /api/v1/analytics/savings

GET    /api/v1/budgets
POST   /api/v1/budgets
PATCH  /api/v1/budgets/{budget_id}

GET    /api/v1/evaluations
POST   /api/v1/evaluations/run

GET    /api/v1/applications
POST   /api/v1/applications
DELETE /api/v1/applications/{application_id}

GET    /health
GET    /ready
```

Provide OpenAPI documentation through FastAPI.

Implement authentication, application-level API keys, authorization, rate limiting, and request validation.

---

# 9. MODEL ROUTING ALGORITHM

Implement routing as an independent service.

The router should not directly communicate with providers.

Its responsibility is to select a model and return a routing decision.

## 9.1 Routing Inputs

```python
class RoutingInput:
    task_type: str
    complexity_score: float
    estimated_input_tokens: int
    expected_output_tokens: int
    quality_requirement: float
    latency_requirement: int | None
    budget_remaining: float | None
```

## 9.2 Model Candidate Selection

Filter available models using:

1. Provider availability.
2. Supported task capabilities.
3. Context window.
4. Required output format.
5. Quality eligibility.
6. Budget restrictions.
7. Latency constraints.

## 9.3 Cost Estimation

Estimate the cost of every eligible model.

```text
estimated_cost =
(input_tokens × input_price)
+
(output_tokens × output_price)
```

Use the correct price units.

## 9.4 Selection

Select the lowest-cost model that satisfies all mandatory constraints.

If no model meets the quality requirement:

- Select the configured safe fallback.
- Or reject the request with an explanatory error.

Never silently lower the required quality threshold.

## 9.5 Routing Decision

Return:

```json
{
  "selected_model": "model-name",
  "provider": "provider-name",
  "estimated_cost": 0.001,
  "complexity_score": 45,
  "reason": "Lowest-cost eligible model",
  "fallback_required": false
}
```

Every routing decision must be explainable and logged.

---

# 10. COST SAVINGS MEASUREMENT

Cost Guard must prove that it actually reduces expenditure.

Do not rely on arbitrary savings percentages.

## 10.1 Baseline

Establish a baseline by sending the same benchmark workload to a designated reference model.

Record:

- Baseline input tokens.
- Baseline output tokens.
- Baseline cost.
- Baseline latency.
- Baseline quality.

## 10.2 Optimized Execution

Run the same workload through Cost Guard.

Record:

- Selected models.
- Optimized token counts.
- Cache hits.
- Actual cost.
- Latency.
- Quality.

## 10.3 Savings Calculation

```text
Savings = Baseline Cost - Optimized Cost
```

```text
Savings Percentage =
(Savings / Baseline Cost) × 100
```

## 10.4 Quality Difference

```text
Quality Difference =
Baseline Quality - Optimized Quality
```

Report this separately.

A system that saves 60% but significantly reduces quality must not be presented as a successful optimization.

## 10.5 Required Benchmark Results

Generate a comparison table:

| Metric | Baseline | Cost Guard |
|---|---|---|
| Total requests | N | N |
| Total cost | Actual | Actual |
| Average cost/request | Actual | Actual |
| Input tokens | Actual | Actual |
| Output tokens | Actual | Actual |
| Average latency | Actual | Actual |
| Cache hit rate | N/A | Actual |
| Quality score | Actual | Actual |
| Fallback rate | N/A | Actual |

Also report:

- Cost savings.
- Quality difference.
- Cost per successful request.
- P50 latency.
- P95 latency.
- Error rate.

Use identical benchmark inputs and clearly document any differences in execution conditions.

---

# 11. FRONTEND DASHBOARD

Build a professional SaaS-style analytics dashboard.

The dashboard should help developers understand where their AI expenditure goes.

## 11.1 Overview Page

Display:

- Total AI spending.
- Estimated savings.
- Total requests.
- Average cost per request.
- Cache hit rate.
- Average quality score.
- Model distribution.
- Daily expenditure.

## 11.2 Cost Analytics

Display:

- Daily spending.
- Weekly spending.
- Monthly spending.
- Cost per application.
- Cost per model.
- Cost per provider.
- Input versus output token expenditure.

## 11.3 Model Analytics

Display:

- Available models.
- Provider.
- Cost per million tokens.
- Average latency.
- Evaluation score.
- Request volume.
- Selection frequency.

## 11.4 Optimization Analytics

Display:

- Requests routed to cheaper models.
- Semantic cache savings.
- Prompt optimization savings.
- Token reduction.
- Fallback frequency.
- Quality failures.

## 11.5 Budget Management

Users should be able to:

- Create budgets.
- Update budgets.
- View budget utilization.
- Configure warning thresholds.
- Configure hard spending limits.

## 11.6 API Playground

Build an interface where developers can:

1. Enter a prompt.
2. Select automatic or fixed model routing.
3. Enable optimization features.
4. Submit the request.
5. View the generated response.
6. Inspect the selected model.
7. Compare estimated costs.
8. View token usage.
9. Inspect routing decisions.

The playground is essential for demonstrating the platform's actual behavior.

---

# 12. SECURITY AND RELIABILITY

Security must be implemented as part of the architecture.

Requirements:

- Never expose provider API keys to the frontend.
- Store secrets in environment variables or a secure secret manager.
- Hash application API keys.
- Implement tenant isolation.
- Validate all incoming requests.
- Implement rate limiting.
- Add request timeouts.
- Implement bounded retries.
- Prevent duplicate processing where appropriate.
- Sanitize logs.
- Avoid storing sensitive prompts by default.
- Support configurable data retention.
- Protect against cache cross-tenant leakage.
- Validate provider responses.
- Implement structured error handling.

Do not log raw API keys, credentials, or sensitive user data.

Implement request IDs for traceability.

---

# 13. ERROR HANDLING

Handle at least the following cases:

| Error | Expected Behavior |
|---|---|
| Provider unavailable | Try eligible fallback |
| Invalid API key | Return authentication error |
| Rate limit exceeded | Apply bounded retry/backoff |
| Context limit exceeded | Return clear error or safe context reduction |
| Budget exhausted | Apply configured budget policy |
| Model unavailable | Select another eligible model |
| Cache unavailable | Continue without cache |
| Database unavailable | Fail safely for operations requiring persistence |
| Evaluation failure | Apply configured quality policy |
| Invalid response format | Validate and handle failure |

Do not allow cache, analytics, or evaluation failures to silently corrupt request accounting.

Use idempotency where retries could otherwise duplicate billable requests.

---

# 14. TESTING REQUIREMENTS

Testing is mandatory.

## 14.1 Unit Tests

Test:

- Token estimation.
- Complexity scoring.
- Task classification.
- Model routing.
- Pricing calculation.
- Cache key generation.
- Semantic similarity thresholds.
- Budget validation.
- Quality evaluation.
- Fallback logic.

## 14.2 Integration Tests

Test:

- API gateway.
- Provider adapters.
- Database persistence.
- Redis integration.
- Semantic cache.
- Routing pipeline.
- Analytics aggregation.

Use mocked providers for deterministic tests.

## 14.3 Evaluation Tests

Create a benchmark dataset containing:

- Simple questions.
- Classification tasks.
- Summarization tasks.
- Extraction tasks.
- Complex reasoning.
- Structured output tasks.
- Long-context requests.

Compare multiple models against a reference.

## 14.4 Load Tests

Test:

- Concurrent requests.
- High request volumes.
- Provider latency.
- Cache performance.
- Database throughput.
- Failure recovery.

Use Locust or an equivalent load-testing tool.

## 14.5 Acceptance Criteria

The project should demonstrate:

1. Multiple provider integrations.
2. Working intelligent routing.
3. Working semantic caching.
4. Measurable cost reduction.
5. Quality comparison against a baseline.
6. Token usage tracking.
7. Budget enforcement.
8. Functional analytics dashboard.
9. Automated tests.
10. Docker-based deployment.

Do not claim a specific percentage of cost savings until benchmark results demonstrate it.

---

# 15. IMPLEMENTATION ROADMAP

CRITICAL IMPLEMENTATION RULE:

Implement this project in exactly four phases.

The coding agent must never implement multiple phases automatically.

Only implement a phase when the user explicitly authorizes it.

After completing each phase:

1. Run relevant tests.
2. Fix implementation errors.
3. Update documentation.
4. Summarize completed work.
5. List remaining work.
6. Stop execution.

Do not start the next phase without explicit authorization.

---

# PHASE 1 — CORE GATEWAY AND PROVIDER INFRASTRUCTURE

## Objective

Build the foundational Cost Guard gateway and establish reliable communication with multiple LLM providers.

## Tasks

### 1. Project Initialization

- Create backend directory structure.
- Configure Python environment.
- Install dependencies.
- Configure FastAPI.
- Configure Pydantic settings.
- Create environment configuration.
- Configure structured logging.
- Create Dockerfile.

### 2. Database Infrastructure

- Configure PostgreSQL.
- Configure SQLAlchemy.
- Configure Alembic.
- Create initial database models.
- Implement database sessions.
- Create migrations.

### 3. Provider Abstraction

Implement:

- Base provider interface.
- OpenAI adapter.
- Anthropic adapter.
- Gemini adapter.
- Ollama adapter.

Implement consistent provider responses and error handling.

### 4. Gateway API

Implement:

```http
POST /api/v1/chat/completions
GET /api/v1/models
GET /health
GET /ready
```

Initially support explicit model selection.

### 5. Usage Tracking

Record:

- Provider.
- Model.
- Input tokens.
- Output tokens.
- Latency.
- Request status.
- Timestamp.

### 6. Authentication

Implement application API keys.

Store only hashed keys.

### 7. Testing

Create unit and integration tests.

Test provider adapters with mocks.

Verify database persistence.

## Phase 1 Completion Criteria

- FastAPI application runs.
- PostgreSQL integration works.
- Multiple providers can be accessed.
- Unified request format works.
- Provider errors are handled.
- Usage records are persisted.
- Authentication works.
- Docker environment starts successfully.
- Tests pass.

STOP AFTER PHASE 1.

Do not implement semantic caching, intelligent routing, prompt optimization, or the frontend dashboard yet.

---

# PHASE 2 — INTELLIGENT OPTIMIZATION ENGINE

## Objective

Implement the main Cost Guard intelligence.

This phase transforms the gateway into an actual cost optimization platform.

## Tasks

### 1. Token Estimator

- Integrate model-compatible token estimation.
- Estimate input token consumption.
- Estimate output token consumption.
- Record estimated versus actual usage.

### 2. Complexity Analyzer

Implement:

- Task classification.
- Complexity scoring.
- Configurable complexity thresholds.

### 3. Model Registry

Implement:

- Model capabilities.
- Model pricing.
- Model context limits.
- Model availability.
- Model quality metadata.

### 4. Intelligent Router

Implement:

- Rule-based routing.
- Complexity-based routing.
- Quality-aware candidate filtering.
- Cost-based selection.
- Model fallback.

### 5. Semantic Cache

Integrate:

- pgvector.
- Embedding generation.
- Similarity search.
- Cache expiration.
- Cache policies.
- Tenant isolation.

### 6. Prompt Optimization

Implement:

- Prompt analysis.
- Redundancy detection.
- Safe prompt compression.
- Token reduction measurement.

### 7. Cost Calculator

Implement:

- Model-specific pricing.
- Input cost.
- Output cost.
- Cached input cost where applicable.
- Estimated and actual expenditure.

### 8. Optimization Pipeline

Integrate all components:

```text
Incoming Request
       |
       v
Request Analysis
       |
       v
Token Estimation
       |
       v
Semantic Cache
       |
       v
Prompt Optimization
       |
       v
Model Routing
       |
       v
Cost Calculation
       |
       v
Provider Execution
       |
       v
Usage Tracking
```

### 9. Testing

Test routing decisions against known scenarios.

Test semantic cache behavior.

Test cost calculation.

Test optimization effectiveness.

## Phase 2 Completion Criteria

- Automatic model routing works.
- Multiple routing strategies work.
- Semantic cache works.
- Prompt optimization works.
- Token usage is measured.
- Cost calculations are accurate for configured pricing.
- Optimization decisions are logged.
- Existing Phase 1 functionality remains operational.

STOP AFTER PHASE 2.

Do not implement the quality evaluation engine, advanced analytics, or frontend dashboard yet.

---

# PHASE 3 — QUALITY EVALUATION AND COST CONTROL

## Objective

Ensure that cost optimization does not create unacceptable response-quality degradation.

This phase establishes measurable quality assurance.

## Tasks

### 1. Evaluation Engine

Implement:

- Exact-match evaluation.
- Semantic similarity evaluation.
- Structured output validation.
- Task-specific evaluation.
- LLM-as-a-judge integration.

### 2. Benchmark Framework

Create benchmark datasets.

Support:

- Reference model execution.
- Candidate model execution.
- Automated evaluation.
- Result storage.
- Model comparisons.

### 3. Quality-Aware Routing

Implement:

- Historical quality tracking.
- Model eligibility based on quality thresholds.
- Task-specific model performance.
- Configurable quality requirements.

### 4. Fallback Engine

Implement:

- Quality failure detection.
- Fallback model selection.
- Retry limits.
- Fallback tracking.
- Final response validation.

### 5. Budget Management

Implement:

- Daily budgets.
- Weekly budgets.
- Monthly budgets.
- Application-level budgets.
- Warning thresholds.
- Hard spending limits.

### 6. Analytics Backend

Implement APIs for:

- Total expenditure.
- Cost savings.
- Model usage.
- Provider usage.
- Token consumption.
- Cache performance.
- Quality metrics.
- Fallback statistics.

### 7. Observability

Integrate:

- OpenTelemetry.
- Prometheus.
- Structured logs.
- Request tracing.
- Latency metrics.

### 8. Testing

Verify:

- Quality thresholds.
- Model fallback.
- Budget enforcement.
- Benchmark reproducibility.
- Cost savings calculation.
- Failure handling.

## Phase 3 Completion Criteria

- Quality evaluation works.
- Baseline comparisons work.
- Model quality measurements are stored.
- Quality-aware routing works.
- Fallback works.
- Budget enforcement works.
- Analytics APIs return accurate data.
- Observability metrics are available.

STOP AFTER PHASE 3.

Do not automatically start the frontend implementation.

---

# PHASE 4 — FRONTEND, INTEGRATION AND PRODUCTION READINESS

## Objective

Build the complete user-facing Cost Guard platform and prepare the application for deployment.

## Tasks

### 1. Frontend Initialization

- Configure React.
- Configure TypeScript.
- Configure Tailwind CSS.
- Configure routing.
- Configure API integration.
- Create reusable components.

### 2. Authentication Interface

Implement:

- Login.
- Registration.
- Application management.
- API key management.

### 3. Analytics Dashboard

Build:

- Cost overview.
- Savings overview.
- Token analytics.
- Model analytics.
- Provider analytics.
- Cache analytics.
- Quality metrics.

### 4. Model Management

Build:

- Model registry interface.
- Provider configuration.
- Pricing management.
- Model capability information.

Never expose provider secrets in the browser.

### 5. Optimization Configuration

Allow users to configure:

- Intelligent routing.
- Semantic caching.
- Prompt optimization.
- Quality thresholds.
- Fallback behavior.
- Token limits.
- Budget policies.

### 6. API Playground

Implement an interactive playground.

Users should be able to compare:

- Fixed-model execution.
- Automatic routing.
- Cost differences.
- Token differences.
- Response quality.
- Latency.

### 7. Budget Dashboard

Display:

- Current spending.
- Budget limits.
- Remaining budget.
- Warning indicators.
- Spending history.

### 8. Benchmark Dashboard

Display actual benchmark results.

Compare:

- Baseline versus optimized cost.
- Baseline versus optimized quality.
- Model performance.
- Latency.
- Cache hit rates.

### 9. Production Readiness

Implement:

- Docker Compose.
- Production configuration.
- CI pipeline.
- Automated testing.
- Database migrations.
- Health checks.
- Logging.
- Monitoring.
- Deployment documentation.

### 10. Documentation

Complete:

- README.md.
- Architecture documentation.
- API documentation.
- Setup instructions.
- Environment configuration.
- Benchmark instructions.
- Deployment instructions.

## Phase 4 Completion Criteria

- Frontend works.
- Backend and frontend are integrated.
- Analytics are functional.
- API playground works.
- Budget interface works.
- Benchmark comparisons work.
- Docker deployment works.
- CI tests pass.
- Documentation is complete.

STOP AFTER PHASE 4.

The project is now ready for final review and deployment.

---

# 16. DEVELOPMENT RULES FOR THE CODING AGENT

These instructions are mandatory.

## Rule 1: Strict Phase Execution

Never implement the entire project at once.

Only execute the phase explicitly requested by the user.

If the user says:

"Implement Phase 1"

Only implement Phase 1.

Do not begin Phase 2 automatically.

## Rule 2: No Unnecessary Code

Do not generate unnecessary abstractions.

Do not create empty placeholder modules.

Do not introduce libraries without a technical reason.

Prefer simple, maintainable implementations.

## Rule 3: Production-Oriented Code

Follow:

- SOLID principles where appropriate.
- Separation of concerns.
- Dependency injection.
- Type hints.
- Pydantic validation.
- Async programming where appropriate.
- Centralized configuration.
- Structured logging.
- Consistent error handling.

## Rule 4: Documentation

Every major module should have clear documentation.

Document:

- Its responsibility.
- Inputs.
- Outputs.
- Dependencies.
- Important implementation decisions.

Update README.md whenever the setup or functionality changes.

## Rule 5: Testing

Never claim that functionality works without testing it.

Write tests alongside implementation.

Fix failing tests before completing a phase.

## Rule 6: Environment Management

Create:

```text
.env.example
```

Never commit:

- API keys.
- Passwords.
- Database credentials.
- Secret tokens.
- Private configuration.

## Rule 7: Database Integrity

Use Alembic migrations.

Do not make undocumented schema changes.

Preserve existing data when modifying database structures.

## Rule 8: Cost Accuracy

Never fabricate cost savings.

Never hardcode model prices across business logic.

Use a centralized pricing registry.

Distinguish estimated expenditure from actual provider-reported usage and billed expenditure.

## Rule 9: Quality Preservation

Never assume cheaper models are equivalent to expensive models.

Use benchmark results and configurable quality requirements.

Never silently sacrifice quality to satisfy a budget.

## Rule 10: Existing Code Protection

Before implementing a phase:

1. Inspect the existing project.
2. Understand the current architecture.
3. Identify completed functionality.
4. Identify missing functionality.
5. Reuse existing implementations where appropriate.

Do not overwrite working code unnecessarily.

## Rule 11: Phase Completion Report

After each phase, provide:

```text
PHASE COMPLETED: [PHASE NUMBER]

1. Implemented Components
2. Files Created
3. Files Modified
4. Dependencies Added
5. Database Changes
6. APIs Implemented
7. Tests Executed
8. Test Results
9. Known Limitations
10. Next Phase Prerequisites
```

Then stop.

Wait for explicit authorization.

---

# 17. FINAL PROJECT DELIVERABLES

The completed Cost Guard project must contain:

1. Intelligent LLM API gateway.
2. Multi-provider integration.
3. Complexity-based model routing.
4. Quality-aware model selection.
5. Semantic caching.
6. Prompt optimization.
7. Token optimization.
8. Cost calculation and tracking.
9. Quality evaluation engine.
10. Benchmark framework.
11. Fallback mechanism.
12. Budget management.
13. Analytics backend.
14. React dashboard.
15. API playground.
16. Docker-based deployment.
17. Automated testing.
18. Monitoring and observability.
19. Complete documentation.

---

# 18. DEFINITION OF SUCCESS

Cost Guard should demonstrate the following through reproducible experiments:

**Cost Efficiency**

The optimized execution costs less than the baseline execution.

**Quality Preservation**

The optimized execution satisfies the configured quality threshold.

**Routing Intelligence**

Different tasks are routed to appropriate models.

**Cache Efficiency**

Repeated, compatible requests can be served without unnecessary provider calls.

**Token Efficiency**

Prompt and context optimization produce measurable token reductions without unacceptable quality loss.

**Operational Visibility**

Developers can identify where their AI expenditure originates.

**Budget Control**

Applications can enforce configurable spending limits.

**Reliability**

Provider failures, timeouts, and evaluation failures are handled predictably.

The final goal is not simply to build another LLM API wrapper.

The final goal is to build an intelligent optimization infrastructure layer that allows AI applications to achieve a better cost-quality-latency trade-off.

---

# 19. FIRST INSTRUCTION TO THE CODING AGENT

Before writing any code:

1. Read this entire instruction.md.
2. Inspect the existing repository.
3. Understand the project structure.
4. Identify existing implementations.
5. Check the development environment.
6. Prepare a concise Phase 1 implementation plan.
7. Identify technical dependencies.
8. Identify potential architectural conflicts.

Do not implement any phase until explicitly authorized.

Wait for the user to say:

"START PHASE 1"

Only then begin implementation.
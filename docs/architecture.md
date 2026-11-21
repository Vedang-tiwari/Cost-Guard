# Architecture Overview — Cost Guard Phase 1

## 1. Gateway Request Lifecycle

```text
  [ Client Application ]
            │
            │ HTTP POST /api/v1/chat/completions
            │ Headers: X-API-Key: cg_live_...
            ▼
  [ FastAPI Gateway Router ]
            │
            ├─► [ Security Dependency ]
            │     └─► Hash incoming key (SHA-256)
            │     └─► Query Application in PostgreSQL
            │     └─► Validate Active status
            │
            ├─► [ Model & Provider Factory ]
            │     └─► Resolve target model (e.g. gpt-4o -> openai)
            │     └─► Fetch ModelRegistry pricing per 1M tokens
            │
            ├─► [ LLM Provider Adapter ]
            │     └─► Execute Async Provider API call
            │     └─► Normalize Response & Token Counts
            │     └─► Standardize error mapping (auth, rate-limit, timeout)
            │
            ├─► [ Usage & Cost Engine ]
            │     └─► Calculate actual cost = (in/1M * in_rate) + (out/1M * out_rate)
            │     └─► Calculate baseline reference cost & savings
            │     └─► Asynchronously persist RequestLog record in PostgreSQL
            │
            ▼
  [ Return ChatCompletionResponse to Client ]
```

## 2. Directory Structure

- `backend/app/api/`: API routes (`chat.py`, `models.py`, `health.py`) and security dependencies (`dependencies.py`).
- `backend/app/core/`: Configuration, logging, exception hierarchy, security utilities.
- `backend/app/database/`: SQLAlchemy 2.0 async engine, models (`Organization`, `User`, `Application`, `ModelRegistry`, `RequestLog`).
- `backend/app/providers/`: Unified provider interface and concrete adapters (`OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`, `OllamaProvider`).
- `backend/app/schemas/`: Pydantic V2 request and response contracts.


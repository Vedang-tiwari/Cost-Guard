# Cost Guard API Documentation (Phase 1)

## Base URL
Default: `http://localhost:8000`

---

## 1. Health & Liveness Probes

### GET `/health`
Returns gateway operational status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "environment": "development",
  "version": "0.1.0",
  "timestamp": "2026-11-20T04:20:00Z"
}
```

### GET `/ready`
Validates database connectivity and upstream provider configuration.

**Response (200 OK):**
```json
{
  "status": "ready",
  "database": "connected",
  "providers": {
    "openai": true,
    "anthropic": true,
    "gemini": true,
    "ollama": false
  },
  "timestamp": "2026-11-20T04:20:00Z"
}
```

---

## 2. Models Registry

### GET `/api/v1/models`
Lists all active models and their cost metrics.

**Response (200 OK):**
```json
[
  {
    "id": "model_gpt4o",
    "provider": "openai",
    "model_name": "gpt-4o",
    "input_price_per_million": 2.50,
    "output_price_per_million": 10.00,
    "capabilities": {
      "chat": true,
      "vision": true,
      "function_calling": true
    },
    "context_window": 128000,
    "is_active": true,
    "pricing_version": "2024-11"
  }
]
```

### GET `/api/v1/models/{model_id}`
Returns details for a single model by ID or model name.

---

## 3. Chat Completions

### POST `/api/v1/chat/completions`

**Headers:**
- `Content-Type: application/json`
- `X-API-Key: cg_live_<your_key>` or `Authorization: Bearer <your_key>`

**Request Body:**
```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "system",
      "content": "You are a concise assistant."
    },
    {
      "role": "user",
      "content": "Explain machine learning."
    }
  ],
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Response (200 OK):**
```json
{
  "request_id": "req_8f1a3b5c7d9e",
  "model": "gpt-4o",
  "provider": "openai",
  "response": {
    "role": "assistant",
    "content": "Machine learning is a field of artificial intelligence..."
  },
  "usage": {
    "input_tokens": 24,
    "output_tokens": 42,
    "total_tokens": 66
  },
  "cost": {
    "estimated_cost": 0.00048,
    "baseline_cost": 0.00048,
    "savings": 0.0,
    "savings_percentage": 0.0
  },
  "optimization": {
    "cache_hit": false,
    "routing_strategy": "explicit",
    "complexity_score": 0.0,
    "prompt_optimized": false,
    "fallback_used": false
  }
}
```


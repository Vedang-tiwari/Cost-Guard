from unittest.mock import AsyncMock, patch

import pytest
from app.providers.base import ProviderResponse, ProviderUsage
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_ready_endpoint(client: AsyncClient):
    with patch("app.providers.factory.ProviderFactory.get_availability_status", AsyncMock(return_value={"openai": True, "anthropic": True, "gemini": True, "ollama": False})):
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["database"] == "connected"
        assert "providers" in data


@pytest.mark.asyncio
async def test_list_models(client: AsyncClient):
    response = await client.get("/api/v1/models")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(m["model_name"] == "gpt-4o" for m in data)


@pytest.mark.asyncio
async def test_chat_completions_missing_auth(client: AsyncClient):
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    response = await client.post("/api/v1/chat/completions", json=payload)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_completions_invalid_api_key(client: AsyncClient):
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello"}]
    }
    headers = {"X-API-Key": "invalid_api_key"}
    response = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_single_model(client: AsyncClient):
    response = await client.get("/api/v1/models/gpt-4o")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "gpt-4o"
    assert data["provider"] == "openai"


@pytest.mark.asyncio
async def test_get_model_not_found(client: AsyncClient):
    response = await client.get("/api/v1/models/non-existent-model")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_chat_completions_success(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org

    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Hello Cost Guard"}]
    }
    headers = {"X-API-Key": raw_key}

    mock_provider_response = ProviderResponse(
        content="Hello from Cost Guard Gateway!",
        model="gpt-4o",
        provider="openai",
        usage=ProviderUsage(input_tokens=15, output_tokens=10, total_tokens=25)
    )

    with patch("app.providers.openai_provider.OpenAIProvider.generate", AsyncMock(return_value=mock_provider_response)):
        response = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["request_id"].startswith("req_")
        assert data["model"] == "gpt-4o"
        assert data["provider"] == "openai"
        assert data["response"]["content"] == "Hello from Cost Guard Gateway!"
        assert data["usage"]["total_tokens"] == 25
        assert data["cost"]["estimated_cost"] > 0
        assert data["optimization"]["routing_strategy"] == "explicit"


@pytest.mark.asyncio
async def test_chat_completions_provider_error(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Trigger error"}]
    }
    headers = {"X-API-Key": raw_key}

    from app.core.exceptions import ProviderRateLimitError
    with patch("app.providers.openai_provider.OpenAIProvider.generate", AsyncMock(side_effect=ProviderRateLimitError("openai", "Rate limit exceeded"))):
        response = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
        assert response.status_code == 429
        data = response.json()
        assert "Rate limit exceeded" in data["detail"]

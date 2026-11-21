from unittest.mock import AsyncMock, patch

import pytest
from app.providers.base import ProviderResponse, ProviderUsage
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_pipeline_auto_routing_and_savings(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org

    # Low complexity classification task with model: auto
    payload = {
        "model": "auto",
        "messages": [
            {"role": "user", "content": "Please classify the following review as positive or negative: Loved it!"}
        ],
        "optimization": {
            "enabled": True,
            "semantic_cache": True,
            "prompt_optimization": True,
            "intelligent_routing": True,
        }
    }
    headers = {"X-API-Key": raw_key}

    mock_resp = ProviderResponse(
        content="Positive",
        model="gemini-1.5-flash",
        provider="gemini",
        usage=ProviderUsage(input_tokens=15, output_tokens=2, total_tokens=17)
    )

    with patch("app.providers.gemini_provider.GeminiProvider.generate", AsyncMock(return_value=mock_resp)):
        response = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
        assert response.status_code == 200
        data = response.json()

        # Verify intelligent routing selected economical model
        assert data["model"] == "gemini-1.5-flash"
        assert data["provider"] == "gemini"
        assert data["response"]["content"] == "Positive"
        assert data["optimization"]["routing_strategy"] == "complexity_based"
        assert data["optimization"]["prompt_optimized"] is True
        assert data["optimization"]["cache_hit"] is False
        assert data["cost"]["savings"] >= 0.0
        assert data["cost"]["savings_percentage"] > 70.0


@pytest.mark.asyncio
async def test_pipeline_semantic_cache_hit(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": "What is the capital of France?"}
        ],
        "optimization": {
            "enabled": True,
            "semantic_cache": True,
        }
    }
    headers = {"X-API-Key": raw_key}

    mock_resp = ProviderResponse(
        content="The capital of France is Paris.",
        model="gpt-4o-mini",
        provider="openai",
        usage=ProviderUsage(input_tokens=12, output_tokens=8, total_tokens=20)
    )

    # First request: Cache Miss -> calls provider and caches response
    with patch("app.providers.openai_provider.OpenAIProvider.generate", AsyncMock(return_value=mock_resp)) as mock_call:
        res1 = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
        assert res1.status_code == 200
        data1 = res1.json()
        assert data1["optimization"]["cache_hit"] is False
        assert mock_call.call_count == 1

    # Second identical request: Cache Hit -> returns directly with ZERO provider calls and 100% savings!
    with patch("app.providers.openai_provider.OpenAIProvider.generate", AsyncMock()) as mock_call2:
        res2 = await client.post("/api/v1/chat/completions", json=payload, headers=headers)
        assert res2.status_code == 200
        data2 = res2.json()
        assert data2["optimization"]["cache_hit"] is True
        assert data2["provider"] == "cache"
        assert data2["response"]["content"] == "The capital of France is Paris."
        assert data2["cost"]["estimated_cost"] == 0.0
        assert data2["cost"]["savings_percentage"] == 100.0
        assert mock_call2.call_count == 0  # Provider was never called!

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.core.exceptions import (
    ProviderAuthenticationError,
)
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import ProviderResponse
from app.providers.factory import ProviderFactory
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider
from app.schemas.request import ChatCompletionRequest, ChatMessage


@pytest.mark.asyncio
async def test_openai_provider_success():
    provider = OpenAIProvider(api_key="sk-fake-key")

    mock_choice = MagicMock()
    mock_choice.message.content = "OpenAI Hello!"
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 5
    mock_usage.total_tokens = 15

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    mock_completion.model = "gpt-4o"
    mock_completion.usage = mock_usage

    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    provider._client = mock_client

    request = ChatCompletionRequest(
        model="gpt-4o",
        messages=[ChatMessage(role="user", content="Hello")]
    )

    response = await provider.generate(request)
    assert isinstance(response, ProviderResponse)
    assert response.content == "OpenAI Hello!"
    assert response.model == "gpt-4o"
    assert response.provider == "openai"
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 5
    assert response.usage.total_tokens == 15


@pytest.mark.asyncio
async def test_anthropic_provider_success():
    provider = AnthropicProvider(api_key="sk-ant-fake")

    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "Anthropic Claude Hello!"

    mock_response = MagicMock()
    mock_response.content = [mock_block]
    mock_response.model = "claude-3-5-sonnet-20241022"
    mock_response.usage = MagicMock(input_tokens=15, output_tokens=8)

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    request = ChatCompletionRequest(
        model="claude-3-5-sonnet-20241022",
        messages=[
            ChatMessage(role="system", content="You are a helper."),
            ChatMessage(role="user", content="Hi")
        ]
    )

    response = await provider.generate(request)
    assert response.content == "Anthropic Claude Hello!"
    assert response.provider == "anthropic"
    assert response.usage.input_tokens == 15
    assert response.usage.output_tokens == 8


@pytest.mark.asyncio
async def test_ollama_provider_success():
    provider = OllamaProvider(base_url="http://localhost:11434")

    mock_http_response = MagicMock()
    mock_http_response.status_code = 200
    mock_http_response.json.return_value = {
        "model": "llama3.2",
        "message": {"role": "assistant", "content": "Ollama Response!"},
        "prompt_eval_count": 20,
        "eval_count": 10
    }

    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_http_response)):
        request = ChatCompletionRequest(
            model="llama3.2",
            messages=[ChatMessage(role="user", content="Hi Ollama")]
        )
        response = await provider.generate(request)
        assert response.content == "Ollama Response!"
        assert response.provider == "ollama"
        assert response.usage.input_tokens == 20
        assert response.usage.output_tokens == 10


@pytest.mark.asyncio
async def test_gemini_provider_success():
    provider = GeminiProvider(api_key="fake-gemini-key")

    mock_response = MagicMock()
    mock_response.text = "Gemini Hello!"
    mock_response.usage_metadata = MagicMock(prompt_token_count=12, candidates_token_count=6)

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    provider._client = mock_client

    request = ChatCompletionRequest(
        model="gemini-1.5-pro",
        messages=[ChatMessage(role="user", content="Hi Gemini")]
    )

    response = await provider.generate(request)
    assert response.content == "Gemini Hello!"
    assert response.provider == "gemini"
    assert response.usage.input_tokens == 12
    assert response.usage.output_tokens == 6


@pytest.mark.asyncio
async def test_openai_provider_missing_key():
    provider = OpenAIProvider(api_key=None)
    provider.api_key = None
    provider._client = None

    request = ChatCompletionRequest(
        model="gpt-4o",
        messages=[ChatMessage(role="user", content="Hi")]
    )

    with pytest.raises(ProviderAuthenticationError):
        await provider.generate(request)


@pytest.mark.asyncio
async def test_ollama_provider_unreachable():
    import httpx
    provider = OllamaProvider(base_url="http://localhost:11434")

    with patch("httpx.AsyncClient.post", AsyncMock(side_effect=httpx.ConnectError("Connection refused"))):
        request = ChatCompletionRequest(
            model="llama3.2",
            messages=[ChatMessage(role="user", content="Hi")]
        )
        from app.core.exceptions import ProviderUnavailableError
        with pytest.raises(ProviderUnavailableError):
            await provider.generate(request)


def test_provider_factory_resolution():
    factory = ProviderFactory()
    p_name, _ = factory.resolve_provider_for_model("gpt-4o")
    assert p_name == "openai"

    p_name, _ = factory.resolve_provider_for_model("claude-3-5-sonnet-20241022")
    assert p_name == "anthropic"

    p_name, _ = factory.resolve_provider_for_model("gemini-1.5-pro")
    assert p_name == "gemini"

    p_name, _ = factory.resolve_provider_for_model("llama3.2")
    assert p_name == "ollama"

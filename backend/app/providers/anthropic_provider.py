from typing import Any

import anthropic
from app.core.config import get_settings
from app.core.exceptions import (
    ProviderAuthenticationError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.core.logging import get_logger
from app.providers.base import BaseLLMProvider, ProviderResponse, ProviderUsage
from app.schemas.request import ChatCompletionRequest

logger = get_logger(__name__)


class AnthropicProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(provider_name="anthropic")
        settings = get_settings()
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self._client: anthropic.AsyncAnthropic | None = None
        if self.api_key:
            self._client = anthropic.AsyncAnthropic(api_key=self.api_key, timeout=settings.DEFAULT_TIMEOUT_SECONDS)

    async def is_available(self) -> bool:
        return self._client is not None

    async def generate(self, request: ChatCompletionRequest) -> ProviderResponse:
        if not self._client:
            raise ProviderAuthenticationError(
                provider=self.provider_name,
                message="Anthropic API key is not configured"
            )

        # Anthropic separates system messages from the messages list
        system_prompts: list[str] = []
        messages: list[dict[str, Any]] = []

        for msg in request.messages:
            if msg.role == "system":
                system_prompts.append(msg.content)
            else:
                messages.append({"role": msg.role, "content": msg.content})

        # Anthropic requires max_tokens
        max_tokens = request.max_tokens or 1024

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        if system_prompts:
            kwargs["system"] = "\n\n".join(system_prompts)
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature

        try:
            response = await self._client.messages.create(**kwargs)
            content = ""
            for block in response.content:
                if block.type == "text":
                    content += block.text

            input_tokens = response.usage.input_tokens if response.usage else 0
            output_tokens = response.usage.output_tokens if response.usage else 0

            return ProviderResponse(
                content=content,
                model=response.model or request.model,
                provider=self.provider_name,
                usage=ProviderUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                ),
            )
        except anthropic.AuthenticationError as e:
            logger.error("Anthropic authentication failed", exc_info=e)
            raise ProviderAuthenticationError(provider=self.provider_name, message=str(e))
        except anthropic.RateLimitError as e:
            logger.warning("Anthropic rate limit hit", exc_info=e)
            raise ProviderRateLimitError(provider=self.provider_name, message=str(e))
        except anthropic.APITimeoutError as e:
            logger.error("Anthropic timeout", exc_info=e)
            raise ProviderTimeoutError(provider=self.provider_name, message=str(e))
        except anthropic.APIConnectionError as e:
            logger.error("Anthropic connection error", exc_info=e)
            raise ProviderUnavailableError(provider=self.provider_name, message=str(e))
        except anthropic.APIError as e:
            logger.error("Anthropic API error", exc_info=e)
            raise ProviderError(provider=self.provider_name, message=str(e))

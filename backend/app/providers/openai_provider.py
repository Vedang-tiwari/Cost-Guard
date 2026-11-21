from typing import Any

import openai
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


class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(provider_name="openai")
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self._client: openai.AsyncOpenAI | None = None
        if self.api_key:
            self._client = openai.AsyncOpenAI(api_key=self.api_key, timeout=settings.DEFAULT_TIMEOUT_SECONDS)

    async def is_available(self) -> bool:
        return self._client is not None

    async def generate(self, request: ChatCompletionRequest) -> ProviderResponse:
        if not self._client:
            raise ProviderAuthenticationError(
                provider=self.provider_name,
                message="OpenAI API key is not configured"
            )

        messages_payload: list[dict[str, Any]] = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages_payload,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature

        try:
            response = await self._client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            content = choice.message.content or ""

            usage = ProviderUsage(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0,
            )

            return ProviderResponse(
                content=content,
                model=response.model or request.model,
                provider=self.provider_name,
                usage=usage,
            )
        except openai.AuthenticationError as e:
            logger.error("OpenAI authentication failed", exc_info=e)
            raise ProviderAuthenticationError(provider=self.provider_name, message=str(e))
        except openai.RateLimitError as e:
            logger.warning("OpenAI rate limit hit", exc_info=e)
            raise ProviderRateLimitError(provider=self.provider_name, message=str(e))
        except openai.APITimeoutError as e:
            logger.error("OpenAI timeout", exc_info=e)
            raise ProviderTimeoutError(provider=self.provider_name, message=str(e))
        except openai.APIConnectionError as e:
            logger.error("OpenAI connection error", exc_info=e)
            raise ProviderUnavailableError(provider=self.provider_name, message=str(e))
        except openai.APIError as e:
            logger.error("OpenAI API error", exc_info=e)
            raise ProviderError(provider=self.provider_name, message=str(e))

from typing import Any

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


class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        super().__init__(provider_name="gemini")
        settings = get_settings()
        self.api_key = api_key or settings.GEMINI_API_KEY
        self._client: Any = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI client: {e}")

    async def is_available(self) -> bool:
        return self._client is not None

    async def generate(self, request: ChatCompletionRequest) -> ProviderResponse:
        if not self._client:
            raise ProviderAuthenticationError(
                provider=self.provider_name,
                message="Google Gemini API key is not configured"
            )

        try:
            from google.genai import types

            # Format system prompt and contents
            system_instruction = None
            contents: list[types.Content] = []

            for msg in request.messages:
                if msg.role == "system":
                    system_instruction = msg.content
                else:
                    role = "user" if msg.role == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.content)]
                        )
                    )

            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=request.temperature,
                max_output_tokens=request.max_tokens,
            )

            # Call async generate_content
            response = await self._client.aio.models.generate_content(
                model=request.model,
                contents=contents,
                config=config,
            )

            content = response.text or ""
            input_tokens = 0
            output_tokens = 0
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count or 0
                output_tokens = response.usage_metadata.candidates_token_count or 0

            return ProviderResponse(
                content=content,
                model=request.model,
                provider=self.provider_name,
                usage=ProviderUsage(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=input_tokens + output_tokens,
                ),
            )
        except Exception as e:
            error_msg = str(e)
            logger.error("Gemini API error", exc_info=e)
            if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
                raise ProviderRateLimitError(provider=self.provider_name, message=error_msg)
            elif "PERMISSION_DENIED" in error_msg or "UNAUTHENTICATED" in error_msg or "API key not valid" in error_msg:
                raise ProviderAuthenticationError(provider=self.provider_name, message=error_msg)
            elif "DEADLINE_EXCEEDED" in error_msg or "timed out" in error_msg.lower():
                raise ProviderTimeoutError(provider=self.provider_name, message=error_msg)
            elif "UNAVAILABLE" in error_msg:
                raise ProviderUnavailableError(provider=self.provider_name, message=error_msg)
            else:
                raise ProviderError(provider=self.provider_name, message=error_msg)

from typing import Any

import httpx
from app.core.config import get_settings
from app.core.exceptions import (
    ProviderError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from app.core.logging import get_logger
from app.providers.base import BaseLLMProvider, ProviderResponse, ProviderUsage
from app.schemas.request import ChatCompletionRequest

logger = get_logger(__name__)


class OllamaProvider(BaseLLMProvider):
    def __init__(self, base_url: str | None = None):
        super().__init__(provider_name="ollama")
        settings = get_settings()
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.timeout = settings.DEFAULT_TIMEOUT_SECONDS

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate(self, request: ChatCompletionRequest) -> ProviderResponse:
        messages_payload: list[dict[str, str]] = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

        options: dict[str, Any] = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens

        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages_payload,
            "stream": False,
            "options": options,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()

                content = data.get("message", {}).get("content", "")
                input_tokens = data.get("prompt_eval_count", 0)
                output_tokens = data.get("eval_count", 0)

                return ProviderResponse(
                    content=content,
                    model=data.get("model", request.model),
                    provider=self.provider_name,
                    usage=ProviderUsage(
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        total_tokens=input_tokens + output_tokens,
                    ),
                )
        except httpx.ConnectError as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}", exc_info=e)
            raise ProviderUnavailableError(
                provider=self.provider_name,
                message=f"Could not connect to Ollama service at {self.base_url}. Is Ollama running?"
            )
        except httpx.TimeoutException as e:
            logger.error("Ollama request timed out", exc_info=e)
            raise ProviderTimeoutError(provider=self.provider_name, message=str(e))
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama returned HTTP error {e.response.status_code}", exc_info=e)
            raise ProviderError(provider=self.provider_name, message=f"HTTP {e.response.status_code}: {e.response.text}")
        except Exception as e:
            logger.error("Unexpected Ollama error", exc_info=e)
            raise ProviderError(provider=self.provider_name, message=str(e))

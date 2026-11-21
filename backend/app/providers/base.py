from abc import ABC, abstractmethod
from typing import Any

from app.schemas.request import ChatCompletionRequest
from pydantic import BaseModel, Field


class ProviderUsage(BaseModel):
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)


class ProviderResponse(BaseModel):
    content: str
    model: str
    provider: str
    usage: ProviderUsage
    raw_response: dict[str, Any] | None = None


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers in Cost Guard."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name

    @abstractmethod
    async def generate(self, request: ChatCompletionRequest) -> ProviderResponse:
        """Executes a chat completion request and returns a normalized ProviderResponse."""

    @abstractmethod
    async def is_available(self) -> bool:
        """Checks if the provider is configured and reachable."""

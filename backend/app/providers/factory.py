
from app.core.exceptions import ProviderError
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import BaseLLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider

# Default known model to provider mapping for Phase 1
KNOWN_MODELS: dict[str, str] = {
    # OpenAI
    "gpt-4o": "openai",
    "gpt-4o-mini": "openai",
    "gpt-4-turbo": "openai",
    "gpt-3.5-turbo": "openai",
    # Anthropic
    "claude-3-5-sonnet-20241022": "anthropic",
    "claude-3-5-haiku-20241022": "anthropic",
    "claude-3-opus-20240229": "anthropic",
    # Google Gemini
    "gemini-1.5-pro": "gemini",
    "gemini-1.5-flash": "gemini",
    "gemini-2.0-flash": "gemini",
    # Ollama local models
    "llama3.2": "ollama",
    "llama3.1": "ollama",
    "mistral": "ollama",
    "qwen2.5": "ollama",
}


class ProviderFactory:
    """Manages provider instances and resolves models to the corresponding provider."""

    def __init__(self):
        self._providers: dict[str, BaseLLMProvider] = {
            "openai": OpenAIProvider(),
            "anthropic": AnthropicProvider(),
            "gemini": GeminiProvider(),
            "ollama": OllamaProvider(),
        }

    def register_provider(self, name: str, provider: BaseLLMProvider) -> None:
        self._providers[name.lower()] = provider

    def get_provider(self, provider_name: str) -> BaseLLMProvider:
        provider = self._providers.get(provider_name.lower())
        if not provider:
            raise ProviderError(provider=provider_name, message=f"Unsupported provider: {provider_name}")
        return provider

    def resolve_provider_for_model(self, model_name: str, explicit_provider: str | None = None) -> tuple[str, BaseLLMProvider]:
        """
        Determines the provider for a given model.
        In Phase 1, uses explicit provider if supplied, or looks up in known model mapping.
        """
        if explicit_provider:
            provider_name = explicit_provider.lower()
        elif model_name in KNOWN_MODELS:
            provider_name = KNOWN_MODELS[model_name]
        elif model_name.startswith(("gpt-", "o1-")):
            provider_name = "openai"
        elif model_name.startswith("claude-"):
            provider_name = "anthropic"
        elif model_name.startswith("gemini-"):
            provider_name = "gemini"
        else:
            # Default fallback for local / unknown models
            provider_name = "ollama"

        provider = self.get_provider(provider_name)
        return provider_name, provider

    async def get_availability_status(self) -> dict[str, bool]:
        status_map = {}
        for name, provider in self._providers.items():
            status_map[name] = await provider.is_available()
        return status_map


_factory_instance: ProviderFactory | None = None


def get_provider_factory() -> ProviderFactory:
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ProviderFactory()
    return _factory_instance

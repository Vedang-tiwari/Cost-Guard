from typing import Any

from pydantic import BaseModel, Field


class ModelPricing(BaseModel):
    provider: str
    model_name: str
    input_price_per_million: float
    output_price_per_million: float
    context_window: int = 128000
    tier: str = "medium"  # low, medium, high
    capabilities: dict[str, Any] = Field(default_factory=dict)


# Default model catalog with current market pricing per million tokens
CATALOG: dict[str, ModelPricing] = {
    # Tier 1 (Low Cost / Economical)
    "gpt-4o-mini": ModelPricing(
        provider="openai",
        model_name="gpt-4o-mini",
        input_price_per_million=0.15,
        output_price_per_million=0.60,
        context_window=128000,
        tier="low",
        capabilities={"chat": True, "json": True, "tools": True},
    ),
    "gemini-1.5-flash": ModelPricing(
        provider="gemini",
        model_name="gemini-1.5-flash",
        input_price_per_million=0.075,
        output_price_per_million=0.30,
        context_window=1000000,
        tier="low",
        capabilities={"chat": True, "json": True, "tools": True, "multimodal": True},
    ),
    "claude-3-5-haiku-20241022": ModelPricing(
        provider="anthropic",
        model_name="claude-3-5-haiku-20241022",
        input_price_per_million=0.80,
        output_price_per_million=4.00,
        context_window=200000,
        tier="low",
        capabilities={"chat": True, "json": True, "tools": True},
    ),
    "llama3.2": ModelPricing(
        provider="ollama",
        model_name="llama3.2",
        input_price_per_million=0.0,
        output_price_per_million=0.0,
        context_window=8192,
        tier="low",
        capabilities={"chat": True, "local": True},
    ),

    # Tier 2 (Balanced / Capable)
    "gpt-4o": ModelPricing(
        provider="openai",
        model_name="gpt-4o",
        input_price_per_million=2.50,
        output_price_per_million=10.00,
        context_window=128000,
        tier="medium",
        capabilities={"chat": True, "json": True, "tools": True, "multimodal": True},
    ),
    "gemini-1.5-pro": ModelPricing(
        provider="gemini",
        model_name="gemini-1.5-pro",
        input_price_per_million=1.25,
        output_price_per_million=5.00,
        context_window=2000000,
        tier="medium",
        capabilities={"chat": True, "json": True, "tools": True, "multimodal": True},
    ),
    "claude-3-5-sonnet-20241022": ModelPricing(
        provider="anthropic",
        model_name="claude-3-5-sonnet-20241022",
        input_price_per_million=3.00,
        output_price_per_million=15.00,
        context_window=200000,
        tier="high",
        capabilities={"chat": True, "json": True, "tools": True, "multimodal": True},
    ),
}

# The baseline model against which savings are measured
BASELINE_MODEL = "gpt-4o"


def get_model_pricing(model_name: str) -> ModelPricing:
    """Retrieves pricing for a model from catalog, or returns baseline pricing if unknown."""
    return CATALOG.get(model_name, CATALOG[BASELINE_MODEL])


class PricingRegistry:
    """Convenience registry interface for model pricing catalog."""

    def __init__(self, catalog: dict[str, ModelPricing] | None = None) -> None:
        self._catalog = catalog or CATALOG

    def get(self, model_name: str) -> ModelPricing | None:
        return self._catalog.get(model_name)

    def get_or_baseline(self, model_name: str) -> ModelPricing:
        return self._catalog.get(model_name, self._catalog[BASELINE_MODEL])

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        pricing = self.get_or_baseline(model_name)
        in_cost = (input_tokens / 1_000_000) * pricing.input_price_per_million
        out_cost = (output_tokens / 1_000_000) * pricing.output_price_per_million
        return round(in_cost + out_cost, 6)

    def list_models(self) -> list[ModelPricing]:
        return list(self._catalog.values())


pricing_registry = PricingRegistry()

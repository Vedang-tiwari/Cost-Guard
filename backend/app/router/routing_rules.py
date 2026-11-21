from typing import Literal

ComplexityTier = Literal["low", "medium", "high"]

# Task to minimum recommended tier
TASK_TIER_RULES: dict[str, ComplexityTier] = {
    "classification": "low",
    "conversational": "low",
    "extraction": "low",
    "summarization": "low",
    "math": "medium",
    "code": "medium",
    "reasoning": "high",
}

# Preferred models per tier in order of cost efficiency
TIER_PREFERRED_MODELS: dict[ComplexityTier, list[str]] = {
    "low": ["gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022", "llama3.2"],
    "medium": ["gpt-4o-mini", "gemini-1.5-flash", "gemini-1.5-pro", "gpt-4o"],
    "high": ["gpt-4o", "gemini-1.5-pro", "claude-3-5-sonnet-20241022"],
}

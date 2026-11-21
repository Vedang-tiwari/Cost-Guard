FALLBACK_CHAINS: dict[str, str] = {
    "gpt-4o-mini": "gpt-4o",
    "gemini-1.5-flash": "gemini-1.5-pro",
    "claude-3-5-haiku-20241022": "claude-3-5-sonnet-20241022",
    "llama3.2": "gpt-4o-mini",
    "gemini-1.5-pro": "gpt-4o",
    "gpt-4o": "claude-3-5-sonnet-20241022",
}


def get_fallback_model(current_model: str) -> str:
    """Returns the designated higher-tier fallback model for a given model."""
    return FALLBACK_CHAINS.get(current_model, "gpt-4o")

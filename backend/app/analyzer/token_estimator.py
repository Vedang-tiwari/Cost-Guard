from app.schemas.request import ChatMessage

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False


def get_encoding_for_model(model_name: str):
    """Retrieves or falls back to standard tiktoken encoding."""
    if not _TIKTOKEN_AVAILABLE:
        return None
    try:
        return tiktoken.encoding_for_model(model_name)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def estimate_tokens(text: str, model_name: str = "gpt-4o") -> int:
    """
    Estimates token count using tiktoken for OpenAI models,
    or character/word heuristic (approx 4 chars or 0.75 words per token) as fallback.
    """
    if not text:
        return 0

    if _TIKTOKEN_AVAILABLE and (model_name.startswith("gpt-") or model_name.startswith("o1-")):
        try:
            encoding = get_encoding_for_model(model_name)
            if encoding:
                return len(encoding.encode(text))
        except Exception:
            pass

    # Heuristic fallback: ~4 characters per token
    return max(1, len(text) // 4)


def estimate_messages_tokens(messages: list[ChatMessage], model_name: str = "gpt-4o") -> int:
    """
    Estimates total input tokens for a list of chat messages,
    including formatting overhead (3 tokens per message for role/content wrappers).
    """
    total = 0
    for msg in messages:
        total += 3  # Formatting overhead per message
        total += estimate_tokens(msg.content, model_name)
    total += 3  # Priming tokens for assistant response
    return total


def estimate_expected_output_tokens(task_type: str, max_tokens: int | None = None) -> int:
    """
    Estimates output token consumption based on task type if max_tokens is not provided.
    """
    if max_tokens is not None:
        return max_tokens

    # Expected output lengths by task category
    typical_output_tokens = {
        "classification": 15,
        "extraction": 150,
        "summarization": 250,
        "code": 400,
        "math": 200,
        "reasoning": 500,
        "conversational": 120,
    }
    return typical_output_tokens.get(task_type.lower(), 200)

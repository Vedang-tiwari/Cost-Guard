from app.schemas.request import ChatMessage


def reduce_context(messages: list[ChatMessage], max_context_tokens: int = 8000) -> list[ChatMessage]:
    """
    Reduces multi-turn context by deduplicating redundant system prompts
    and preserving the latest user and assistant turns.
    """
    if not messages:
        return []

    # Preserve last system message if multiple system messages exist
    system_msgs = [m for m in messages if m.role == "system"]
    non_system_msgs = [m for m in messages if m.role != "system"]

    deduped_system = [system_msgs[-1]] if system_msgs else []

    # Combine
    return deduped_system + non_system_msgs

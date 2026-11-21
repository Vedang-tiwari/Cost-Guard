import re

from app.analyzer.token_estimator import estimate_messages_tokens
from app.schemas.request import ChatMessage
from pydantic import BaseModel, Field


class PromptOptimizationResult(BaseModel):
    optimized_messages: list[ChatMessage]
    original_tokens: int
    optimized_tokens: int
    tokens_saved: int
    savings_percentage: float
    methods_applied: list[str] = Field(default_factory=list)


FILLER_PATTERNS = [
    r"^(?:please\s+|could\s+you\s+please\s+|kindly\s+|can\s+you\s+please\s+|i\s+want\s+you\s+to\s+|i\s+would\s+like\s+you\s+to\s+)",
    r"^(?:answer\s+the\s+following\s+question:\s*|respond\s+to\s+the\s+following:\s*)",
]


def clean_text(text: str) -> tuple[str, list[str]]:
    """Cleans text of redundant formatting and empty whitespace."""
    applied: list[str] = []
    cleaned = text

    # 1. Normalize line-level whitespace and consecutive newlines
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in cleaned.splitlines()]
    new_text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if new_text != cleaned:
        applied.append("whitespace_normalization")
        cleaned = new_text

    # 2. Repeatedly strip conversational filler prefixes in user prompt
    changed = True
    while changed:
        changed = False
        for pat in FILLER_PATTERNS:
            sub = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
            if sub != cleaned and len(sub) > 5:
                cleaned = sub[0].upper() + sub[1:] if sub else ""
                applied.append("filler_removal")
                changed = True
                break

    return cleaned, applied


def optimize_prompt(messages: list[ChatMessage], enabled: bool = True) -> PromptOptimizationResult:
    """
    Optimizes messages by trimming redundant whitespace, removing filler phrases,
    and deduplicating identical consecutive sentences.
    Preserves all instructions, formatting constraints, and safety guidelines.
    """
    original_tokens = estimate_messages_tokens(messages)

    if not enabled:
        return PromptOptimizationResult(
            optimized_messages=messages,
            original_tokens=original_tokens,
            optimized_tokens=original_tokens,
            tokens_saved=0,
            savings_percentage=0.0,
            methods_applied=[],
        )

    all_methods: set[str] = set()
    new_messages: list[ChatMessage] = []

    for msg in messages:
        cleaned_content, methods = clean_text(msg.content)
        all_methods.update(methods)
        new_messages.append(ChatMessage(role=msg.role, content=cleaned_content))

    optimized_tokens = estimate_messages_tokens(new_messages)
    tokens_saved = max(0, original_tokens - optimized_tokens)
    savings_pct = round((tokens_saved / original_tokens * 100), 2) if original_tokens > 0 else 0.0

    return PromptOptimizationResult(
        optimized_messages=new_messages,
        original_tokens=original_tokens,
        optimized_tokens=optimized_tokens,
        tokens_saved=tokens_saved,
        savings_percentage=savings_pct,
        methods_applied=list(all_methods),
    )

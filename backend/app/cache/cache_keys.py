import hashlib
import json

from app.schemas.request import ChatMessage


def generate_prompt_hash(messages: list[ChatMessage]) -> str:
    """Generates a stable MD5/SHA-256 hash of messages content and roles."""
    normalized = [{"r": m.role, "c": " ".join(m.content.strip().split())} for m in messages]
    payload = json.dumps(normalized, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_cache_key(
    application_id: str,
    messages: list[ChatMessage],
    temperature: float = 0.7,
    max_tokens: int | None = None,
    prompt_version: str = "v1",
) -> str:
    """
    Generates a deterministic composite cache key enforcing tenant/application isolation
    and compatibility across generation parameters.
    """
    prompt_hash = generate_prompt_hash(messages)
    key_payload = f"app:{application_id}:ver:{prompt_version}:temp:{round(temperature, 2)}:max:{max_tokens or 0}:hash:{prompt_hash}"
    return hashlib.sha256(key_payload.encode("utf-8")).hexdigest()

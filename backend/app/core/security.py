import hashlib
import secrets


def hash_api_key(api_key: str) -> str:
    """Computes SHA-256 hash of an API key for safe database storage and lookup."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def generate_api_key(prefix: str = "cg_live_") -> tuple[str, str]:
    """
    Generates a secure random API key and its hash.
    Returns:
        (raw_key, hashed_key)
    """
    random_part = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{random_part}"
    hashed_key = hash_api_key(raw_key)
    return raw_key, hashed_key


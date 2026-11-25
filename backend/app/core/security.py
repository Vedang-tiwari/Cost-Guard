import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError


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


def hash_password(password: str) -> str:
    """Hashes a plaintext password with a random 16-byte salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    iterations = 200_000
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${dk.hex()}"


def verify_password(plain_password: str, stored_hash: str) -> bool:
    """Verifies a plaintext password against a stored PBKDF2-HMAC-SHA256 hash."""
    try:
        scheme, iter_str, salt_hex, hash_hex = stored_hash.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(data: dict[str, Any], expires_minutes: int = 1440) -> str:
    """Creates a signed HMAC-SHA256 JWT token."""
    settings = get_settings()
    now = int(time.time())
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        **data,
        "iat": now,
        "exp": now + (expires_minutes * 60),
    }

    h_enc = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    p_enc = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{h_enc}.{p_enc}".encode("ascii")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    s_enc = _b64url_encode(sig)
    return f"{h_enc}.{p_enc}.{s_enc}"


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodes and validates an HMAC-SHA256 JWT token."""
    settings = get_settings()
    parts = token.split(".")
    if len(parts) != 3:
        raise AuthenticationError("Invalid session token format")

    h_enc, p_enc, s_enc = parts
    signing_input = f"{h_enc}.{p_enc}".encode("ascii")
    expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        actual_sig = _b64url_decode(s_enc)
    except Exception:
        raise AuthenticationError("Malformed token signature")

    if not hmac.compare_digest(actual_sig, expected_sig):
        raise AuthenticationError("Invalid session token signature")

    try:
        payload = json.loads(_b64url_decode(p_enc).decode("utf-8"))
    except Exception:
        raise AuthenticationError("Malformed token payload")

    if payload.get("exp", 0) < int(time.time()):
        raise AuthenticationError("Session token has expired")

    return payload

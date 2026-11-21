from app.core.security import generate_api_key, hash_api_key


def test_hash_api_key_deterministic():
    key = "test_api_key_123"
    hash1 = hash_api_key(key)
    hash2 = hash_api_key(key)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 is 64 hex characters


def test_generate_api_key():
    raw_key, hashed_key = generate_api_key(prefix="cg_live_")
    assert raw_key.startswith("cg_live_")
    assert hash_api_key(raw_key) == hashed_key
    assert len(raw_key) > 30


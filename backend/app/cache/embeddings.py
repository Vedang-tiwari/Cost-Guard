import math
import re
from collections.abc import Sequence

EMBEDDING_DIM = 256

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "or", "that",
    "the", "to", "was", "were", "what", "where", "which", "who", "will", "with",
}


def _normalize_vector(vec: list[float]) -> list[float]:
    """Normalizes vector to unit length (L2 norm = 1.0)."""
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [round(x / norm, 6) for x in vec]


def generate_embedding(text: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """
    Generates a dense normalized feature vector from input text.
    Applies topical term weighting (TF-IDF style stop-word suppression)
    and sub-word n-gram hashing to capture semantic similarity.
    """
    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())

    if not words:
        return vec

    for i, word in enumerate(words):
        is_stop = word in STOP_WORDS
        weight = 0.15 if is_stop else 2.5
        pos_weight = weight / (math.log(i + 2))

        # Primary token hash
        h1 = (hash(word) * 2654435761) % dim
        vec[h1] += pos_weight

        # Sub-word trigrams for non-stop words
        if not is_stop and len(word) >= 3:
            for j in range(len(word) - 2):
                tri = word[j:j+3]
                th = (hash(tri) * 2246822519) % dim
                vec[th] += 0.4

    return _normalize_vector(vec)


def cosine_similarity(v1: Sequence[float], v2: Sequence[float]) -> float:
    """Calculates cosine similarity between two vectors (-1.0 to 1.0)."""
    if len(v1) != len(v2) or not v1:
        return 0.0

    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    sim = dot / (norm_a * norm_b)
    return round(max(0.0, min(1.0, sim)), 4)

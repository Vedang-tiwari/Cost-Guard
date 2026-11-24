import ast
import json
import re
from typing import Any

from app.cache.embeddings import cosine_similarity, generate_embedding


def exact_match(
    candidate: str,
    reference: str,
    case_sensitive: bool = False,
    strip_whitespace: bool = True,
) -> float:
    """Computes exact match score (1.0 or 0.0) between candidate and reference."""
    c = candidate.strip() if strip_whitespace else candidate
    r = reference.strip() if strip_whitespace else reference

    if not case_sensitive:
        c = c.lower()
        r = r.lower()

    return 1.0 if c == r else 0.0


def semantic_similarity(candidate: str, reference: str) -> float:
    """Computes semantic similarity score (0.0 to 1.0) using normalized embedding vectors."""
    if not candidate.strip() or not reference.strip():
        return 1.0 if candidate.strip() == reference.strip() else 0.0

    v1 = generate_embedding(candidate)
    v2 = generate_embedding(reference)
    return cosine_similarity(v1, v2)


def json_schema_validity(
    candidate: str,
    expected_schema: dict[str, Any] | None = None,
) -> tuple[float, dict[str, Any]]:
    """
    Validates if candidate contains valid JSON and optionally matches an expected schema.
    Returns (score 0.0-1.0, details dict).
    """
    text = candidate.strip()
    # Strip optional markdown code fence
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1).strip()

    try:
        data = json.loads(text)
    except Exception as e:
        return 0.0, {"valid_json": False, "error": str(e)}

    if not expected_schema:
        return 1.0, {"valid_json": True, "keys": list(data.keys()) if isinstance(data, dict) else []}

    # Validate against expected keys
    if isinstance(data, dict):
        required_keys = set(expected_schema.get("required", expected_schema.keys()))
        present_keys = set(data.keys())
        if not required_keys:
            return 1.0, {"valid_json": True, "schema_match": True}

        matching = len(required_keys.intersection(present_keys))
        score = round(matching / len(required_keys), 4)
        return score, {
            "valid_json": True,
            "matching_keys": list(required_keys.intersection(present_keys)),
            "missing_keys": list(required_keys - present_keys),
        }

    return 0.5, {"valid_json": True, "note": "Root is not a JSON object"}


def length_consistency(candidate: str, reference: str) -> float:
    """
    Penalizes extreme under-generation or hallucinated runaway generation.
    Returns score from 0.0 to 1.0.
    """
    len_c = max(1, len(candidate.strip()))
    len_r = max(1, len(reference.strip()))
    ratio = min(len_c, len_r) / max(len_c, len_r)
    return round(ratio, 4)


def task_rubric_score(candidate: str, task_type: str, reference: str | None = None) -> float:
    """
    Applies task-specific heuristic rubrics.
    Categories: classification, extraction, summarization, code, math, reasoning, structured_output.
    """
    text = candidate.strip()
    if not text:
        return 0.0

    task = task_type.lower()

    if task == "classification":
        if reference:
            ref_clean = reference.strip().lower()
            cand_clean = text.lower()
            if ref_clean in cand_clean:
                # Bonus if concise output
                return 1.0 if len(cand_clean.split()) <= len(ref_clean.split()) + 3 else 0.8
        return 0.7 if len(text.split()) <= 5 else 0.4

    if task == "code":
        # Check balanced delimiters
        pairs = {"(": ")", "{": "}", "[": "]"}
        stack = []
        balanced = True
        for char in text:
            if char in pairs:
                stack.append(pairs[char])
            elif char in pairs.values():
                if not stack or stack.pop() != char:
                    balanced = False
                    break
        delimiters_score = 0.5 if (balanced and not stack) else 0.2

        # Check Python syntax if python code block or def/class present
        if "def " in text or "class " in text or "import " in text:
            # Extract code inside block if any
            code_body = text
            m = re.search(r"```(?:python)?\s*([\s\S]*?)\s*```", text)
            if m:
                code_body = m.group(1)
            try:
                ast.parse(code_body)
                return 1.0
            except SyntaxError:
                return delimiters_score + 0.2

        # Has code formatting or markdown backticks
        has_fences = "```" in text or "`" in text
        return delimiters_score + (0.5 if has_fences else 0.3)

    if task == "math":
        # Check for numbers / equation presence
        has_numbers = bool(re.search(r"\d+", text))
        if reference:
            ref_numbers = re.findall(r"-?\d+(?:\.\d+)?", reference)
            cand_numbers = re.findall(r"-?\d+(?:\.\d+)?", text)
            if ref_numbers and cand_numbers and ref_numbers[-1] == cand_numbers[-1]:
                return 1.0
            if any(num in cand_numbers for num in ref_numbers):
                return 0.8
        return 0.8 if has_numbers else 0.4

    if task == "reasoning":
        # Look for logical connective indicators
        indicators = ["because", "therefore", "since", "step", "thus", "hence", "first", "second", "result"]
        count = sum(1 for ind in indicators if ind in text.lower())
        return min(1.0, 0.4 + (count * 0.15))

    if task == "structured_output":
        score, _ = json_schema_validity(text)
        return score

    if task == "summarization":
        # Good length: concise but informative
        words = len(text.split())
        if 20 <= words <= 200:
            return 0.9
        if words < 20:
            return 0.5
        return 0.7

    return 0.8

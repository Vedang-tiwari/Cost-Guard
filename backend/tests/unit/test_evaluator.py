import pytest
from app.evaluation.evaluator import QualityEvaluator
from app.evaluation.quality_metrics import (
    exact_match,
    json_schema_validity,
    length_consistency,
    semantic_similarity,
    task_rubric_score,
)


def test_exact_match():
    assert exact_match("Hello World", "hello world") == 1.0
    assert exact_match("Hello World", "hello world", case_sensitive=True) == 0.0
    assert exact_match("  test  ", "test", strip_whitespace=True) == 1.0
    assert exact_match("apple", "banana") == 0.0


def test_semantic_similarity():
    sim_same = semantic_similarity("Payment processing failed with error 402", "Payment processing failed with error 402")
    assert sim_same == 1.0

    sim_related = semantic_similarity(
        "The quick brown fox jumps over the lazy dog",
        "A fast dark fox leaped above the sleepy hound",
    )
    sim_unrelated = semantic_similarity(
        "Quantum computing algorithms for prime factorization",
        "Strawberry banana smoothie recipe with almond milk",
    )
    assert sim_related > sim_unrelated


def test_json_schema_validity():
    valid_json = '{"name": "Alice", "role": "admin", "age": 30}'
    score, details = json_schema_validity(valid_json, {"required": ["name", "role"]})
    assert score == 1.0
    assert details["valid_json"] is True

    # Partial missing key
    score_partial, details_partial = json_schema_validity(valid_json, {"required": ["name", "role", "email"]})
    assert 0.6 <= score_partial <= 0.7
    assert "email" in details_partial["missing_keys"]

    # Invalid JSON
    score_inv, details_inv = json_schema_validity("Not a json at all")
    assert score_inv == 0.0
    assert details_inv["valid_json"] is False


def test_length_consistency():
    score_eq = length_consistency("hello world", "hello world")
    assert score_eq == 1.0

    score_diff = length_consistency("short", "a very very very long text spanning many sentences")
    assert score_diff < 0.2


def test_task_rubrics():
    code_pass = task_rubric_score("```python\ndef add(a, b):\n    return a + b\n```", "code")
    assert code_pass >= 0.8

    math_pass = task_rubric_score("The total is $129.60", "math", reference="$129.60")
    assert math_pass >= 0.8

    rsn_pass = task_rubric_score("Therefore, because premise A holds, we conclude B.", "reasoning")
    assert rsn_pass >= 0.6


@pytest.mark.asyncio
async def test_evaluator_methods():
    evaluator = QualityEvaluator(default_threshold=0.8)

    # Exact match
    res_em = await evaluator.evaluate(
        candidate="Negative",
        reference="Negative",
        method="exact_match",
    )
    assert res_em.passed is True
    assert res_em.score == 1.0

    # Auto classification
    res_cls = await evaluator.evaluate(
        candidate="Billing",
        expected_output="Billing",
        task_type="classification",
    )
    assert res_cls.passed is True
    assert res_cls.score == 1.0

    # Schema
    res_schema = await evaluator.evaluate(
        candidate='{"status": "ok", "code": 200}',
        expected_schema={"required": ["status", "code"]},
        method="schema",
    )
    assert res_schema.passed is True
    assert res_schema.score == 1.0

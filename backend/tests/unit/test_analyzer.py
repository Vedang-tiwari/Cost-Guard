from app.analyzer.complexity import analyze_complexity
from app.analyzer.task_classifier import classify_task
from app.analyzer.token_estimator import (
    estimate_expected_output_tokens,
    estimate_messages_tokens,
    estimate_tokens,
)
from app.schemas.request import ChatMessage


def test_estimate_tokens():
    text = "Hello world! This is a test sentence."
    tokens = estimate_tokens(text, "gpt-4o")
    assert tokens > 0
    assert estimate_tokens("") == 0


def test_estimate_messages_tokens():
    messages = [
        ChatMessage(role="system", content="You are a helpful assistant."),
        ChatMessage(role="user", content="Classify this review: Excellent service!"),
    ]
    tokens = estimate_messages_tokens(messages, "gpt-4o")
    assert tokens > 10


def test_estimate_expected_output_tokens():
    assert estimate_expected_output_tokens("classification") == 15
    assert estimate_expected_output_tokens("reasoning") == 500
    assert estimate_expected_output_tokens("custom", max_tokens=100) == 100


def test_task_classification():
    # Classification
    res = classify_task("Classify the following customer feedback as positive or negative")
    assert res.task_type == "classification"

    # Summarization
    res = classify_task("Summarize this article in 3 sentences: TLDR")
    assert res.task_type == "summarization"

    # Extraction
    res = classify_task("Extract the invoice number and due date as JSON from this text")
    assert res.task_type == "extraction"

    # Code
    res = classify_task("Write a python function to compute fibonacci numbers")
    assert res.task_type == "code"

    # Math
    res = classify_task("Calculate the derivative of x^2 + 5x = 0")
    assert res.task_type == "math"

    # Reasoning
    res = classify_task("Analyze the geopolitical implications and compare trade-offs step by step")
    assert res.task_type == "reasoning"


def test_complexity_scoring_low():
    messages = [
        ChatMessage(role="user", content="Classify sentiment: Great app!"),
    ]
    result = analyze_complexity(messages)
    assert result.tier == "low"
    assert result.score <= 30.0


def test_complexity_scoring_high():
    long_prompt = (
        "Analyze the following financial report. Evaluate trade-offs step by step. "
        "Strictly adhere to the following constraints: "
        "1. Identify all balance sheet inconsistencies. "
        "2. Explain why each discrepancy matters. "
        "3. Provide implications of inflation on cash reserves. "
        "Format output only in JSON with fields: discrepancies, analysis, risks."
    )
    messages = [
        ChatMessage(role="user", content=long_prompt),
    ]
    result = analyze_complexity(messages)
    assert result.tier in ("medium", "high")
    assert result.score > 30.0

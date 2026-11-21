from app.optimization.prompt_optimizer import optimize_prompt
from app.schemas.request import ChatMessage


def test_prompt_optimization_whitespace():
    messages = [
        ChatMessage(role="user", content="  What   is   machine    learning?   \n\n\n\nExplain it.  ")
    ]
    res = optimize_prompt(messages, enabled=True)
    assert res.tokens_saved >= 0
    assert "whitespace_normalization" in res.methods_applied
    assert res.optimized_messages[0].content == "What is machine learning?\n\nExplain it."


def test_prompt_optimization_filler_removal():
    messages = [
        ChatMessage(role="user", content="Please answer the following question: What is Python?")
    ]
    res = optimize_prompt(messages, enabled=True)
    assert "filler_removal" in res.methods_applied
    assert res.optimized_messages[0].content == "What is Python?"


def test_prompt_optimization_disabled():
    original = "   Hello    world   "
    messages = [ChatMessage(role="user", content=original)]
    res = optimize_prompt(messages, enabled=False)
    assert res.tokens_saved == 0
    assert res.optimized_messages[0].content == original

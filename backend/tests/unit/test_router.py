from app.router.fallback import get_fallback_model
from app.router.model_router import ModelRouter, RoutingInput


def test_explicit_routing():
    router = ModelRouter()
    decision = router.route(
        RoutingInput(
            requested_model="claude-3-5-sonnet-20241022",
            task_type="conversational",
            complexity_score=10.0,
        )
    )
    assert decision.selected_model == "claude-3-5-sonnet-20241022"
    assert decision.provider == "anthropic"
    assert decision.routing_strategy == "explicit"
    assert decision.fallback_required is False


def test_complexity_routing_low():
    router = ModelRouter()
    decision = router.route(
        RoutingInput(
            requested_model="auto",
            task_type="classification",
            complexity_score=15.0,
            strategy="complexity_based",
        )
    )
    # Low complexity should select an economical model
    assert decision.selected_model in ("gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022", "llama3.2")
    assert decision.routing_strategy == "complexity_based"
    assert "Low complexity" in decision.reason


def test_complexity_routing_high():
    router = ModelRouter()
    decision = router.route(
        RoutingInput(
            requested_model="auto",
            task_type="reasoning",
            complexity_score=85.0,
            strategy="complexity_based",
        )
    )
    # High complexity should select a capable model
    assert decision.selected_model in ("gpt-4o", "gemini-1.5-pro", "claude-3-5-sonnet-20241022")
    assert "High complexity" in decision.reason


def test_rule_based_routing():
    router = ModelRouter()
    decision = router.route(
        RoutingInput(
            requested_model="auto",
            task_type="classification",
            strategy="rule_based",
        )
    )
    assert decision.routing_strategy == "rule_based"
    assert decision.selected_model in ("gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022", "llama3.2")


def test_fallback_chain():
    assert get_fallback_model("gpt-4o-mini") == "gpt-4o"
    assert get_fallback_model("gemini-1.5-flash") == "gemini-1.5-pro"
    assert get_fallback_model("llama3.2") == "gpt-4o-mini"

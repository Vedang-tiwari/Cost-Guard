
from app.cost.calculator import estimate_model_cost
from app.cost.pricing_registry import get_model_pricing
from app.providers.factory import get_provider_factory
from app.router.routing_rules import TASK_TIER_RULES, TIER_PREFERRED_MODELS, ComplexityTier
from pydantic import BaseModel, Field


class RoutingInput(BaseModel):
    task_type: str = "conversational"
    complexity_score: float = 0.0
    estimated_input_tokens: int = 100
    expected_output_tokens: int = 100
    quality_requirement: float = 0.90
    requested_model: str = "auto"
    strategy: str = "complexity_based"  # complexity_based, rule_based, cost_based


class RoutingDecision(BaseModel):
    selected_model: str = Field(..., description="Selected model name")
    provider: str = Field(..., description="Provider hosting the selected model")
    estimated_cost: float = Field(..., description="Calculated estimated cost")
    complexity_score: float = Field(..., description="Complexity score (0-100)")
    routing_strategy: str = Field(..., description="Routing strategy applied")
    reason: str = Field(..., description="Explainable reason for selection")
    fallback_required: bool = Field(default=False, description="Whether fallback model was invoked")


class ModelRouter:
    """
    Intelligent Model Router evaluating complexity, task category,
    context limits, and pricing to pick the most cost-effective eligible model.
    """

    def __init__(self):
        self.provider_factory = get_provider_factory()

    def route(self, routing_input: RoutingInput) -> RoutingDecision:
        # Case 1: Explicit model request
        if routing_input.requested_model != "auto":
            model = routing_input.requested_model
            provider_name, _ = self.provider_factory.resolve_provider_for_model(model)
            cost = estimate_model_cost(
                model_name=model,
                input_tokens=routing_input.estimated_input_tokens,
                expected_output_tokens=routing_input.expected_output_tokens,
            )
            return RoutingDecision(
                selected_model=model,
                provider=provider_name,
                estimated_cost=cost,
                complexity_score=routing_input.complexity_score,
                routing_strategy="explicit",
                reason=f"Explicitly requested model '{model}'",
                fallback_required=False,
            )

        # Case 2: Rule-Based Routing
        if routing_input.strategy == "rule_based":
            tier: ComplexityTier = TASK_TIER_RULES.get(routing_input.task_type, "low")
            reason = f"Rule-based routing for task '{routing_input.task_type}' targeting tier '{tier}'"
            return self._select_best_model_for_tier(tier, routing_input, reason, "rule_based")

        # Case 3: Complexity-Based Routing (Default)
        score = routing_input.complexity_score
        if score <= 30.0:
            target_tier: ComplexityTier = "low"
            reason = f"Low complexity score ({score}/100) routed to economical model"
        elif score <= 65.0:
            target_tier = "medium"
            reason = f"Moderate complexity score ({score}/100) routed to balanced model"
        else:
            target_tier = "high"
            reason = f"High complexity score ({score}/100) routed to premium reasoning model"

        return self._select_best_model_for_tier(target_tier, routing_input, reason, "complexity_based")

    def _select_best_model_for_tier(
        self,
        tier: ComplexityTier,
        routing_input: RoutingInput,
        reason: str,
        strategy: str,
    ) -> RoutingDecision:
        candidate_models = TIER_PREFERRED_MODELS.get(tier, TIER_PREFERRED_MODELS["low"])
        total_tokens = routing_input.estimated_input_tokens + routing_input.expected_output_tokens

        eligible: list[tuple[str, str, float]] = []  # (model_name, provider, cost)

        for model in candidate_models:
            pricing = get_model_pricing(model)
            # Filter by context window
            if pricing.context_window < total_tokens:
                continue

            provider_name, _ = self.provider_factory.resolve_provider_for_model(model)
            # Exclude local models (ollama) from automatic routing unless explicitly requested
            # to guarantee reliable cloud provider execution
            if provider_name == "ollama":
                continue

            cost = estimate_model_cost(
                model_name=model,
                input_tokens=routing_input.estimated_input_tokens,
                expected_output_tokens=routing_input.expected_output_tokens,
            )
            eligible.append((model, provider_name, cost))

        if not eligible:
            # Fallback to standard safe default
            fallback = "gpt-4o"
            p_name, _ = self.provider_factory.resolve_provider_for_model(fallback)
            cost = estimate_model_cost(fallback, routing_input.estimated_input_tokens, routing_input.expected_output_tokens)
            return RoutingDecision(
                selected_model=fallback,
                provider=p_name,
                estimated_cost=cost,
                complexity_score=routing_input.complexity_score,
                routing_strategy=strategy,
                reason=f"{reason} (Fallback to '{fallback}' due to context length)",
                fallback_required=True,
            )

        # Select the lowest-cost eligible model
        eligible.sort(key=lambda x: x[2])
        best_model, best_provider, best_cost = eligible[0]

        return RoutingDecision(
            selected_model=best_model,
            provider=best_provider,
            estimated_cost=best_cost,
            complexity_score=routing_input.complexity_score,
            routing_strategy=strategy,
            reason=reason,
            fallback_required=False,
        )


_router_instance: ModelRouter | None = None


def get_model_router() -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter()
    return _router_instance

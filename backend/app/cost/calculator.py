from app.cost.pricing_registry import BASELINE_MODEL, CATALOG, get_model_pricing


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    input_price_per_million: float,
    output_price_per_million: float,
) -> float:
    """
    Computes dollar cost from token counts and price per million tokens.
    Formula: (Input / 1,000,000 * InPrice) + (Output / 1,000,000 * OutPrice)
    """
    in_cost = (input_tokens / 1_000_000) * input_price_per_million
    out_cost = (output_tokens / 1_000_000) * output_price_per_million
    return round(in_cost + out_cost, 6)


def estimate_model_cost(model_name: str, input_tokens: int, expected_output_tokens: int) -> float:
    """Calculates estimated cost for a given model and token counts."""
    pricing = get_model_pricing(model_name)
    return calculate_cost(
        input_tokens=input_tokens,
        output_tokens=expected_output_tokens,
        input_price_per_million=pricing.input_price_per_million,
        output_price_per_million=pricing.output_price_per_million,
    )


def calculate_savings(actual_cost: float, baseline_cost: float) -> tuple[float, float]:
    """
    Computes absolute savings and percentage savings against baseline cost.
    Returns: (savings_dollar, savings_percentage)
    """
    savings = round(max(0.0, baseline_cost - actual_cost), 6)
    if baseline_cost > 0.0:
        savings_percentage = round((savings / baseline_cost) * 100.0, 2)
    else:
        savings_percentage = 0.0
    return savings, savings_percentage


def calculate_baseline_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculates baseline cost using the reference standard (gpt-4o)."""
    baseline_pricing = CATALOG[BASELINE_MODEL]
    return calculate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        input_price_per_million=baseline_pricing.input_price_per_million,
        output_price_per_million=baseline_pricing.output_price_per_million,
    )

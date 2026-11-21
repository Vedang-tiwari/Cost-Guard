
from app.analyzer.token_estimator import estimate_expected_output_tokens


def optimize_token_limits(task_type: str, requested_max_tokens: int | None = None) -> int:
    """
    Enforces sensible maximum output tokens when omitted by client,
    preventing open-ended runaway output costs.
    """
    return estimate_expected_output_tokens(task_type, requested_max_tokens)

from app.cost.calculator import (
    calculate_baseline_cost,
    calculate_cost,
    calculate_savings,
)


def test_calculate_cost():
    # 1,000,000 input tokens at $2.50 + 1,000,000 output tokens at $10.00 = $12.50
    cost = calculate_cost(1_000_000, 1_000_000, 2.50, 10.00)
    assert cost == 12.50

    # 10,000 in, 5,000 out
    cost_small = calculate_cost(10_000, 5_000, 0.15, 0.60)
    assert cost_small == 0.0045


def test_calculate_savings():
    baseline = 0.0100
    actual = 0.0025
    savings, pct = calculate_savings(actual, baseline)
    assert savings == 0.0075
    assert pct == 75.0


def test_calculate_baseline_cost():
    # Baseline gpt-4o price is 2.50 in, 10.00 out
    cost = calculate_baseline_cost(1_000, 1_000)
    assert cost == 0.0125

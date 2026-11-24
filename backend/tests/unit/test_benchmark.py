from pathlib import Path

import pytest
from app.evaluation.benchmark import BenchmarkItem, BenchmarkSuite


@pytest.mark.asyncio
async def test_benchmark_suite_execution():
    suite = BenchmarkSuite()
    items = [
        BenchmarkItem(
            id="t1",
            category="classification",
            prompt="Classify sentiment: great phone",
            expected_output="Positive",
            task_type="classification",
        ),
        BenchmarkItem(
            id="t2",
            category="code",
            prompt="Write a python function that adds two numbers",
            expected_output="```python\ndef add(a, b):\n    return a + b\n```",
            task_type="code",
        ),
    ]

    summary = await suite.run_benchmark(
        items=items,
        candidate_model="gpt-4o-mini",
        reference_model="gpt-4o",
    )

    assert summary.total_cases == 2
    assert summary.overall_quality_score >= 0.8
    assert summary.cost_savings_pct > 80.0

    report = suite.generate_markdown_report(summary)
    assert "# Benchmark Report" in report
    assert "gpt-4o-mini" in report
    assert "Classification" in report


def test_benchmark_dataset_file():
    suite = BenchmarkSuite()
    dataset_path = Path(__file__).resolve().parent.parent.parent.parent / "benchmarks" / "datasets" / "test_prompts.json"
    items = suite.load_dataset(dataset_path)
    assert len(items) >= 10
    categories = {it.category for it in items}
    assert "classification" in categories
    assert "code" in categories
    assert "math" in categories
    assert "reasoning" in categories
    assert "structured_output" in categories

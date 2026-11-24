import asyncio
import sys
from pathlib import Path

# Add backend directory to PYTHONPATH
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))

from app.evaluation.benchmark import BenchmarkSuite  # noqa: E402


async def main() -> None:
    print("=" * 70)
    print("  Cost Guard Benchmark Suite — Quality & Cost Evaluation")
    print("=" * 70)

    dataset_path = root_dir / "benchmarks" / "datasets" / "test_prompts.json"
    if not dataset_path.exists():
        print(f"Error: dataset not found at {dataset_path}")
        sys.exit(1)

    suite = BenchmarkSuite()
    items = suite.load_dataset(dataset_path)
    print(f"Loaded {len(items)} benchmark test cases across categories.")

    models_to_test = ["gpt-4o-mini", "gemini-1.5-flash", "claude-3-5-haiku-20241022"]
    reference_model = "gpt-4o"

    all_reports = []

    for candidate in models_to_test:
        print(f"\nRunning benchmark: Candidate `{candidate}` vs Baseline `{reference_model}`...")
        summary = await suite.run_benchmark(
            items=items,
            candidate_model=candidate,
            reference_model=reference_model,
        )

        md = suite.generate_markdown_report(summary)
        print(md)
        all_reports.append(md)

    # Save to benchmarks/BENCHMARK_RESULTS.md
    output_path = root_dir / "benchmarks" / "BENCHMARK_RESULTS.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Cost Guard Comprehensive Benchmark Results\n\n")
        f.write("\n\n---\n\n".join(all_reports))
        f.write("\n")

    print(f"\nSaved benchmark results to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

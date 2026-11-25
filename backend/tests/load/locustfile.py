"""
Load testing script for Cost Guard API Gateway.

Usage:
    pip install locust
    locust -f backend/tests/load/locustfile.py --host=http://localhost:8000
"""
import os

try:
    from locust import HttpUser, between, task
except ImportError:
    HttpUser = object  # type: ignore[misc, assignment]
    between = lambda *args, **kwargs: None  # noqa: E731
    task = lambda fn: fn  # noqa: E731


API_KEY = os.getenv("COSTGUARD_TEST_API_KEY", "cg_test_1234567890abcdef")


class CostGuardGatewayUser(HttpUser):
    wait_time = between(0.5, 2.0)

    def on_start(self) -> None:
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json",
        }

    @task(2)
    def health_check(self) -> None:
        self.client.get("/health")

    @task(3)
    def analytics_overview(self) -> None:
        self.client.get("/api/v1/analytics/overview", headers=self.headers)

    @task(5)
    def playground_simulation(self) -> None:
        self.client.post(
            "/api/v1/playground/compare",
            headers=self.headers,
            json={
                "prompt": "Summarize the benefits of vector caching for LLM gateways.",
                "fixed_model": "gpt-4o",
                "execution_mode": "simulate",
            },
        )

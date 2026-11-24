import pytest
from app.database.models.application import Application
from app.database.models.budget import Budget
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_budgets_crud_api(
    client: AsyncClient,
    test_app_and_org: tuple[Application, str],
):
    app, api_key = test_app_and_org
    headers = {"X-API-Key": api_key}

    # 1. Create budget
    create_resp = await client.post(
        "/api/v1/budgets",
        headers=headers,
        json={
            "organization_id": app.organization_id,
            "budget_type": "organization",
            "limit_amount": 50.0,
            "warning_threshold": 0.8,
            "hard_limit": True,
            "period": "monthly",
        },
    )
    assert create_resp.status_code == 201
    budget_data = create_resp.json()
    budget_id = budget_data["id"]
    assert budget_data["limit_amount"] == 50.0
    assert budget_data["remaining_amount"] == 50.0

    # 2. List budgets
    list_resp = await client.get("/api/v1/budgets", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1

    # 3. Get single budget
    get_resp = await client.get(f"/api/v1/budgets/{budget_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == budget_id

    # 4. Patch budget
    patch_resp = await client.patch(
        f"/api/v1/budgets/{budget_id}",
        headers=headers,
        json={"limit_amount": 75.0, "warning_threshold": 0.85},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["limit_amount"] == 75.0
    assert patch_resp.json()["warning_threshold"] == 0.85


@pytest.mark.asyncio
async def test_evaluations_api(
    client: AsyncClient,
    test_app_and_org: tuple[Application, str],
):
    app, api_key = test_app_and_org
    headers = {"X-API-Key": api_key}

    # Run evaluation
    eval_resp = await client.post(
        "/api/v1/evaluations/run",
        headers=headers,
        json={
            "candidate_response": "Billing",
            "expected_output": "Billing",
            "task_type": "classification",
            "method": "auto",
        },
    )
    assert eval_resp.status_code == 200
    data = eval_resp.json()
    assert data["quality_score"] == 1.0
    assert data["passed"] is True

    # List evaluations
    list_resp = await client.get("/api/v1/evaluations", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.asyncio
async def test_analytics_endpoints(
    client: AsyncClient,
    test_app_and_org: tuple[Application, str],
):
    app, api_key = test_app_and_org
    headers = {"X-API-Key": api_key}

    overview_resp = await client.get("/api/v1/analytics/overview", headers=headers)
    assert overview_resp.status_code == 200
    assert "total_requests" in overview_resp.json()

    costs_resp = await client.get("/api/v1/analytics/costs", headers=headers)
    assert costs_resp.status_code == 200
    assert "breakdown" in costs_resp.json()

    models_resp = await client.get("/api/v1/analytics/models", headers=headers)
    assert models_resp.status_code == 200
    assert "models" in models_resp.json()

    savings_resp = await client.get("/api/v1/analytics/savings", headers=headers)
    assert savings_resp.status_code == 200
    assert "sources" in savings_resp.json()


@pytest.mark.asyncio
async def test_prometheus_metrics_endpoint(client: AsyncClient):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    text = resp.text
    assert "costguard_requests_total" in text
    assert "costguard_cost_dollars_total" in text


@pytest.mark.asyncio
async def test_gateway_budget_hard_limit_block(
    client: AsyncClient,
    test_app_and_org: tuple[Application, str],
    db_session: AsyncSession,
):
    app, api_key = test_app_and_org
    headers = {"X-API-Key": api_key}

    # Add an exceeded budget with hard_limit = True
    budget = Budget(
        organization_id=app.organization_id,
        application_id=app.id,
        budget_type="organization",
        limit_amount=0.01,
        current_spend=0.015,
        hard_limit=True,
        status="active",
    )
    db_session.add(budget)
    await db_session.commit()

    # Chat request should be rejected with 429 Too Many Requests / Budget Exceeded
    resp = await client.post(
        "/api/v1/chat/completions",
        headers=headers,
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": "Hello, how are you today?"}],
        },
    )
    assert resp.status_code == 429
    assert "Budget limit" in resp.json()["detail"]

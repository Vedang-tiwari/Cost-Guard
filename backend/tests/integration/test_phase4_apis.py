import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_register_login_and_me(client: AsyncClient):
    # 1. Register new developer user + org + default API key
    reg_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "StrongPassword123!",
            "full_name": "Alice Developer",
            "organization_name": "Acme AI Labs",
        },
    )
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["access_token"]
    assert reg_data["default_api_key"].startswith("cg_live_")
    assert reg_data["user"]["email"] == "alice@example.com"
    assert reg_data["user"]["organization_name"] == "Acme AI Labs"

    # 2. Duplicate registration rejected with 409
    dup_resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "StrongPassword123!",
            "full_name": "Alice Developer",
            "organization_name": "Acme AI Labs",
        },
    )
    assert dup_resp.status_code == 409

    # 3. Login with wrong password -> 401
    bad_login = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401

    # 4. Login with valid credentials -> JWT
    login_resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "alice@example.com", "password": "StrongPassword123!"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 5. Fetch /me profile
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "alice@example.com"

    # 6. Access dashboard endpoints seamlessly with JWT Bearer token
    apps_resp = await client.get("/api/v1/applications", headers=headers)
    assert apps_resp.status_code == 200
    assert len(apps_resp.json()) == 1
    assert apps_resp.json()[0]["name"] == "Default Gateway App"


@pytest.mark.asyncio
async def test_applications_crud_and_revoke(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    # Create second application
    create_resp = await client.post(
        "/api/v1/applications",
        headers=headers,
        json={"name": "Production Support Bot"},
    )
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "Production Support Bot"
    assert created["api_key"].startswith("cg_live_")
    assert created["status"] == "active"

    # List applications
    list_resp = await client.get("/api/v1/applications", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 2

    # Revoke new application
    del_resp = await client.delete(f"/api/v1/applications/{created['id']}", headers=headers)
    assert del_resp.status_code == 204

    # Verify revoked key fails authentication
    fail_resp = await client.get("/api/v1/budgets", headers={"X-API-Key": created["api_key"]})
    assert fail_resp.status_code == 401


@pytest.mark.asyncio
async def test_optimization_policy_persistence(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    get_resp = await client.get("/api/v1/policies", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["routing_strategy"] == "complexity_based"

    put_resp = await client.put(
        "/api/v1/policies",
        headers=headers,
        json={
            "routing_strategy": "rule_based",
            "minimum_quality_score": 0.92,
            "cache_similarity_threshold": 0.91,
            "max_output_tokens": 2048,
        },
    )
    assert put_resp.status_code == 200
    updated = put_resp.json()
    assert updated["routing_strategy"] == "rule_based"
    assert updated["minimum_quality_score"] == 0.92
    assert updated["cache_similarity_threshold"] == 0.91
    assert updated["max_output_tokens"] == 2048


@pytest.mark.asyncio
async def test_benchmarks_endpoints(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    # Auto-runs defaults if empty
    res_get = await client.get("/api/v1/benchmarks/results", headers=headers)
    assert res_get.status_code == 200
    runs = res_get.json()
    assert len(runs) >= 3
    assert any(r["candidate_model"] == "gpt-4o-mini" and r["cost_savings_pct"] > 80.0 for r in runs)

    # Trigger custom benchmark run
    res_post = await client.post(
        "/api/v1/benchmarks/run",
        headers=headers,
        json={"candidate_models": ["gemini-1.5-flash"], "reference_model": "gpt-4o"},
    )
    assert res_post.status_code == 201
    assert res_post.json()[0]["candidate_model"] == "gemini-1.5-flash"


@pytest.mark.asyncio
async def test_playground_compare_simulation(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    resp = await client.post(
        "/api/v1/playground/compare",
        headers=headers,
        json={
            "prompt": "Please classify this customer review as Positive or Negative: Fast delivery and great quality!",
            "fixed_model": "gpt-4o",
            "semantic_cache": True,
            "prompt_optimization": True,
            "intelligent_routing": True,
            "execution_mode": "simulate",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["execution_mode"] == "simulate"
    assert data["fixed"]["model"] == "gpt-4o"
    assert data["optimized"]["model"] != "gpt-4o"
    assert data["optimized"]["cost"] < data["fixed"]["cost"]
    assert data["optimized"]["savings_percentage"] > 70.0


@pytest.mark.asyncio
async def test_models_status_and_patch(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    status_resp = await client.get("/api/v1/models/providers/status")
    assert status_resp.status_code == 200
    providers = [p["provider"] for p in status_resp.json()]
    assert "openai" in providers
    assert "anthropic" in providers
    assert "gemini" in providers

    patch_resp = await client.patch(
        "/api/v1/models/gpt-4o-mini",
        headers=headers,
        json={"input_price_per_million": 0.14, "pricing_version": "2026-11"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["input_price_per_million"] == 0.14
    assert patch_resp.json()["pricing_version"] == "2026-11"


@pytest.mark.asyncio
async def test_analytics_logs_and_breakdowns(client: AsyncClient, test_app_and_org):
    _app, raw_key = test_app_and_org
    headers = {"X-API-Key": raw_key}

    costs_resp = await client.get("/api/v1/analytics/costs?period=weekly", headers=headers)
    assert costs_resp.status_code == 200
    c_data = costs_resp.json()
    assert "by_provider" in c_data
    assert "by_model" in c_data
    assert "token_costs" in c_data

    logs_resp = await client.get("/api/v1/analytics/logs?limit=20", headers=headers)
    assert logs_resp.status_code == 200
    assert isinstance(logs_resp.json(), list)

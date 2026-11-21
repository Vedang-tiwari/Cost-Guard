import os
import sys
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import app.database.models  # Register all models with Base.metadata
from app.core.security import hash_api_key
from app.database.base import Base
from app.database.models.application import Application
from app.database.models.model import ModelRegistry
from app.database.models.organization import Organization
from app.database.session import get_db
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_maker() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_app_and_org(db_session: AsyncSession) -> tuple[Application, str]:
    """Creates a test organization, application, and returns (application, raw_api_key)."""
    org = Organization(id="org_test_123", name="Test Org")
    db_session.add(org)

    raw_api_key = "cg_live_testkey1234567890abcdef"
    test_application = Application(
        id="app_test_123",
        organization_id=org.id,
        name="Test Application",
        api_key_hash=hash_api_key(raw_api_key),
        status="active",
    )
    db_session.add(test_application)

    model = ModelRegistry(
        id="model_test_gpt4o",
        provider="openai",
        model_name="gpt-4o",
        input_price_per_million=2.50,
        output_price_per_million=10.00,
        capabilities={"chat": True},
        context_window=128000,
        is_active=True,
        pricing_version="1.0.0",
    )
    db_session.add(model)
    await db_session.commit()

    return test_application, raw_api_key


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client with overridden database dependency."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()

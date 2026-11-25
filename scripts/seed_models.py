import asyncio
import os
import sys
import uuid

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.api.routes.models import DEFAULT_MODELS
from app.core.security import hash_api_key, hash_password
from app.database.models.application import Application
from app.database.models.budget import Budget
from app.database.models.model import ModelRegistry
from app.database.models.organization import Organization
from app.database.models.policy import OptimizationPolicy
from app.database.models.user import User
from app.database.session import AsyncSessionLocal
from sqlalchemy import select


async def seed():
    print("Seeding initial models, organization, demo user, and default application...")
    async with AsyncSessionLocal() as session:
        # Seed Organization
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name="Cost Guard Demo Org",
            )
            session.add(org)
            await session.flush()
            print(f"Created organization: {org.name} ({org.id})")

        # Seed Demo Dashboard User
        user_result = await session.execute(select(User).where(User.email == "demo@costguard.ai"))
        user = user_result.scalar_one_or_none()
        if not user:
            user = User(
                id=str(uuid.uuid4()),
                email="demo@costguard.ai",
                password_hash=hash_password("CostGuard2026!"),
                full_name="Demo Developer",
                organization_id=org.id,
            )
            session.add(user)
            print("Created demo dashboard user: demo@costguard.ai / CostGuard2026!")

        # Seed Demo Application & API Key
        app_result = await session.execute(select(Application).where(Application.organization_id == org.id).limit(1))
        app_record = app_result.scalar_one_or_none()
        raw_key = "cg_test_1234567890abcdef"
        if not app_record:
            app_record = Application(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                name="Demo Application",
                api_key_hash=hash_api_key(raw_key),
                key_prefix=raw_key[:14] + "...",
                status="active",
            )
            session.add(app_record)
            print(f"Created demo application with API Key: {raw_key}")

        # Seed Default Optimization Policy
        pol_result = await session.execute(select(OptimizationPolicy).where(OptimizationPolicy.organization_id == org.id))
        if not pol_result.scalar_one_or_none():
            session.add(OptimizationPolicy(id=str(uuid.uuid4()), organization_id=org.id))
            print("Created default optimization policy")

        # Seed Starter Budget
        b_result = await session.execute(select(Budget).where(Budget.organization_id == org.id).limit(1))
        if not b_result.scalar_one_or_none():
            session.add(
                Budget(
                    id=str(uuid.uuid4()),
                    organization_id=org.id,
                    budget_type="organization",
                    limit_amount=250.0,
                    warning_threshold=0.8,
                    hard_limit=True,
                    period="monthly",
                )
            )
            print("Created default $250/month organization budget")

        # Seed Models
        for m_data in DEFAULT_MODELS:
            existing = await session.execute(
                select(ModelRegistry).where(ModelRegistry.model_name == m_data["model_name"])
            )
            if not existing.scalar_one_or_none():
                model = ModelRegistry(**m_data)
                session.add(model)
                print(f"Registered model: {m_data['model_name']} ({m_data['provider']})")

        await session.commit()
        print("Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())

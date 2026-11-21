import asyncio
import uuid
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from sqlalchemy import select
from app.database.session import AsyncSessionLocal
from app.database.models.organization import Organization
from app.database.models.application import Application
from app.database.models.model import ModelRegistry
from app.core.security import hash_api_key
from app.api.routes.models import DEFAULT_MODELS


async def seed():
    print("🌱 Seeding initial models and default application...")
    async with AsyncSessionLocal() as session:
        # Seed Organization
        org_result = await session.execute(select(Organization).limit(1))
        org = org_result.scalar_one_or_none()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name="Cost Guard Demo Org"
            )
            session.add(org)
            await session.flush()
            print(f"Created organization: {org.name} ({org.id})")

        # Seed Demo Application & API Key
        app_result = await session.execute(select(Application).limit(1))
        app_record = app_result.scalar_one_or_none()
        raw_key = "cg_test_1234567890abcdef"
        if not app_record:
            app_record = Application(
                id=str(uuid.uuid4()),
                organization_id=org.id,
                name="Demo Application",
                api_key_hash=hash_api_key(raw_key),
                status="active"
            )
            session.add(app_record)
            print(f"Created demo application with API Key: {raw_key}")

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
        print("✅ Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())


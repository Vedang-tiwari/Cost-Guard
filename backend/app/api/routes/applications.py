import uuid

from app.api.dependencies import verify_application_api_key
from app.core.security import generate_api_key
from app.database.models.application import Application
from app.database.session import get_db
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationCreateResponse,
    ApplicationResponse,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/applications", tags=["Applications & API Keys"])


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    current_app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> list[ApplicationResponse]:
    """Lists all active applications registered under the organization."""
    stmt = (
        select(Application)
        .where(Application.organization_id == current_app.organization_id)
        .order_by(Application.created_at.desc())
    )
    res = await db.execute(stmt)
    apps = res.scalars().all()
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.post("", response_model=ApplicationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreateRequest,
    current_app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> ApplicationCreateResponse:
    """Creates a new application and generates a fresh SHA-256 hashed API key."""
    raw_key, hashed_key = generate_api_key("cg_live_")
    new_app = Application(
        id=str(uuid.uuid4()),
        organization_id=current_app.organization_id,
        name=payload.name,
        api_key_hash=hashed_key,
        key_prefix=raw_key[:14] + "...",
        status="active",
    )
    db.add(new_app)
    await db.commit()
    await db.refresh(new_app)

    return ApplicationCreateResponse(
        id=new_app.id,
        organization_id=new_app.organization_id,
        name=new_app.name,
        key_prefix=new_app.key_prefix,
        status=new_app.status,
        created_at=new_app.created_at,
        api_key=raw_key,
    )


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_application(
    application_id: str,
    current_app: Application = Depends(verify_application_api_key),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Deactivates/revokes an application API key within the organization."""
    stmt = select(Application).where(
        Application.id == application_id,
        Application.organization_id == current_app.organization_id,
    )
    res = await db.execute(stmt)
    target = res.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

    if target.id == current_app.id:
        # Still allow revoking other apps cleanly; mark target revoked
        target.status = "revoked"
    else:
        target.status = "revoked"

    await db.commit()

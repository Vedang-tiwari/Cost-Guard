import uuid

from app.api.dependencies import verify_dashboard_user
from app.core.exceptions import AuthenticationError, CostGuardException
from app.core.security import (
    create_access_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.database.models.application import Application
from app.database.models.organization import Organization
from app.database.models.policy import OptimizationPolicy
from app.database.models.user import User
from app.database.session import get_db
from app.schemas.auth import (
    AuthTokenResponse,
    UserLoginRequest,
    UserProfile,
    UserRegisterRequest,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthTokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    """Registers a new user, provisions an organization, default optimization policy, and initial API key."""
    existing = await db.execute(select(User).where(User.email == payload.email.lower()))
    if existing.scalar_one_or_none():
        raise CostGuardException(
            message="An account with this email already exists",
            status_code=status.HTTP_409_CONFLICT,
        )

    org = Organization(
        id=str(uuid.uuid4()),
        name=payload.organization_name,
    )
    db.add(org)
    await db.flush()

    user = User(
        id=str(uuid.uuid4()),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        organization_id=org.id,
    )
    db.add(user)

    raw_key, hashed_key = generate_api_key("cg_live_")
    default_app = Application(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        name="Default Gateway App",
        api_key_hash=hashed_key,
        key_prefix=raw_key[:14] + "...",
        status="active",
    )
    db.add(default_app)

    default_policy = OptimizationPolicy(
        id=str(uuid.uuid4()),
        organization_id=org.id,
    )
    db.add(default_policy)

    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": user.id, "email": user.email, "org_id": org.id})

    return AuthTokenResponse(
        access_token=token,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization_id=org.id,
            organization_name=org.name,
            created_at=user.created_at,
        ),
        default_api_key=raw_key,
    )


@router.post("/login", response_model=AuthTokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthTokenResponse:
    """Authenticates a user with email and password and issues a JWT session token."""
    result = await db.execute(select(User).where(User.email == payload.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    org_name: str | None = None
    if user.organization_id:
        org_res = await db.execute(select(Organization).where(Organization.id == user.organization_id))
        org = org_res.scalar_one_or_none()
        org_name = org.name if org else None

    token = create_access_token({"sub": user.id, "email": user.email, "org_id": user.organization_id})

    return AuthTokenResponse(
        access_token=token,
        user=UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            organization_id=user.organization_id,
            organization_name=org_name,
            created_at=user.created_at,
        ),
    )


@router.get("/me", response_model=UserProfile)
async def get_current_user(
    user: User = Depends(verify_dashboard_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    """Returns profile details for the authenticated dashboard user."""
    org_name: str | None = None
    if user.organization_id:
        org_res = await db.execute(select(Organization).where(Organization.id == user.organization_id))
        org = org_res.scalar_one_or_none()
        org_name = org.name if org else None

    return UserProfile(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        organization_id=user.organization_id,
        organization_name=org_name,
        created_at=user.created_at,
    )

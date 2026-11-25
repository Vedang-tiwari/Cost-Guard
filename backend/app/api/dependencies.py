from app.core.exceptions import AuthenticationError, InvalidAPIKeyError
from app.core.security import decode_access_token, hash_api_key
from app.database.models.application import Application
from app.database.models.user import User
from app.database.session import get_db
from fastapi import Depends, Header, Security
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key_from_headers(
    x_api_key: str | None = Security(api_key_header),
    authorization: str | None = Header(None),
) -> str | None:
    """Extracts API key or Bearer token from headers."""
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


async def verify_dashboard_user(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validates a Dashboard JWT Bearer token and returns the User."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("Dashboard session token required")

    token = authorization[7:].strip()
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid session token subject")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise AuthenticationError("Authenticated user account no longer exists")
    return user


async def verify_application_api_key(
    api_key: str | None = Security(api_key_header),
    authorization: str | None = Header(None),
    x_application_id: str | None = Header(None, alias="X-Application-Id"),
    db: AsyncSession = Depends(get_db),
) -> Application:
    """
    Validates authentication via either:
    1) Application API Key ('X-API-Key' or 'Authorization: Bearer cg_...')
    2) Dashboard Session JWT ('Authorization: Bearer <jwt>'), resolving an active Application in the user's org.
    """
    # 1. Explicit X-API-Key header always takes precedence as an API key
    token: str | None = api_key
    is_bearer = False
    if not token and authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        is_bearer = True

    if not token:
        raise AuthenticationError("API key must be provided via 'X-API-Key' or 'Authorization: Bearer <key>'")

    # 2. If Bearer token looks like a JWT (3 dot-separated parts and not starting with 'cg_')
    if is_bearer and token.count(".") == 2 and not token.startswith("cg_"):
        payload = decode_access_token(token)
        org_id = payload.get("org_id")
        user_id = payload.get("sub")
        if not org_id and user_id:
            u_res = await db.execute(select(User).where(User.id == user_id))
            user = u_res.scalar_one_or_none()
            org_id = user.organization_id if user else None

        if not org_id:
            raise AuthenticationError("No organization associated with dashboard session")

        app_query = select(Application).where(
            Application.organization_id == org_id,
            Application.status == "active",
        )
        if x_application_id:
            app_query = app_query.where(Application.id == x_application_id)

        app_res = await db.execute(app_query.limit(1))
        application = app_res.scalar_one_or_none()
        if not application:
            raise InvalidAPIKeyError("No active application found for this organization")
        return application

    # 3. Standard API Key SHA-256 verification
    hashed_key = hash_api_key(token)
    query = select(Application).where(
        Application.api_key_hash == hashed_key,
        Application.status == "active",
    )
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise InvalidAPIKeyError("Provided API key is invalid or has been deactivated")

    return application

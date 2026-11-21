
from app.core.exceptions import AuthenticationError, InvalidAPIKeyError
from app.core.security import hash_api_key
from app.database.models.application import Application
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
    """Extracts API key from either X-API-Key header or Authorization: Bearer header."""
    if x_api_key:
        return x_api_key
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


async def verify_application_api_key(
    api_key: str | None = Depends(get_api_key_from_headers),
    db: AsyncSession = Depends(get_db),
) -> Application:
    """
    Validates application API key against hashed values in the database.
    Raises AuthenticationError if missing, or InvalidAPIKeyError if key is invalid/inactive.
    """
    if not api_key:
        raise AuthenticationError("API key must be provided via 'X-API-Key' or 'Authorization: Bearer <key>'")

    hashed_key = hash_api_key(api_key)
    query = select(Application).where(
        Application.api_key_hash == hashed_key,
        Application.status == "active"
    )
    result = await db.execute(query)
    application = result.scalar_one_or_none()

    if not application:
        raise InvalidAPIKeyError("Provided API key is invalid or has been deactivated")

    return application

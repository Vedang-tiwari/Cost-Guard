from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)


class ApplicationResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    key_prefix: str | None = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplicationCreateResponse(ApplicationResponse):
    api_key: str = Field(..., description="Full API key (displayed once upon creation)")

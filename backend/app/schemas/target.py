from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class TargetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    url: HttpUrl
    environment: str = Field(..., min_length=1, max_length=50)


class TargetResponse(BaseModel):
    id: UUID
    name: str
    url: str
    environment: str
    allowed_host: str
    created_at: datetime

    class Config:
        from_attributes = True
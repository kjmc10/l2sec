from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RunnerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class RunnerCreatedResponse(BaseModel):
    id: UUID
    name: str
    token: str
    is_online: bool
    created_at: datetime


class RunnerResponse(BaseModel):
    id: UUID
    name: str
    is_online: bool
    last_seen_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class RunnerHeartbeatResponse(BaseModel):
    status: str
    runner_id: UUID
    runner_name: str
    is_online: bool
    last_seen_at: datetime
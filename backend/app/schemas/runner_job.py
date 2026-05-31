from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RunnerTargetPayload(BaseModel):
    id: UUID
    name: str
    url: str
    environment: str
    allowed_host: str


class RunnerJobPayload(BaseModel):
    id: UUID
    target_id: UUID
    runner_id: UUID | None
    scan_type: str
    status: str
    upload_mode: str
    created_at: datetime
    target: RunnerTargetPayload


class RunnerJobStatusUpdate(BaseModel):
    status: str
    message: str | None = None
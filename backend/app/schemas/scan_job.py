from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ScanJobCreate(BaseModel):
    target_id: UUID
    runner_id: UUID | None = None
    scan_type: str = Field(default="baseline", max_length=50)
    upload_mode: str = Field(default="sanitized", max_length=50)


class ScanJobResponse(BaseModel):
    id: UUID
    target_id: UUID
    runner_id: UUID | None
    scan_type: str
    status: str
    upload_mode: str
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None

    class Config:
        from_attributes = True


class ScanJobStatusUpdate(BaseModel):
    status: str = Field(..., max_length=50)
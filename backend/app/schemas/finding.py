from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from typing import Literal


class FindingResponse(BaseModel):
    id: UUID
    scan_job_id: UUID
    target_id: UUID
    name: str
    severity: str
    confidence: str | None
    url: str | None
    method: str | None
    cwe: str | None
    owasp_category: str | None
    evidence: str | None
    remediation: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

FindingStatus = Literal[
    "open",
    "false_positive",
    "accepted_risk",
    "fixed",
]

class FindingStatusUpdate(BaseModel):
    status: FindingStatus

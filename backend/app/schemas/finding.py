from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
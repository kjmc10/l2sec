import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Finding(Base):
    __tablename__ = "findings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id"), nullable=False)
    target_id = Column(UUID(as_uuid=True), ForeignKey("targets.id"), nullable=False)
    name = Column(String(500), nullable=False)
    severity = Column(String(50), nullable=False)
    confidence = Column(String(50), nullable=True)
    url = Column(String(2048), nullable=True)
    method = Column(String(20), nullable=True)
    cwe = Column(String(100), nullable=True)
    owasp_category = Column(String(255), nullable=True)
    evidence = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    status = Column(String(50), default="open", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
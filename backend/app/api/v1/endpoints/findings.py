from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.finding import Finding


router = APIRouter()


@router.get("/findings")
def list_findings(
    severity: str | None = Query(default=None),
    scan_job_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Finding)

    if severity:
        query = query.filter(Finding.severity == severity)

    if scan_job_id:
        query = query.filter(Finding.scan_job_id == scan_job_id)

    findings = query.order_by(Finding.created_at.desc()).all()

    return findings
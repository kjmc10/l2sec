from fastapi import HTTPException, APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.schemas.finding import FindingStatusUpdate
from app.db.session import get_db
from app.models.finding import Finding


router = APIRouter()


@router.get("")
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

@router.get("/summary")
def findings_summary(
    scan_job_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Finding)

    if scan_job_id:
        query = query.filter(Finding.scan_job_id == scan_job_id)

    findings = query.all()

    summary = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "total": len(findings),
    }

    for f in findings:
        if f.severity in summary:
            summary[f.severity] += 1

    return summary

@router.patch("/{finding_id}/status")
def update_finding_status(
    finding_id: str,
    payload: FindingStatusUpdate,
    db: Session = Depends(get_db),
):
    finding = db.query(Finding).filter(Finding.id == finding_id).first()

    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.status = payload.status

    db.commit()
    db.refresh(finding)

    return {
        "id": finding.id,
        "status": finding.status,
        "severity": finding.severity,
    }
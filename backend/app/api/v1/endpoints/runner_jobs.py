from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.scan_job import ScanJob
from app.models.target import Target
from app.schemas.runner_job import RunnerJobPayload, RunnerJobStatusUpdate
from app.schemas.runner_results import RunnerResultsPayload
from app.services.runner_auth import get_runner_from_authorization


router = APIRouter()


VALID_JOB_STATUSES = {
    "picked",
    "running",
    "completed",
    "failed",
    "canceled",
}


@router.get(
    "/runner/jobs/next",
    response_model=RunnerJobPayload | None,
)
def get_next_runner_job(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    runner = get_runner_from_authorization(
        db=db,
        authorization=authorization,
    )

    scan_job = (
        db.query(ScanJob)
        .filter(ScanJob.status == "queued")
        .filter(
            (ScanJob.runner_id.is_(None)) | (ScanJob.runner_id == runner.id)
        )
        .order_by(ScanJob.created_at.asc())
        .first()
    )

    if not scan_job:
        return None

    target = db.query(Target).filter(Target.id == scan_job.target_id).first()

    if not target:
        scan_job.status = "failed"
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Scan job target not found.",
        )

    scan_job.runner_id = runner.id
    scan_job.status = "picked"

    db.commit()
    db.refresh(scan_job)

    return {
        "id": scan_job.id,
        "target_id": scan_job.target_id,
        "runner_id": scan_job.runner_id,
        "scan_type": scan_job.scan_type,
        "status": scan_job.status,
        "upload_mode": scan_job.upload_mode,
        "created_at": scan_job.created_at,
        "target": {
            "id": target.id,
            "name": target.name,
            "url": target.url,
            "environment": target.environment,
            "allowed_host": target.allowed_host,
        },
    }


@router.post(
    "/runner/jobs/{scan_job_id}/status",
    response_model=dict,
)
def update_runner_job_status(
    scan_job_id: UUID,
    data: RunnerJobStatusUpdate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    runner = get_runner_from_authorization(
        db=db,
        authorization=authorization,
    )

    if data.status not in VALID_JOB_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed values: {sorted(VALID_JOB_STATUSES)}",
        )

    scan_job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()

    if not scan_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found.",
        )

    if scan_job.runner_id != runner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This job is not assigned to this runner.",
        )

    now = datetime.now(timezone.utc)

    scan_job.status = data.status

    if data.status == "running":
        scan_job.started_at = now

    if data.status in ["completed", "failed", "canceled"]:
        scan_job.finished_at = now

    db.commit()
    db.refresh(scan_job)

    return {
        "status": "ok",
        "scan_job_id": str(scan_job.id),
        "job_status": scan_job.status,
        "message": data.message,
    }


@router.post(
    "/runner/jobs/{scan_job_id}/results",
)
def submit_job_results(
    scan_job_id: UUID,
    payload: RunnerResultsPayload,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    runner = get_runner_from_authorization(
        db=db,
        authorization=authorization,
    )

    scan_job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()

    if not scan_job:
        raise HTTPException(status_code=404, detail="Scan job not found")

    if scan_job.runner_id != runner.id:
        raise HTTPException(status_code=403, detail="Invalid runner")

    from app.models.finding import Finding

    for f in payload.findings:
        finding = Finding(
            scan_job_id=scan_job.id,
            target_id=scan_job.target_id,
            name=f.name,
            severity=f.severity,
            confidence=f.confidence,
            url=f.url,
            method=f.method,
            cwe=f.cwe,
            owasp_category=f.owasp_category,
            evidence=f.evidence,
            remediation=f.remediation,
        )

        db.add(finding)

    db.commit()

    return {
        "status": "ok",
        "findings_count": len(payload.findings),
    }


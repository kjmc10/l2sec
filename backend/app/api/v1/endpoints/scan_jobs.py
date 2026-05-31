from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.runner import Runner
from app.models.scan_job import ScanJob
from app.models.target import Target
from app.schemas.scan_job import ScanJobCreate, ScanJobResponse


router = APIRouter()


VALID_SCAN_TYPES = {
    "baseline",
    "api",
    "full",
    "passive",
}


VALID_UPLOAD_MODES = {
    "sanitized",
    "metadata_only",
}


@router.post(
    "/scan-jobs",
    response_model=ScanJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_scan_job(
    data: ScanJobCreate,
    db: Session = Depends(get_db),
):
    target = db.query(Target).filter(Target.id == data.target_id).first()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found.",
        )

    if data.runner_id:
        runner = db.query(Runner).filter(Runner.id == data.runner_id).first()

        if not runner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Runner not found.",
            )

    if data.scan_type not in VALID_SCAN_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid scan_type. Allowed values: {sorted(VALID_SCAN_TYPES)}",
        )

    if data.upload_mode not in VALID_UPLOAD_MODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid upload_mode. Allowed values: {sorted(VALID_UPLOAD_MODES)}",
        )

    scan_job = ScanJob(
        target_id=data.target_id,
        runner_id=data.runner_id,
        scan_type=data.scan_type,
        upload_mode=data.upload_mode,
        status="queued",
    )

    db.add(scan_job)
    db.commit()
    db.refresh(scan_job)

    return scan_job


@router.get(
    "/scan-jobs",
    response_model=list[ScanJobResponse],
)
def list_scan_jobs(
    db: Session = Depends(get_db),
):
    scan_jobs = db.query(ScanJob).order_by(ScanJob.created_at.desc()).all()

    return scan_jobs


@router.get(
    "/scan-jobs/{scan_job_id}",
    response_model=ScanJobResponse,
)
def get_scan_job(
    scan_job_id: UUID,
    db: Session = Depends(get_db),
):
    scan_job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()

    if not scan_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found.",
        )

    return scan_job


@router.post(
    "/scan-jobs/{scan_job_id}/cancel",
    response_model=ScanJobResponse,
)
def cancel_scan_job(
    scan_job_id: UUID,
    db: Session = Depends(get_db),
):
    scan_job = db.query(ScanJob).filter(ScanJob.id == scan_job_id).first()

    if not scan_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan job not found.",
        )

    if scan_job.status in ["completed", "failed", "canceled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job in status '{scan_job.status}'.",
        )

    scan_job.status = "canceled"

    db.commit()
    db.refresh(scan_job)

    return scan_job
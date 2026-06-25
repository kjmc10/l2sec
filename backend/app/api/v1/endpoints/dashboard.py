from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.finding import Finding
from app.models.runner import Runner
from app.models.scan_job import ScanJob
from app.models.target import Target


router = APIRouter()


SEVERITIES = ["high", "medium", "low", "info"]
FINDING_STATUSES = ["open", "false_positive", "accepted_risk", "fixed"]
SCAN_JOB_STATUSES = ["queued", "picked", "running", "completed", "failed", "canceled"]


def normalize_severity(severity: str | None) -> str:
    if not severity:
        return "info"

    normalized = severity.lower().strip()

    if normalized in ["informational", "information"]:
        return "info"

    if normalized not in SEVERITIES:
        return "info"

    return normalized


def normalize_finding_status(status: str | None) -> str:
    if not status:
        return "open"

    normalized = status.lower().strip()

    if normalized not in FINDING_STATUSES:
        return "open"

    return normalized


def normalize_scan_job_status(status: str | None) -> str:
    if not status:
        return "queued"

    normalized = status.lower().strip()

    if normalized not in SCAN_JOB_STATUSES:
        return normalized

    return normalized


def calculate_security_score(
    high: int,
    medium: int,
    low: int,
) -> int:
    """
    MVP risk score:
    - Base: 100
    - High: -20 each
    - Medium: -8 each
    - Low: -3 each

    Info findings do not reduce score.
    """

    score = 100

    score -= high * 20
    score -= medium * 8
    score -= low * 3

    return max(score, 0)


def calculate_quality_gate(high: int) -> str:
    """
    MVP quality gate:
    - failed si existe al menos 1 finding high abierto
    - passed si no hay high abierto
    """

    if high > 0:
        return "failed"

    return "passed"


def build_target_lookup(db: Session) -> dict[str, Target]:
    targets = db.query(Target).all()

    return {
        str(target.id): target
        for target in targets
    }


def build_runner_lookup(db: Session) -> dict[str, Runner]:
    runners = db.query(Runner).all()

    return {
        str(runner.id): runner
        for runner in runners
    }


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    findings = db.query(Finding).all()
    runners = db.query(Runner).all()
    targets = db.query(Target).all()

    target_lookup = build_target_lookup(db)
    runner_lookup = build_runner_lookup(db)

    severity_counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "total": 0,
    }

    finding_status_counts = {
        "open": 0,
        "false_positive": 0,
        "accepted_risk": 0,
        "fixed": 0,
    }

    actionable_findings = []

    for finding in findings:
        severity = normalize_severity(finding.severity)
        finding_status = normalize_finding_status(finding.status)

        severity_counts[severity] += 1
        severity_counts["total"] += 1

        finding_status_counts[finding_status] += 1

        if finding_status == "open":
            actionable_findings.append(finding)

    actionable_severity_counts = {
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "total": len(actionable_findings),
    }

    for finding in actionable_findings:
        severity = normalize_severity(finding.severity)
        actionable_severity_counts[severity] += 1

    security_score = calculate_security_score(
        high=actionable_severity_counts["high"],
        medium=actionable_severity_counts["medium"],
        low=actionable_severity_counts["low"],
    )

    quality_gate = calculate_quality_gate(
        high=actionable_severity_counts["high"],
    )

    total_jobs = db.query(ScanJob).count()

    queued_jobs = db.query(ScanJob).filter(ScanJob.status == "queued").count()
    running_jobs = db.query(ScanJob).filter(ScanJob.status == "running").count()
    completed_jobs = db.query(ScanJob).filter(ScanJob.status == "completed").count()
    failed_jobs = db.query(ScanJob).filter(ScanJob.status == "failed").count()
    picked_jobs = db.query(ScanJob).filter(ScanJob.status == "picked").count()

    scan_job_summary = {
        "total": total_jobs,
        "queued": queued_jobs,
        "running": running_jobs + picked_jobs,  # 🔥 clave
        "completed": completed_jobs,
        "failed": failed_jobs,
    }

    latest_scan_jobs = (
        db.query(ScanJob)
        .order_by(ScanJob.created_at.desc())
        .limit(5)
        .all()
    )

    latest_scans = []

    for scan_job in latest_scan_jobs:
        target = target_lookup.get(str(scan_job.target_id))
        runner = runner_lookup.get(str(scan_job.runner_id)) if scan_job.runner_id else None

        latest_scans.append(
            {
                "id": str(scan_job.id),
                "target_id": str(scan_job.target_id),
                "target_name": target.name if target else None,
                "target_url": target.url if target else None,
                "runner_id": str(scan_job.runner_id) if scan_job.runner_id else None,
                "runner_name": runner.name if runner else None,
                "scan_type": scan_job.scan_type,
                "status": normalize_scan_job_status(scan_job.status),
                "upload_mode": scan_job.upload_mode,
                "created_at": scan_job.created_at,
                "started_at": scan_job.started_at,
                "finished_at": scan_job.finished_at,
            }
        )

    runners_online = len(
        [
            runner
            for runner in runners
            if runner.is_online
        ]
    )

    latest_runners = []

    for runner in runners[:5]:
        latest_runners.append(
            {
                "id": str(runner.id),
                "name": runner.name,
                "is_online": runner.is_online,
                "last_seen_at": runner.last_seen_at,
                "created_at": runner.created_at,
            }
        )

    latest_targets = []

    for target in targets[:5]:
        latest_targets.append(
            {
                "id": str(target.id),
                "name": target.name,
                "url": target.url,
                "environment": target.environment,
                "allowed_host": target.allowed_host,
                "created_at": target.created_at,
            }
        )

    return {
        "security_score": security_score,
        "quality_gate": quality_gate,
        "findings": {
            "severity": severity_counts,
            "actionable_severity": actionable_severity_counts,
            "status": finding_status_counts,
            "total": len(findings),
            "open": finding_status_counts["open"],
        },
        "scan_jobs": {
        "summary": scan_job_summary,
        "latest": latest_scans,
        },
        "runners": {
            "online": runners_online,
            "total": len(runners),
            "latest": latest_runners,
        },
        "targets": {
            "total": len(targets),
            "latest": latest_targets,
        },
    }
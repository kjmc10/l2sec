from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import generate_runner_token, hash_token
from app.db.session import get_db
from app.models.runner import Runner
from app.schemas.runner import (
    RunnerCreate,
    RunnerCreatedResponse,
    RunnerHeartbeatResponse,
    RunnerResponse,
)
from app.services.runner_auth import get_runner_from_authorization


router = APIRouter()


@router.post(
    "/runners",
    response_model=RunnerCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_runner(
    data: RunnerCreate,
    db: Session = Depends(get_db),
):
    token = generate_runner_token()
    token_hash = hash_token(token)

    runner = Runner(
        name=data.name,
        token_hash=token_hash,
        is_online=False,
    )

    db.add(runner)
    db.commit()
    db.refresh(runner)

    return {
        "id": runner.id,
        "name": runner.name,
        "token": token,
        "is_online": runner.is_online,
        "created_at": runner.created_at,
    }


@router.get(
    "/runners",
    response_model=list[RunnerResponse],
)
def list_runners(
    db: Session = Depends(get_db),
):
    runners = db.query(Runner).order_by(Runner.created_at.desc()).all()

    return runners


@router.post(
    "/runners/heartbeat",
    response_model=RunnerHeartbeatResponse,
)
def runner_heartbeat(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    runner = get_runner_from_authorization(
        db=db,
        authorization=authorization,
    )

    now = datetime.now(timezone.utc)

    runner.is_online = True
    runner.last_seen_at = now

    db.commit()
    db.refresh(runner)

    return {
        "status": "ok",
        "runner_id": runner.id,
        "runner_name": runner.name,
        "is_online": runner.is_online,
        "last_seen_at": runner.last_seen_at,
    }
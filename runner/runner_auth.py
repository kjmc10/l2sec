from fastapi import Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.models.runner import Runner


def extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
        )

    parts = authorization.split(" ")

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header. Use: Bearer <token>.",
        )

    return parts[1]


def get_runner_from_authorization(
    db: Session,
    authorization: str | None = Header(default=None),
) -> Runner:
    token = extract_bearer_token(authorization)
    token_hash = hash_token(token)

    runner = db.query(Runner).filter(Runner.token_hash == token_hash).first()

    if not runner:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid runner token.",
        )

    return runner
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.target import Target
from app.schemas.target import TargetCreate, TargetResponse


router = APIRouter()


@router.post(
    "/targets",
    response_model=TargetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_target(
    data: TargetCreate,
    db: Session = Depends(get_db),
):
    parsed_url = urlparse(str(data.url))

    if parsed_url.scheme not in ["http", "https"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only http and https URLs are allowed.",
        )

    if not parsed_url.hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target URL must contain a valid hostname.",
        )

    target = Target(
        name=data.name,
        url=str(data.url),
        environment=data.environment,
        allowed_host=parsed_url.hostname,
    )

    db.add(target)
    db.commit()
    db.refresh(target)

    return target


@router.get(
    "/targets",
    response_model=list[TargetResponse],
)
def list_targets(
    db: Session = Depends(get_db),
):
    targets = db.query(Target).order_by(Target.created_at.desc()).all()

    return targets


@router.get(
    "/targets/{target_id}",
    response_model=TargetResponse,
)
def get_target(
    target_id: str,
    db: Session = Depends(get_db),
):
    target = db.query(Target).filter(Target.id == target_id).first()

    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found.",
        )

    return target
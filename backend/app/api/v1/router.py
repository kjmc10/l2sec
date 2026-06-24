from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.endpoints import runner_jobs
from app.api.v1.endpoints import runners
from app.api.v1.endpoints import scan_jobs
from app.api.v1.endpoints import targets
from app.api.v1.endpoints import findings
from app.api.v1.endpoints import dashboard

api_router = APIRouter()

api_router.include_router(
    health.router,
    tags=["health"],
)

api_router.include_router(
    targets.router,
    tags=["targets"],
)

api_router.include_router(
    runners.router,
    prefix="/runners",
    tags=["runners"],
)

api_router.include_router(
    scan_jobs.router,
    tags=["scan-jobs"],
)

api_router.include_router(
    runner_jobs.router,
    tags=["runner-jobs"],
)
api_router.include_router(
    findings.router, 
    prefix="/findings",
    tags=["findings"]
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

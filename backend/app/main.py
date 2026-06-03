import logging

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("L2Sec")


app = FastAPI(
    title="L2Sec API",
    description="Local-first PTaaS/DAST control plane API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://localhost:4201",
        "http://localhost:4202",
        "http://localhost:4203",
        "http://localhost:4204",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)


@app.on_event("startup")
def on_startup():
    logger.info("L2Sec API started")
    logger.info("Environment: %s", settings.app_env)
    logger.info("API prefix: %s", settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "message": "L2Sec API is running",
        "docs": "/docs",
        "health": f"{settings.api_v1_prefix}/health",
    }
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("l2sec")

logger.info("L2Sec API started")


app = FastAPI(
    title="l2sec API",
    description="Local-first PTaaS/DAST control plane API",
    version="0.1.0",
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "message": "l2sec API is running",
        "docs": "/docs",
    }
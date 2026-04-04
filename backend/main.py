"""FastAPI entrypoint for the MVP backend."""

from __future__ import annotations

from fastapi import FastAPI

from backend.api.routes.analysis import router as analysis_router
from backend.api.routes.intake import router as intake_router
from backend.core.config import settings


app = FastAPI(
    title="Enviro Negotiator MVP API",
    version="0.1.0",
    description="Phase 0 API skeleton for structured intake and baseline analysis.",
)


@app.get("/health")
def health() -> dict[str, str | bool]:
    """Global health endpoint."""

    return {
        "status": "ok",
        "environment": settings.app_env,
        "mock_mode": settings.mock_mode,
    }


app.include_router(intake_router, prefix="/api/v1/intake", tags=["intake"])
app.include_router(analysis_router, prefix="/api/v1/analysis", tags=["analysis"])

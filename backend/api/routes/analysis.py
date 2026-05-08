"""Analysis route group for baseline and placeholder agent processing."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.api_models import (
    AgentReviewRequest,
    AgentReviewResponse,
    BaselineRequest,
    BaselineResponse,
    OrientationOptionsResponse,
)
from backend.services.agent_review_service import run_agent_review
from backend.services.orchestration_service import run_baseline_pipeline
from backend.services.orientation_service import get_orientation_options

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    """Simple health endpoint for analysis route group."""

    return {"status": "ok", "service": "analysis"}


@router.post("/baseline", response_model=BaselineResponse)
def baseline(request: BaselineRequest) -> BaselineResponse:
    """Run baseline heuristics and placeholder mitigation ranking."""

    if not request.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Project state must be explicitly confirmed before baseline analysis.",
        )

    enriched = run_baseline_pipeline(request.project_state)
    return BaselineResponse(project_state=enriched)


@router.post("/agent-review", response_model=AgentReviewResponse)
def agent_review(request: AgentReviewRequest) -> AgentReviewResponse:
    """Run explicit post-baseline constraint/compensation/tradeoff review."""

    baseline = request.project_state.baseline_results
    if baseline.energy_risk is None:
        raise HTTPException(
            status_code=400,
            detail="Baseline analysis must run before agent review.",
        )

    return run_agent_review(request.project_state)


@router.post("/orientation-options", response_model=OrientationOptionsResponse)
def orientation_options(request: AgentReviewRequest) -> OrientationOptionsResponse:
    """Return top 3 scored orientation options for the current project state."""
    return get_orientation_options(request.project_state)

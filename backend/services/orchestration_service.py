"""Workflow orchestration for Phase 0 baseline analysis pipeline."""

from __future__ import annotations

from shared.project_state import ProjectState

from backend.services.climate_service import get_climate_context
from backend.services.scoring_service import compute_baseline
from backend.services.validation_service import validate_project_state


def run_baseline_pipeline(project: ProjectState) -> ProjectState:
    """Validate state, derive climate context, and compute baseline metrics."""

    project.validation_issues = validate_project_state(project)
    climate_context = get_climate_context(project.site)
    project.climate_context = climate_context
    project.baseline_results = compute_baseline(project, climate_context)
    if not project.assumptions:
        project.assumptions.append("Baseline scores are heuristic, not simulation-grade.")
    return project

"""Climate agent: derive climate context from site fields."""

from __future__ import annotations

from shared.project_state import ProjectState

from backend.services.climate_service import get_climate_context


class ClimateAgent:
    """Provides climate context for downstream analysis."""

    def run(self, project: ProjectState) -> dict[str, str | float]:
        return get_climate_context(project.site)

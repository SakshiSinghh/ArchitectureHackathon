"""Climate agent: derive climate context from site fields."""

from __future__ import annotations

from typing import Any

from shared.project_state import ProjectState

from backend.services.climate_service import get_climate_context


class ClimateAgent:
    """Provides climate context for downstream analysis."""

    def run(self, project: ProjectState) -> dict[str, Any]:
        return get_climate_context(project.site)

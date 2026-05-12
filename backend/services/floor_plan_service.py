"""Floor plan upload service: run analysis and persist results to project state."""

from __future__ import annotations

import math
from typing import Any

from fastapi import HTTPException

from backend.agents.floor_plan_agent import FloorPlanAgent
from backend.services.project_service import ProjectService
from shared.project_state import Building, FloorPlanAnalysis, ProjectState

_ORIENTATION_MAP: dict[str, float] = {
    "north": 0.0,
    "north-east": 45.0,
    "east": 90.0,
    "south-east": 135.0,
    "south": 180.0,
    "south-west": 225.0,
    "west": 270.0,
    "north-west": 315.0,
}


def _infer_orientation_deg(analysis: FloorPlanAnalysis) -> float | None:
    """Return orientation_deg from analysis, falling back to room-facade inference."""

    if analysis.primary_orientation_deg is not None:
        return analysis.primary_orientation_deg

    # Use the most common external room orientation as a proxy.
    counts: dict[str, int] = {}
    for room in analysis.rooms:
        if room.is_external:
            for orientation in room.facade_orientations:
                counts[orientation.lower()] = counts.get(orientation.lower(), 0) + 1

    if not counts:
        return None

    dominant = max(counts, key=lambda k: counts[k])
    return _ORIENTATION_MAP.get(dominant)


def _infer_wwr(analysis: FloorPlanAnalysis) -> float | None:
    """Estimate window-to-wall ratio from suggestion keywords (rough heuristic)."""

    for suggestion in analysis.overall_suggestions:
        lower = suggestion.lower()
        if "wwr" in lower or "glazing ratio" in lower or "window-to-wall" in lower:
            # Try to parse a numeric value from text like "should not exceed 0.20"
            import re
            match = re.search(r"0\.\d+", lower)
            if match:
                return float(match.group(0))
    return None


class FloorPlanService:
    """Orchestrates floor plan analysis and project state persistence."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._agent = FloorPlanAgent()
        self._project_service = ProjectService(base_dir=base_dir)

    def analyse_and_persist(
        self, project_id: str, image_bytes: bytes, media_type: str
    ) -> dict[str, Any]:
        """Run floor plan analysis, merge findings into project state, and persist.

        Returns a dict with keys: floor_plan_analysis, updated_building, project_id.
        Raises HTTPException(404) when the project does not exist.
        """

        # Load existing project — raises 404 via ProjectService if not found.
        project_detail = self._project_service.get_project(project_id)
        raw_state = project_detail["current_state"]
        current_state = raw_state if isinstance(raw_state, ProjectState) else ProjectState(**raw_state)

        # Run vision analysis.
        analysis: FloorPlanAnalysis = self._agent.run(image_bytes, media_type)

        # Merge findings into building fields (only fill blanks — don't overwrite user data).
        building = current_state.building
        inferred_orientation = _infer_orientation_deg(analysis)
        inferred_wwr = _infer_wwr(analysis)

        updated_building = Building(
            building_type=building.building_type,
            width_m=building.width_m,
            depth_m=building.depth_m,
            height_m=building.height_m,
            floors=building.floors,
            orientation_deg=(
                building.orientation_deg
                if building.orientation_deg is not None
                else inferred_orientation
            ),
            window_to_wall_ratio=(
                building.window_to_wall_ratio
                if building.window_to_wall_ratio is not None
                else inferred_wwr
            ),
            geometry_notes=building.geometry_notes or analysis.analysis_notes,
        )

        # Record provenance for inferred fields.
        provenance = current_state.provenance
        if building.orientation_deg is None and inferred_orientation is not None:
            if "orientation_deg" not in provenance.inferred_fields:
                provenance.inferred_fields.append("orientation_deg")
        if building.window_to_wall_ratio is None and inferred_wwr is not None:
            if "window_to_wall_ratio" not in provenance.inferred_fields:
                provenance.inferred_fields.append("window_to_wall_ratio")

        updated_state = ProjectState(
            **{
                **current_state.model_dump(),
                "building": updated_building.model_dump(),
                "provenance": provenance.model_dump(),
                "floor_plan_analysis": analysis.model_dump(),
            }
        )

        self._project_service.update_project(project_id, updated_state)

        return {
            "project_id": project_id,
            "floor_plan_analysis": analysis,
            "updated_building": updated_building,
        }

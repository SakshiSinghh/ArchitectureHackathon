from __future__ import annotations

from backend.services.orchestration_service import run_baseline_pipeline
from shared.project_state import ProjectState


def _project_with_minimum_inputs() -> ProjectState:
    state = ProjectState(project_name="Constraint Parsing Test")
    state.site.location_name = "Pune"
    state.building.building_type = "office"
    state.building.width_m = 20
    state.building.depth_m = 30
    state.building.height_m = 24
    state.building.orientation_deg = 90
    state.building.window_to_wall_ratio = 0.35
    return state


def test_free_text_constraints_are_preserved_and_noted() -> None:
    state = _project_with_minimum_inputs()
    state.constraints["free_text"] = "Orientation cannot change due to site access."

    enriched = run_baseline_pipeline(state)

    assert "free_text" in enriched.constraints
    assert isinstance(enriched.constraints.get("free_text"), str)
    assert "effective_hard_constraints" in enriched.constraints
    assert any("interpreted with human review" in note.lower() for note in enriched.assumptions)

import os

from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_MODE", "true")

from backend.main import app
from backend.services.constraint_parsing_service import prepare_constraints_context
from shared.project_state import ParsedConstraintItem, ParsedConstraints, ProjectState


client = TestClient(app)


def _sample_project_state() -> dict:
    return {
        "project_name": "Constraint Parse Demo",
        "input_mode": "manual_form",
        "brief_text": None,
        "site": {
            "location_name": "Pune",
            "latitude": 18.52,
            "longitude": 73.85,
            "climate_notes": None,
        },
        "building": {
            "building_type": "office",
            "width_m": 20,
            "depth_m": 28,
            "height_m": 24,
            "floors": 6,
            "orientation_deg": 90,
            "window_to_wall_ratio": 0.35,
            "geometry_notes": None,
        },
        "constraints": {
            "hard_constraints": ["max floors 6"],
            "soft_constraints": [],
            "free_text": "Orientation cannot change due to access. Height capped at 8 floors.",
            "structured_enabled": True,
            "notes": None,
        },
        "priorities": {
            "energy": 0.25,
            "daylight": 0.2,
            "ventilation": 0.2,
            "cost": 0.2,
            "aesthetics": 0.15,
        },
        "provenance": {
            "user_provided_fields": ["project_name", "location_name"],
            "inferred_fields": [],
            "defaulted_fields": [],
            "unresolved_fields": [],
        },
        "assumptions": [],
        "validation_issues": [],
        "parsed_constraints": {
            "extracted_items": [],
            "unresolved_items": [],
            "confidence_label": "low",
            "confidence_score": 0,
            "parser_provider": "none",
            "parser_mode": "none",
            "notes": [],
            "conflict_warnings": [],
        },
        "climate_context": {},
        "baseline_results": {
            "summary": "Not computed yet",
            "energy_risk": None,
            "daylight_potential": None,
            "ventilation_potential": None,
            "narrative_insight": None,
        },
        "mitigation_options": [],
    }


def test_interpret_constraints_endpoint_returns_candidates() -> None:
    response = client.post(
        "/api/v1/intake/interpret-constraints",
        json={
            "project_state": _sample_project_state(),
        },
    )

    assert response.status_code == 200
    payload = response.json()["parsed_constraints"]
    assert payload["parser_mode"] in {"heuristic", "llm"}
    keys = [item["normalized_key"] for item in payload["extracted_items"]]
    assert "orientation_locked" in keys
    assert "max_floors" in keys
    assert payload["conflict_warnings"]


def test_prepare_constraints_context_uses_accepted_and_edited_items_only() -> None:
    project = ProjectState()
    project.constraints["hard_constraints"] = ["max floors 6"]
    project.constraints["free_text"] = "Max floors 8 and lock orientation"
    project.parsed_constraints = ParsedConstraints(
        extracted_items=[
            ParsedConstraintItem(
                source_text="Max floors 8",
                normalized_key="max_floors",
                normalized_value=8,
                confidence=0.9,
                status="accepted",
            ),
            ParsedConstraintItem(
                source_text="Lock orientation",
                normalized_key="orientation_locked",
                normalized_value=True,
                confidence=0.8,
                status="edited",
            ),
            ParsedConstraintItem(
                source_text="Ignore this",
                normalized_key="facade_locked",
                normalized_value=True,
                confidence=0.7,
                status="rejected",
            ),
        ]
    )

    next_state = prepare_constraints_context(project)

    assert "max floors 6" in next_state.constraints["effective_hard_constraints"]
    assert "max floors 8" in next_state.constraints["effective_hard_constraints"]
    assert "orientation locked" in next_state.constraints["effective_hard_constraints"]
    assert "facade intent locked" not in next_state.constraints["effective_hard_constraints"]
    assert "max floors 8" in next_state.constraints["parsed_hard_constraints"]

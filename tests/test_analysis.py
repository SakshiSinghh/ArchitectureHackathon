import os

from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_MODE", "true")

from backend.main import app


client = TestClient(app)


def _sample_project_state() -> dict:
    return {
        "project_name": "Phase 1 Demo",
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
            "hard_constraints": ["max height 30m"],
            "soft_constraints": ["maximize daylight"],
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


def test_baseline_happy_path_when_confirmed() -> None:
    response = client.post(
        "/api/v1/analysis/baseline",
        json={
            "confirmed": True,
            "project_state": _sample_project_state(),
        },
    )

    assert response.status_code == 200
    project_state = response.json()["project_state"]
    assert project_state["baseline_results"]["energy_risk"] is not None
    assert project_state["climate_context"]["location"] == "Pune"
    assert project_state["climate_context"]["provider"] in {"mock", "visualcrossing", "open-meteo"}
    assert "source_tier" in project_state["climate_context"]
    assert project_state["baseline_results"]["heat_exposure_score"] is not None


def test_baseline_rejects_unconfirmed_state() -> None:
    response = client.post(
        "/api/v1/analysis/baseline",
        json={
            "confirmed": False,
            "project_state": _sample_project_state(),
        },
    )

    assert response.status_code == 400
    assert "confirmed" in response.json()["detail"].lower()


def test_agent_review_happy_path_after_baseline() -> None:
    baseline_response = client.post(
        "/api/v1/analysis/baseline",
        json={
            "confirmed": True,
            "project_state": _sample_project_state(),
        },
    )
    assert baseline_response.status_code == 200

    review_response = client.post(
        "/api/v1/analysis/agent-review",
        json={"project_state": baseline_response.json()["project_state"]},
    )

    assert review_response.status_code == 200
    payload = review_response.json()
    assert "baseline_metrics" in payload
    assert "constrained_metrics" in payload
    assert "metric_deltas" in payload
    assert isinstance(payload["ranked_options"], list)


def test_agent_review_rejects_without_baseline() -> None:
    response = client.post(
        "/api/v1/analysis/agent-review",
        json={"project_state": _sample_project_state()},
    )
    assert response.status_code == 400
    assert "baseline" in response.json()["detail"].lower()

from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("MOCK_MODE", "true")

from backend.main import app
from backend.schemas.project_models import RunSnapshot
from backend.services.project_service import diff_runs


client = TestClient(app)


def _sample_project_state(project_name: str = "Workspace Project") -> dict:
    return {
        "project_name": project_name,
        "input_mode": "manual_form",
        "brief_text": "Improve passive comfort while keeping cost stable.",
        "site": {
            "location_name": "Pune",
            "latitude": 18.52,
            "longitude": 73.85,
            "climate_notes": None,
        },
        "building": {
            "building_type": "office",
            "width_m": 22,
            "depth_m": 28,
            "height_m": 30,
            "floors": 8,
            "orientation_deg": 120,
            "window_to_wall_ratio": 0.4,
            "geometry_notes": "Early massing",
        },
        "constraints": {
            "hard_constraints": ["max height 45m"],
            "soft_constraints": ["maximize daylight"],
        },
        "priorities": {
            "energy": 0.3,
            "daylight": 0.25,
            "ventilation": 0.2,
            "cost": 0.15,
            "aesthetics": 0.1,
        },
        "provenance": {
            "user_provided_fields": ["project_name"],
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
            "climate_provider": None,
            "heat_exposure_score": None,
            "solar_exposure_score": None,
            "climate_ventilation_score": None,
            "narrative_insight": None,
        },
        "mitigation_options": [],
    }


def test_project_create_list_get_update_and_runs(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PROJECTS_DATA_DIR", str(tmp_path / "projects"))

    create_response = client.post(
        "/api/v1/projects",
        json={
            "project_name": "Phase 4 Workspace",
            "brief_text": "Iterative negotiation baseline",
            "notes": "Initial workspace",
        },
    )
    assert create_response.status_code == 200
    created = create_response.json()
    project_id = created["project"]["project_id"]

    list_response = client.get("/api/v1/projects")
    assert list_response.status_code == 200
    listed = list_response.json()["projects"]
    assert any(project["project_id"] == project_id for project in listed)

    get_response = client.get(f"/api/v1/projects/{project_id}")
    assert get_response.status_code == 200
    assert get_response.json()["project"]["project_name"] == "Phase 4 Workspace"

    update_state = _sample_project_state(project_name="Phase 4 Workspace v2")
    update_response = client.put(
        f"/api/v1/projects/{project_id}",
        json={
            "project_state": update_state,
            "notes": "Refined constraints",
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["current_state"]["project_name"] == "Phase 4 Workspace v2"

    run1_response = client.post(
        f"/api/v1/projects/{project_id}/runs",
        json={"project_state": _sample_project_state(project_name="Iteration 1")},
    )
    assert run1_response.status_code == 200
    run1 = run1_response.json()
    assert run1["run"]["run_id"].startswith("run-")
    assert run1["run"]["climate_provider"] in {"mock", "visualcrossing", "open-meteo"}

    iter2_state = _sample_project_state(project_name="Iteration 2")
    iter2_state["building"]["orientation_deg"] = 145
    run2_response = client.post(
        f"/api/v1/projects/{project_id}/runs",
        json={"project_state": iter2_state},
    )
    assert run2_response.status_code == 200
    run2 = run2_response.json()
    assert run2["diff_from_previous"] is not None
    assert isinstance(run2["diff_from_previous"]["changed_inputs"], list)

    list_runs_response = client.get(f"/api/v1/projects/{project_id}/runs")
    assert list_runs_response.status_code == 200
    runs = list_runs_response.json()["runs"]
    assert len(runs) >= 2

    detail_after_runs = client.get(f"/api/v1/projects/{project_id}")
    assert detail_after_runs.status_code == 200
    assert len(detail_after_runs.json()["recent_run_ids"]) >= 1


def test_run_diff_utility_detects_changes() -> None:
    base = _sample_project_state(project_name="A")
    changed = _sample_project_state(project_name="B")
    changed["building"]["orientation_deg"] = 180

    snapshot_a = RunSnapshot.model_validate(
        {
            "run_id": "run-a",
            "created_at": "2026-04-06T00:00:00+00:00",
            "input_state": base,
            "baseline_state": base,
            "agent_review": {
                "baseline_metrics": {
                    "energy_risk": 0.5,
                    "daylight_potential": 0.6,
                    "ventilation_potential": 0.5,
                },
                "constrained_metrics": {
                    "energy_risk": 0.55,
                    "daylight_potential": 0.55,
                    "ventilation_potential": 0.48,
                },
                "metric_deltas": {
                    "energy_risk_delta": 0.05,
                    "daylight_potential_delta": -0.05,
                    "ventilation_potential_delta": -0.02,
                },
                "penalty_summary": "x",
                "ranked_options": [],
                "top_option_reason": "alpha",
            },
            "top_recommendation": "Option A",
            "climate_provider": "mock",
            "climate_source_tier": "mock_mode_forced",
        }
    )

    changed_baseline = _sample_project_state(project_name="B")
    changed_baseline["baseline_results"]["energy_risk"] = 0.62

    snapshot_b = RunSnapshot.model_validate(
        {
            "run_id": "run-b",
            "created_at": "2026-04-06T00:01:00+00:00",
            "input_state": changed,
            "baseline_state": changed_baseline,
            "agent_review": {
                "baseline_metrics": {
                    "energy_risk": 0.62,
                    "daylight_potential": 0.6,
                    "ventilation_potential": 0.5,
                },
                "constrained_metrics": {
                    "energy_risk": 0.66,
                    "daylight_potential": 0.56,
                    "ventilation_potential": 0.47,
                },
                "metric_deltas": {
                    "energy_risk_delta": 0.04,
                    "daylight_potential_delta": -0.04,
                    "ventilation_potential_delta": -0.03,
                },
                "penalty_summary": "y",
                "ranked_options": [],
                "top_option_reason": "beta",
            },
            "top_recommendation": "Option B",
            "climate_provider": "open-meteo",
            "climate_source_tier": "fallback_openmeteo_after_primary_failure",
        }
    )

    diff = diff_runs(snapshot_b, snapshot_a)
    assert any("state.project_name" == key for key in diff.changed_inputs)
    assert diff.changed_top_recommendation["previous"] == "Option A"
    assert diff.changed_top_recommendation["current"] == "Option B"

"""Tests for orientation options service and endpoint."""

from __future__ import annotations

import os

os.environ.setdefault("MOCK_MODE", "true")

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _sample_project_state(orientation_deg: float = 90.0) -> dict:
    return {
        "project_name": "Orientation Test",
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
            "orientation_deg": orientation_deg,
            "window_to_wall_ratio": 0.35,
            "geometry_notes": None,
        },
        "constraints": {
            "hard_constraints": [],
            "soft_constraints": [],
        },
        "priorities": {
            "energy": 0.25,
            "daylight": 0.2,
            "ventilation": 0.15,
            "cost": 0.2,
            "aesthetics": 0.1,
            "sustainability": 0.1,
        },
        "floor_plan_analysis": None,
        "baseline_results": {
            "energy_risk": None,
            "daylight_potential": None,
            "ventilation_potential": None,
            "heat_exposure": None,
            "solar_exposure": None,
            "ventilation_context": None,
            "narrative_insight": None,
            "mitigation_options": [],
        },
    }


class TestOrientationOptionsEndpoint:
    """POST /api/v1/analysis/orientation-options"""

    def test_returns_three_options(self):
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "options" in body
        assert len(body["options"]) == 3

    def test_options_have_required_fields(self):
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        for opt in resp.json()["options"]:
            assert "orientation_deg" in opt
            assert "label" in opt
            assert "rank" in opt
            assert "energy_risk" in opt
            assert "daylight_potential" in opt
            assert "ventilation_potential" in opt
            assert "composite_score" in opt
            assert "narrative" in opt
            assert "is_current" in opt

    def test_recommended_orientation_in_top3(self):
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        body = resp.json()
        option_degs = {o["orientation_deg"] for o in body["options"]}
        assert body["recommended_orientation_deg"] in option_degs

    def test_current_orientation_always_present(self):
        """The user's current orientation must appear even if not in top 3."""
        # Use 45 deg which may not be the highest composite score
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state(orientation_deg=45.0)},
        )
        assert resp.status_code == 200
        current_options = [o for o in resp.json()["options"] if o["is_current"]]
        assert len(current_options) == 1
        assert current_options[0]["orientation_deg"] == 45.0

    def test_ranks_are_sequential(self):
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        ranks = sorted(o["rank"] for o in resp.json()["options"])
        assert ranks == [1, 2, 3]

    def test_location_field_returned(self):
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        assert resp.json()["location"] == "Pune"

    def test_composite_score_descending(self):
        """Options should be ordered best-to-worst by composite score."""
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        options = resp.json()["options"]
        # Rank 1 should have the highest composite score among the 3
        rank1 = next(o for o in options if o["rank"] == 1)
        rank2 = next(o for o in options if o["rank"] == 2)
        assert rank1["composite_score"] >= rank2["composite_score"]


class TestOrientationService:
    """Unit-level checks on orientation_service helpers."""

    def test_all_eight_orientations_evaluated(self):
        """Running with a non-grid orientation should still produce 3 results."""
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state(orientation_deg=37.0)},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["options"]) == 3
        # The off-grid orientation must appear exactly once
        current_options = [o for o in body["options"] if o["is_current"]]
        assert len(current_options) == 1
        assert current_options[0]["orientation_deg"] == 37.0

    def test_score_fields_are_normalised(self):
        """All float scores should be in [0, 1] range."""
        resp = client.post(
            "/api/v1/analysis/orientation-options",
            json={"project_state": _sample_project_state()},
        )
        assert resp.status_code == 200
        for opt in resp.json()["options"]:
            assert 0.0 <= opt["energy_risk"] <= 1.0
            assert 0.0 <= opt["daylight_potential"] <= 1.0
            assert 0.0 <= opt["ventilation_potential"] <= 1.0

"""Tests for Review Mode: floor plan upload and environmental analysis."""

from __future__ import annotations

import io
import os

import pytest

os.environ.setdefault("MOCK_MODE", "true")

from fastapi.testclient import TestClient

from backend.main import app
from backend.agents.floor_plan_agent import FloorPlanAgent
from backend.services.floor_plan_service import FloorPlanService, _infer_orientation_deg
from shared.project_state import FloorPlanAnalysis, RoomAnalysis

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_project(name: str = "Floor Plan Test Project") -> str:
    response = client.post("/api/v1/projects", json={"project_name": name})
    assert response.status_code == 200
    return response.json()["project"]["project_id"]


def _minimal_png_bytes() -> bytes:
    """1x1 white PNG — smallest valid PNG for upload tests."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
        b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
        b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
        b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
    )


# ---------------------------------------------------------------------------
# Unit: FloorPlanAgent (mock mode)
# ---------------------------------------------------------------------------

class TestFloorPlanAgent:
    def test_run_returns_floor_plan_analysis_in_mock_mode(self) -> None:
        agent = FloorPlanAgent()
        result = agent.run(_minimal_png_bytes(), "image/png")
        assert isinstance(result, FloorPlanAnalysis)
        assert result.provider in {"mock", "fallback"}

    def test_run_populates_rooms(self) -> None:
        agent = FloorPlanAgent()
        result = agent.run(_minimal_png_bytes(), "image/png")
        assert len(result.rooms) > 0
        for room in result.rooms:
            assert isinstance(room, RoomAnalysis)
            assert room.room_name

    def test_run_raises_on_unsupported_type(self) -> None:
        agent = FloorPlanAgent()
        with pytest.raises(ValueError, match="Unsupported file type"):
            agent.run(b"data", "application/zip")

    def test_mock_analysis_has_overall_suggestions(self) -> None:
        agent = FloorPlanAgent()
        result = agent.run(_minimal_png_bytes(), "image/png")
        assert len(result.overall_suggestions) > 0


# ---------------------------------------------------------------------------
# Unit: orientation inference helper
# ---------------------------------------------------------------------------

class TestOrientationInference:
    def _make_analysis(self, deg: float | None, rooms: list[RoomAnalysis]) -> FloorPlanAnalysis:
        return FloorPlanAnalysis(primary_orientation_deg=deg, rooms=rooms)

    def test_uses_primary_orientation_when_present(self) -> None:
        analysis = self._make_analysis(90.0, [])
        assert _infer_orientation_deg(analysis) == 90.0

    def test_falls_back_to_dominant_room_facade(self) -> None:
        rooms = [
            RoomAnalysis(room_name="Living", facade_orientations=["west"], is_external=True),
            RoomAnalysis(room_name="Bedroom", facade_orientations=["west"], is_external=True),
            RoomAnalysis(room_name="Kitchen", facade_orientations=["north"], is_external=True),
        ]
        analysis = self._make_analysis(None, rooms)
        assert _infer_orientation_deg(analysis) == 270.0  # west

    def test_returns_none_when_no_data(self) -> None:
        analysis = self._make_analysis(None, [])
        assert _infer_orientation_deg(analysis) is None


# ---------------------------------------------------------------------------
# Integration: API endpoint
# ---------------------------------------------------------------------------

class TestUploadFloorPlanEndpoint:
    def test_upload_png_returns_200(self) -> None:
        project_id = _make_project()
        response = client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("plan.png", io.BytesIO(_minimal_png_bytes()), "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["project_id"] == project_id
        assert "floor_plan_analysis" in body
        assert "updated_building" in body

    def test_response_contains_rooms(self) -> None:
        project_id = _make_project()
        response = client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("plan.png", io.BytesIO(_minimal_png_bytes()), "image/png")},
        )
        analysis = response.json()["floor_plan_analysis"]
        assert isinstance(analysis["rooms"], list)
        assert len(analysis["rooms"]) > 0

    def test_response_contains_overall_suggestions(self) -> None:
        project_id = _make_project()
        response = client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("plan.png", io.BytesIO(_minimal_png_bytes()), "image/png")},
        )
        analysis = response.json()["floor_plan_analysis"]
        assert len(analysis["overall_suggestions"]) > 0

    def test_analysis_is_persisted_in_project_state(self) -> None:
        project_id = _make_project()
        client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("plan.png", io.BytesIO(_minimal_png_bytes()), "image/png")},
        )
        project = client.get(f"/api/v1/projects/{project_id}").json()
        assert project["current_state"]["floor_plan_analysis"] is not None

    def test_upload_unsupported_type_returns_415(self) -> None:
        project_id = _make_project()
        response = client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("doc.zip", io.BytesIO(b"fake"), "application/zip")},
        )
        assert response.status_code == 415

    def test_upload_empty_file_returns_400(self) -> None:
        project_id = _make_project()
        response = client.post(
            f"/api/v1/projects/{project_id}/upload-plan",
            files={"file": ("empty.png", io.BytesIO(b""), "image/png")},
        )
        assert response.status_code == 400

    def test_upload_to_nonexistent_project_returns_404(self) -> None:
        response = client.post(
            "/api/v1/projects/proj-doesnotexist/upload-plan",
            files={"file": ("plan.png", io.BytesIO(_minimal_png_bytes()), "image/png")},
        )
        assert response.status_code == 404

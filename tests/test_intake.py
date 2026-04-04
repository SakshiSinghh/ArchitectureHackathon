from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_intake_parse_manual_mode() -> None:
    response = client.post(
        "/api/v1/intake/parse",
        json={
            "input_mode": "manual_form",
            "payload": {
                "project_name": "Hackathon Tower",
                "location_name": "Bengaluru",
                "building_type": "office",
                "width_m": 22,
                "depth_m": 28,
                "height_m": 30,
                "floors": 8,
                "orientation_deg": 120,
                "window_to_wall_ratio": 0.4,
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    project = payload["project_state"]
    assert project["project_name"] == "Hackathon Tower"
    assert project["input_mode"] == "manual_form"
    assert "validation_issues" in payload
    assert payload["parse_metadata"]["input_mode"] == "manual_form"
    assert "defaulted_fields" in payload["provenance"]
    assert "unresolved_fields" in payload["provenance"]


def test_intake_parse_uploaded_json_invalid_schema() -> None:
    response = client.post(
        "/api/v1/intake/parse",
        json={
            "input_mode": "uploaded_json",
            "payload": {
                "project_name": "Broken Input",
                "site": "not-an-object",
            },
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "canonical schema" in detail.lower()


def test_intake_pasted_brief_reports_uncertainty() -> None:
    response = client.post(
        "/api/v1/intake/parse",
        json={
            "input_mode": "pasted_brief",
            "payload": "A conceptual office block with daylight goals but no fixed dimensions.",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["parse_metadata"]["input_mode"] == "pasted_brief"
    assert payload["parse_metadata"]["extraction_confidence"] in {"low", "medium"}

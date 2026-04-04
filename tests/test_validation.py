from backend.services.validation_service import validate_project_state
from shared.project_state import ProjectState


def test_validation_flags_missing_site_location() -> None:
    state = ProjectState()
    issues = validate_project_state(state)

    fields = [issue.field for issue in issues]
    assert "site.location_name" in fields


def test_validation_flags_invalid_orientation_and_coordinates() -> None:
    state = ProjectState()
    state.site.location_name = "Pune"
    state.site.latitude = 120
    state.site.longitude = 250
    state.building.orientation_deg = 400

    issues = validate_project_state(state)
    fields = [issue.field for issue in issues]
    assert "site.latitude" in fields
    assert "site.longitude" in fields
    assert "building.orientation_deg" in fields


def test_validation_detects_height_constraint_conflict() -> None:
    state = ProjectState()
    state.site.location_name = "Pune"
    state.building.building_type = "office"
    state.building.width_m = 20
    state.building.depth_m = 25
    state.building.height_m = 60
    state.building.orientation_deg = 90
    state.constraints["hard_constraints"] = ["max height 30m"]

    issues = validate_project_state(state)
    conflict_messages = [issue.message for issue in issues if issue.field == "constraints.hard_constraints"]
    assert any("exceeds hard constraint" in message.lower() for message in conflict_messages)

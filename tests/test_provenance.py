from backend.services.intake_service import parse_intake


def test_provenance_tracks_defaulted_and_unresolved_fields() -> None:
    result = parse_intake(
        "manual_form",
        {
            "project_name": "Demo",
            "location_name": "Bengaluru",
            "building_type": "office",
            "width_m": 20,
            "depth_m": 30,
            "height_m": 25,
            "orientation_deg": 90,
        },
    )

    provenance = result.project_state.provenance
    assert "building.window_to_wall_ratio" in provenance.defaulted_fields
    assert "site.latitude" in provenance.unresolved_fields
    assert "site.longitude" in provenance.unresolved_fields

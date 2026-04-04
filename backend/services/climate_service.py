"""Climate context service with mock-first behavior for MVP."""

from __future__ import annotations

from shared.project_state import Site


def get_climate_context(site: Site) -> dict[str, str | float]:
    """Return lightweight climate context; no external dependency required."""

    location = site.location_name or "Unknown"
    return {
        "location": location,
        "cooling_pressure": 0.55,
        "solar_exposure": 0.6,
        "wind_potential": 0.5,
        "note": "Phase 0 mock climate context. Replace with API-backed data in later phases.",
    }

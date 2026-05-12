"""Orientation sweep service: rank 8 compass orientations and return top 3."""

from __future__ import annotations

import copy

from backend.schemas.api_models import OrientationOption, OrientationOptionsResponse
from backend.services.climate_service import get_climate_context
from backend.services.scoring_service import compute_baseline
from shared.project_state import ProjectState

_LABELS: dict[float, str] = {
    0.0: "North",
    45.0: "North-East",
    90.0: "East",
    135.0: "South-East",
    180.0: "South",
    225.0: "South-West",
    270.0: "West",
    315.0: "North-West",
}

_CANDIDATES = list(_LABELS.keys())


def _composite(energy_risk: float, daylight: float, ventilation: float, priorities) -> float:
    """Weighted composite: higher = better overall option."""
    return (
        priorities.daylight * daylight
        + priorities.ventilation * ventilation
        - priorities.energy * energy_risk
    )


def _short_narrative(label: str, energy_risk: float, daylight: float, ventilation: float) -> str:
    """One-sentence heuristic narrative for each orientation option."""
    if energy_risk >= 0.65:
        return f"{label}-facing orientation carries high energy risk — strong shading strategy required."
    if daylight < 0.45:
        return f"{label}-facing orientation limits daylight — consider increasing glazing ratio."
    if ventilation < 0.45:
        return f"{label}-facing orientation restricts ventilation — prioritise cross-ventilation openings."
    return f"{label}-facing orientation offers a balanced environmental baseline."


def get_orientation_options(project: ProjectState) -> OrientationOptionsResponse:
    """Run baseline for all 8 compass orientations and return the top 3 ranked.

    The user's current orientation is always included and flagged is_current=True.
    Climate data is fetched once and reused across all sweeps.
    """

    climate = get_climate_context(project.site)
    current_deg = float(project.building.orientation_deg or 0.0)
    candidates = list(_CANDIDATES)

    # Ensure current orientation is evaluated even if off-grid
    if current_deg not in candidates:
        candidates.append(current_deg)

    scored: list[dict] = []
    for deg in candidates:
        variant = copy.deepcopy(project)
        variant.building.orientation_deg = deg
        baseline = compute_baseline(variant, climate)

        energy = float(baseline.energy_risk or 0.0)
        daylight = float(baseline.daylight_potential or 0.0)
        ventilation = float(baseline.ventilation_potential or 0.0)
        composite = _composite(energy, daylight, ventilation, project.priorities)
        label = _LABELS.get(deg, f"{deg:.0f} deg")

        scored.append({
            "orientation_deg": deg,
            "label": label,
            "energy_risk": round(energy, 3),
            "daylight_potential": round(daylight, 3),
            "ventilation_potential": round(ventilation, 3),
            "composite_score": round(composite, 4),
            "narrative": _short_narrative(label, energy, daylight, ventilation),
            "is_current": deg == current_deg,
        })

    scored.sort(key=lambda x: x["composite_score"], reverse=True)

    # Always show top 3 from the ranked list; current orientation included regardless
    top3_degs = {s["orientation_deg"] for s in scored[:3]}
    if current_deg not in top3_degs:
        # Replace rank-3 with current so user always sees where they stand
        top3 = scored[:2] + [s for s in scored if s["is_current"]]
    else:
        top3 = scored[:3]

    # Assign final ranks
    options = []
    for rank, item in enumerate(top3, start=1):
        options.append(OrientationOption(rank=rank, **item))

    recommended = options[0].orientation_deg

    return OrientationOptionsResponse(
        options=options,
        recommended_orientation_deg=recommended,
        location=project.site.location_name,
    )

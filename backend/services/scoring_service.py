"""Simple baseline scoring heuristics for MVP demonstration."""

from __future__ import annotations

from shared.project_state import BaselineResults, ProjectState


def compute_baseline(project: ProjectState, climate: dict[str, float | str]) -> BaselineResults:
    """Compute deterministic heuristic outputs for baseline analysis."""

    orientation = project.building.orientation_deg or 0
    wwr = project.building.window_to_wall_ratio if project.building.window_to_wall_ratio is not None else 0.35

    orientation_penalty = abs((orientation % 180) - 90) / 90
    energy_risk = min(1.0, 0.35 + 0.4 * orientation_penalty + 0.3 * wwr)

    daylight_potential = max(0.0, min(1.0, 0.4 + 0.6 * wwr))
    ventilation_potential = 0.5 + (0.1 if (project.building.depth_m or 0) < 18 else -0.1)
    ventilation_potential = max(0.0, min(1.0, ventilation_potential))

    if energy_risk >= 0.7:
        narrative = "High cooling-risk pattern detected; prioritize envelope and shading mitigation first."
    elif daylight_potential < 0.45:
        narrative = "Daylight potential is limited; consider facade and depth adjustments before locking constraints."
    else:
        narrative = "Current massing is balanced for Phase 1 heuristics; refine trade-offs with stakeholder priorities."

    return BaselineResults(
        summary="Phase 2 heuristic baseline (not simulation-grade).",
        energy_risk=round(energy_risk, 3),
        daylight_potential=round(daylight_potential, 3),
        ventilation_potential=round(ventilation_potential, 3),
        narrative_insight=narrative,
    )

"""Simple baseline scoring heuristics with optional LLM narrative."""

from __future__ import annotations

from typing import Any

from shared.project_state import BaselineResults, ProjectState
from backend.services.llm_service import LLMService


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def compute_baseline(project: ProjectState, climate: dict[str, Any]) -> BaselineResults:
    """Compute heuristic baseline metrics, then enrich narrative with LLM if available."""

    orientation = project.building.orientation_deg or 0
    wwr = project.building.window_to_wall_ratio if project.building.window_to_wall_ratio is not None else 0.35
    metrics = climate.get("environmental_metrics") or {}

    heat_exposure = float(metrics.get("heat_exposure_score") or 0.5)
    solar_exposure = float(metrics.get("solar_exposure_score") or 0.5)
    ventilation_context = float(metrics.get("ventilation_potential_score") or 0.5)

    orientation_penalty = abs((orientation % 180) - 90) / 90
    energy_risk = _clamp(0.25 + 0.3 * orientation_penalty + 0.2 * wwr + 0.25 * heat_exposure + 0.1 * solar_exposure)

    daylight_potential = _clamp(0.35 + 0.5 * wwr + 0.15 * solar_exposure)
    depth_adjustment = 0.08 if (project.building.depth_m or 0) < 18 else -0.08
    ventilation_potential = _clamp(0.45 + 0.35 * ventilation_context + depth_adjustment)

    if energy_risk >= 0.7:
        heuristic_narrative = (
            "Heat exposure and orientation indicate elevated cooling risk; "
            "prioritize facade shading and heat-gain control."
        )
    elif daylight_potential < 0.45:
        heuristic_narrative = (
            "Daylight potential remains limited relative to glazing/context; "
            "tune facade balance and depth before locking constraints."
        )
    elif ventilation_potential < 0.45:
        heuristic_narrative = (
            "Ventilation potential is constrained by wind/depth context; "
            "prioritize cross-ventilation and operable facade strategy."
        )
    else:
        heuristic_narrative = (
            "Current baseline is relatively balanced; "
            "refine trade-offs against stakeholder priorities."
        )

    narrative = (
        _llm_narrative(
            project, energy_risk, daylight_potential, ventilation_potential,
            heat_exposure, solar_exposure, ventilation_context,
        )
        or heuristic_narrative
    )

    return BaselineResults(
        summary="Climate-informed heuristic baseline (not simulation-grade).",
        energy_risk=round(energy_risk, 3),
        daylight_potential=round(daylight_potential, 3),
        ventilation_potential=round(ventilation_potential, 3),
        climate_provider=climate.get("provider"),
        heat_exposure_score=round(heat_exposure, 3),
        solar_exposure_score=round(solar_exposure, 3),
        climate_ventilation_score=round(ventilation_context, 3),
        narrative_insight=narrative,
    )


def _llm_narrative(
    project: ProjectState,
    energy_risk: float,
    daylight_potential: float,
    ventilation_potential: float,
    heat_exposure: float,
    solar_exposure: float,
    ventilation_context: float,
) -> str | None:
    """Return an LLM-generated narrative insight, or None when unavailable."""

    llm = LLMService()
    constraints = project.constraints.get("hard_constraints") or []
    constraint_text = ", ".join(constraints[:3]) if constraints else "none specified"

    lines = [
        "You are an environmental design consultant.",
        "Write a 2-sentence plain-language insight for an architect reviewing their early-stage building design.",
        "",
        f"Building: {project.building.building_type or 'unspecified'}, "
        f"{project.building.floors or '?'} floors, "
        f"orientation {project.building.orientation_deg or '?'} degrees.",
        f"Location: {project.site.location_name or 'unspecified'}.",
        "Key scores (0=best, 1=worst for risk; 0=worst, 1=best for potential):",
        f"  Energy risk: {energy_risk:.2f} | Daylight potential: {daylight_potential:.2f} | "
        f"Ventilation potential: {ventilation_potential:.2f}",
        f"  Heat exposure: {heat_exposure:.2f} | Solar exposure: {solar_exposure:.2f} | "
        f"Ventilation context: {ventilation_context:.2f}",
        f"Hard constraints: {constraint_text}",
        "",
        "Focus on the most critical issue and one actionable next step. "
        "Be specific and avoid generic advice. Do not use bullet points.",
    ]
    prompt = "\n".join(lines)

    result = llm.generate(prompt)
    if result.startswith("["):
        return None
    return result

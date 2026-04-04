"""Constraint agent: estimate penalties from hard constraints."""

from __future__ import annotations

from shared.project_state import ProjectState


class ConstraintAgent:
    """Calculates deterministic penalties from hard constraints."""

    def run(self, project: ProjectState) -> dict[str, float | str]:
        count = len(project.constraints.get("hard_constraints", []))
        energy_penalty = min(0.25, 0.04 * count)
        daylight_penalty = min(0.2, 0.03 * count)
        ventilation_penalty = min(0.15, 0.02 * count)

        for constraint in project.constraints.get("hard_constraints", []):
            normalized = constraint.lower()
            if "max height" in normalized or "setback" in normalized:
                daylight_penalty += 0.03
            if "orientation" in normalized:
                energy_penalty += 0.04
            if "sealed facade" in normalized or "no operable window" in normalized:
                ventilation_penalty += 0.05

        energy_penalty = min(0.35, energy_penalty)
        daylight_penalty = min(0.3, daylight_penalty)
        ventilation_penalty = min(0.25, ventilation_penalty)

        total_penalty = min(1.0, energy_penalty + daylight_penalty + ventilation_penalty)
        return {
            "penalty": round(total_penalty, 3),
            "energy_penalty": round(energy_penalty, 3),
            "daylight_penalty": round(daylight_penalty, 3),
            "ventilation_penalty": round(ventilation_penalty, 3),
            "note": "Constraint penalties are heuristic and derived from hard-constraint intensity/keywords.",
        }

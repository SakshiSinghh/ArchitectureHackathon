"""Compensation agent: generate mitigation options."""

from __future__ import annotations

from shared.project_state import ProjectState


class CompensationAgent:
    """Returns grounded mitigation candidates from baseline/context signals."""

    def run(self, project: ProjectState) -> list[dict]:
        baseline = project.baseline_results
        options: list[dict] = []

        if (baseline.energy_risk or 0) >= 0.6:
            options.append(
                {
                    "title": "Add external shading on high-exposure facade",
                    "description": "Increase shading depth and prioritize west/south facade control.",
                    "expected_benefit": "Reduces cooling pressure and peak heat gains.",
                    "tradeoff_note": "Adds facade complexity and moderate cost increase.",
                    "rationale": "Triggered by high baseline energy risk.",
                    "energy_gain": 0.28,
                    "daylight_gain": -0.05,
                    "ventilation_gain": 0.02,
                    "cost_penalty": 0.18,
                    "aesthetics_penalty": 0.08,
                }
            )

        if (baseline.daylight_potential or 0) <= 0.5:
            options.append(
                {
                    "title": "Rebalance glazing and interior depth",
                    "description": "Increase useful glazing on low-risk orientation and reduce overly deep zones.",
                    "expected_benefit": "Improves daylight distribution in occupied zones.",
                    "tradeoff_note": "Can increase cooling risk if not paired with shading.",
                    "rationale": "Triggered by low baseline daylight potential.",
                    "energy_gain": 0.06,
                    "daylight_gain": 0.24,
                    "ventilation_gain": 0.04,
                    "cost_penalty": 0.12,
                    "aesthetics_penalty": 0.05,
                }
            )

        if (baseline.ventilation_potential or 0) <= 0.5:
            options.append(
                {
                    "title": "Enable cross-ventilation strategy",
                    "description": "Adjust core/wall openings and reduce deep-plan obstruction where feasible.",
                    "expected_benefit": "Improves passive ventilation potential.",
                    "tradeoff_note": "May constrain rentable floor efficiency.",
                    "rationale": "Triggered by weak baseline ventilation potential.",
                    "energy_gain": 0.1,
                    "daylight_gain": 0.08,
                    "ventilation_gain": 0.25,
                    "cost_penalty": 0.1,
                    "aesthetics_penalty": 0.04,
                }
            )

        if not options:
            options.append(
                {
                    "title": "Fine-tune facade controls",
                    "description": "Apply modest shading and glazing tuning without changing core massing.",
                    "expected_benefit": "Balanced incremental performance improvement.",
                    "tradeoff_note": "Smaller gains than geometry-level changes.",
                    "rationale": "Used when baseline signals are balanced and no dominant issue is detected.",
                    "energy_gain": 0.08,
                    "daylight_gain": 0.08,
                    "ventilation_gain": 0.08,
                    "cost_penalty": 0.05,
                    "aesthetics_penalty": 0.03,
                }
            )

        return options[:3]

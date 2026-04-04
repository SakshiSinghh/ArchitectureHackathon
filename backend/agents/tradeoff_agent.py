"""Trade-off agent: rank mitigation options against priorities."""

from __future__ import annotations

from shared.project_state import ProjectState


class TradeoffAgent:
    """Applies deterministic trade-off ranking from project priorities."""

    def run(self, project: ProjectState, options: list[dict]) -> list[dict]:
        ranked: list[dict] = []
        for option in options:
            score = (
                project.priorities.energy * option.get("energy_gain", 0)
                + project.priorities.daylight * option.get("daylight_gain", 0)
                + project.priorities.ventilation * option.get("ventilation_gain", 0)
                - project.priorities.cost * option.get("cost_penalty", 0)
                - project.priorities.aesthetics * option.get("aesthetics_penalty", 0)
            )
            enriched = dict(option)
            enriched["score"] = round(score, 4)
            enriched["tradeoff_explanation"] = (
                f"Score favors gains aligned to priorities (energy={project.priorities.energy}, "
                f"daylight={project.priorities.daylight}, ventilation={project.priorities.ventilation}) "
                "while subtracting cost/aesthetics penalties."
            )
            ranked.append(enriched)

        ranked.sort(key=lambda item: item.get("score", 0), reverse=True)
        return ranked

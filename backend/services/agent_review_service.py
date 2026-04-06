"""Explicit post-baseline agent review pipeline for Phase 2 MVP."""

from __future__ import annotations

from backend.agents.compensation_agent import CompensationAgent
from backend.agents.constraint_agent import ConstraintAgent
from backend.agents.tradeoff_agent import TradeoffAgent
from backend.schemas.api_models import (
    AgentReviewResponse,
    MetricsDelta,
    MetricsSnapshot,
    RankedMitigation,
)
from shared.project_state import ProjectState


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def run_agent_review(project: ProjectState) -> AgentReviewResponse:
    """Run deterministic constraint -> compensation -> trade-off review."""

    climate_metrics = project.climate_context.get("environmental_metrics") or {}
    heat_exposure = float(climate_metrics.get("heat_exposure_score") or 0.5)
    solar_exposure = float(climate_metrics.get("solar_exposure_score") or 0.5)
    ventilation_context = float(climate_metrics.get("ventilation_potential_score") or 0.5)

    baseline_energy = float(project.baseline_results.energy_risk or 0.0)
    baseline_daylight = float(project.baseline_results.daylight_potential or 0.0)
    baseline_ventilation = float(project.baseline_results.ventilation_potential or 0.0)

    baseline_metrics = MetricsSnapshot(
        energy_risk=round(baseline_energy, 3),
        daylight_potential=round(baseline_daylight, 3),
        ventilation_potential=round(baseline_ventilation, 3),
    )

    constraint_result = ConstraintAgent().run(project)

    constrained_metrics = MetricsSnapshot(
        energy_risk=round(_clamp(baseline_energy + float(constraint_result["energy_penalty"])), 3),
        daylight_potential=round(_clamp(baseline_daylight - float(constraint_result["daylight_penalty"])), 3),
        ventilation_potential=round(_clamp(baseline_ventilation - float(constraint_result["ventilation_penalty"])), 3),
    )

    deltas = MetricsDelta(
        energy_risk_delta=round(constrained_metrics.energy_risk - baseline_metrics.energy_risk, 3),
        daylight_potential_delta=round(constrained_metrics.daylight_potential - baseline_metrics.daylight_potential, 3),
        ventilation_potential_delta=round(
            constrained_metrics.ventilation_potential - baseline_metrics.ventilation_potential, 3
        ),
    )

    options = CompensationAgent().run(project)
    ranked = TradeoffAgent().run(project, options)

    ranked_options: list[RankedMitigation] = []
    for index, option in enumerate(ranked, start=1):
        ranked_options.append(
            RankedMitigation(
                rank=index,
                title=option.get("title", "Untitled mitigation"),
                description=option.get("description", ""),
                rationale=option.get("rationale", "Heuristic mitigation rationale."),
                expected_benefit=option.get("expected_benefit", ""),
                tradeoff_note=option.get("tradeoff_note", ""),
                score=float(option.get("score", 0.0)),
            )
        )

    top_option_reason = (
        f"Top option is ranked highest by weighted priority score ({ranked_options[0].score}) "
        f"with rationale: {ranked_options[0].rationale}. "
        f"Climate context: heat={heat_exposure:.2f}, solar={solar_exposure:.2f}, ventilation={ventilation_context:.2f}."
        if ranked_options
        else "No mitigation option available for current state."
    )

    penalty_summary = (
        "Constraint penalties increased energy risk and reduced daylight/ventilation potential. "
        f"Penalty score={constraint_result['penalty']}. {constraint_result['note']}"
    )

    return AgentReviewResponse(
        baseline_metrics=baseline_metrics,
        constrained_metrics=constrained_metrics,
        metric_deltas=deltas,
        penalty_summary=penalty_summary,
        ranked_options=ranked_options,
        top_option_reason=top_option_reason,
    )

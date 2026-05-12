"""Explicit post-baseline agent review pipeline for Phase 2 MVP."""

from __future__ import annotations

from backend.agents.compensation_agent import CompensationAgent
from backend.services.llm_service import LLMService
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

    if ranked_options:
        heuristic_top_reason = (
            f"Top option is ranked highest by weighted priority score ({ranked_options[0].score}) "
            f"with rationale: {ranked_options[0].rationale}. "
            f"Climate context: heat={heat_exposure:.2f}, solar={solar_exposure:.2f}, ventilation={ventilation_context:.2f}."
        )
        top_option_reason = (
            _llm_top_reason(ranked_options[0], deltas, project)
            or heuristic_top_reason
        )
    else:
        top_option_reason = "No mitigation option available for current state."

    heuristic_penalty = (
        "Constraint penalties increased energy risk and reduced daylight/ventilation potential. "
        f"Penalty score={constraint_result['penalty']}. {constraint_result['note']}"
    )
    penalty_summary = (
        _llm_penalty_summary(constraint_result, deltas, project)
        or heuristic_penalty
    )

    return AgentReviewResponse(
        baseline_metrics=baseline_metrics,
        constrained_metrics=constrained_metrics,
        metric_deltas=deltas,
        penalty_summary=penalty_summary,
        ranked_options=ranked_options,
        top_option_reason=top_option_reason,
    )


def _llm_top_reason(top: RankedMitigation, deltas: MetricsDelta, project: ProjectState) -> str | None:
    """Return an LLM-generated explanation for why the top mitigation option was chosen."""

    llm = LLMService()
    lines = [
        "You are an environmental design consultant. Write 2 plain-language sentences explaining",
        "to an architect why this mitigation strategy was selected as the top recommendation.",
        "",
        f"Top strategy: {top.title}",
        f"Description: {top.description}",
        f"Expected benefit: {top.expected_benefit}",
        f"Trade-off: {top.tradeoff_note}",
        f"Priority score: {top.score:.3f}",
        "Constraint-adjusted metric changes:",
        f"  Energy risk delta: {deltas.energy_risk_delta:+.3f}",
        f"  Daylight potential delta: {deltas.daylight_potential_delta:+.3f}",
        f"  Ventilation potential delta: {deltas.ventilation_potential_delta:+.3f}",
        f"Building: {project.building.building_type or 'unspecified'}, ",
        f"orientation {project.building.orientation_deg or '?'}deg, ",
        f"location: {project.site.location_name or 'unspecified'}",
        "",
        "Be specific about what this strategy addresses and why it fits this project best.",
        "Do not use bullet points.",
    ]
    result = llm.generate("\n".join(lines))
    if result.startswith("["):
        return None
    return result


def _llm_penalty_summary(
    constraint_result: dict, deltas: MetricsDelta, project: ProjectState
) -> str | None:
    """Return an LLM-generated constraint penalty summary."""

    llm = LLMService()
    constraints = project.constraints.get("hard_constraints") or []
    constraint_text = ", ".join(constraints[:3]) if constraints else "none"
    lines = [
        "You are an environmental design consultant. Write 1-2 plain-language sentences summarising",
        "the performance impact of the architect's design constraints.",
        "",
        f"Hard constraints applied: {constraint_text}",
        f"Penalty score: {constraint_result.get('penalty', 0)}",
        f"Note: {constraint_result.get('note', '')}",
        "Constraint-adjusted metric changes:",
        f"  Energy risk: {deltas.energy_risk_delta:+.3f}",
        f"  Daylight potential: {deltas.daylight_potential_delta:+.3f}",
        f"  Ventilation potential: {deltas.ventilation_potential_delta:+.3f}",
        "",
        "If penalties are zero, say the constraints have no measurable performance cost.",
        "Be concise and practical. Do not use bullet points.",
    ]
    result = llm.generate("\n".join(lines))
    if result.startswith("["):
        return None
    return result

"""API request/response models for intake and baseline endpoints."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from shared.project_state import (
    InputMode,
    ParsedConstraints,
    ProjectState,
    Provenance,
    ValidationIssue,
)


class IntakeRequest(BaseModel):
    """Payload for intake parse endpoint."""

    input_mode: InputMode
    payload: Any


class ParseMetadata(BaseModel):
    """Describes parser behavior and confidence for MVP explainability."""

    input_mode: InputMode
    parser_note: str
    extraction_confidence: Literal["low", "medium", "high"]
    unparsed_items: list[str] = Field(default_factory=list)


class IntakeResponse(BaseModel):
    """Normalized state plus parse metadata and validation details."""

    project_state: ProjectState
    validation_issues: list[ValidationIssue]
    assumptions: list[str]
    provenance: Provenance
    parse_metadata: ParseMetadata


class BaselineRequest(BaseModel):
    """Payload for baseline analysis endpoint."""

    confirmed: bool = False
    project_state: ProjectState


class BaselineResponse(BaseModel):
    """Baseline analysis response for frontend display."""

    project_state: ProjectState


class MetricsSnapshot(BaseModel):
    """Compact metrics payload used for baseline/constrained comparisons."""

    energy_risk: float
    daylight_potential: float
    ventilation_potential: float


class MetricsDelta(BaseModel):
    """Delta between constrained and baseline metrics."""

    energy_risk_delta: float
    daylight_potential_delta: float
    ventilation_potential_delta: float


class RankedMitigation(BaseModel):
    """Mitigation option enriched with ranking explanation."""

    rank: int
    title: str
    description: str
    rationale: str
    expected_benefit: str
    tradeoff_note: str
    score: float


class AgentReviewRequest(BaseModel):
    """Request payload for explicit post-baseline agent review stage."""

    project_state: ProjectState


class AgentReviewResponse(BaseModel):
    """Structured output from constraint, compensation, and trade-off review."""

    baseline_metrics: MetricsSnapshot
    constrained_metrics: MetricsSnapshot
    metric_deltas: MetricsDelta
    penalty_summary: str
    ranked_options: list[RankedMitigation]
    top_option_reason: str


class ConstraintInterpretRequest(BaseModel):
    """Request payload for free-text constraint interpretation."""

    project_state: ProjectState
    preferred_provider: str | None = None


class ConstraintInterpretResponse(BaseModel):
    """Response payload for interpreted constraint candidates."""

    parsed_constraints: ParsedConstraints

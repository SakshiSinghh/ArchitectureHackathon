"""Canonical project state schemas for MVP workflows."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

InputMode = Literal["manual_form", "pasted_brief", "uploaded_json"]


class Site(BaseModel):
    """Location and climate context fields."""

    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    climate_notes: str | None = None


class Building(BaseModel):
    """Lightweight geometry fields for MVP."""

    building_type: str | None = None
    width_m: float | None = None
    depth_m: float | None = None
    height_m: float | None = None
    floors: int | None = None
    orientation_deg: float | None = None
    window_to_wall_ratio: float | None = None
    geometry_notes: str | None = None


class Priorities(BaseModel):
    """Relative weights for trade-off ranking."""

    energy: float = 0.25
    daylight: float = 0.2
    ventilation: float = 0.2
    cost: float = 0.2
    aesthetics: float = 0.15


class Provenance(BaseModel):
    """Tracks which values were provided vs inferred."""

    user_provided_fields: list[str] = Field(default_factory=list)
    inferred_fields: list[str] = Field(default_factory=list)
    defaulted_fields: list[str] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)


class ValidationIssue(BaseModel):
    """Represents missing fields, conflicts, and weak assumptions."""

    severity: Literal["info", "warning", "error"]
    field: str
    message: str


class BaselineResults(BaseModel):
    """Simple baseline outputs from heuristics."""

    summary: str = "Not computed yet"
    energy_risk: float | None = None
    daylight_potential: float | None = None
    ventilation_potential: float | None = None
    climate_provider: str | None = None
    heat_exposure_score: float | None = None
    solar_exposure_score: float | None = None
    climate_ventilation_score: float | None = None
    narrative_insight: str | None = None


class MitigationOption(BaseModel):
    """Candidate mitigation with lightweight scoring hints."""

    title: str
    description: str
    expected_benefit: str
    tradeoff_note: str


class ParsedConstraintItem(BaseModel):
    """Single interpreted constraint candidate from free-text parsing."""

    source_text: str
    normalized_key: str
    normalized_value: str | bool | float | int | None = None
    confidence: float = 0.0
    rationale: str = ""
    status: Literal["proposed", "accepted", "rejected", "edited"] = "proposed"


class ParsedConstraints(BaseModel):
    """Structured parsing result with transparency metadata."""

    extracted_items: list[ParsedConstraintItem] = Field(default_factory=list)
    unresolved_items: list[str] = Field(default_factory=list)
    confidence_label: Literal["low", "medium", "high"] = "low"
    confidence_score: float = 0.0
    parser_provider: str = "none"
    parser_mode: Literal["llm", "heuristic", "fallback", "none"] = "none"
    notes: list[str] = Field(default_factory=list)
    conflict_warnings: list[str] = Field(default_factory=list)


class ProjectState(BaseModel):
    """Canonical state used across intake, analysis, and agent steps."""

    project_name: str = "Untitled Project"
    input_mode: InputMode = "manual_form"
    brief_text: str | None = None
    site: Site = Field(default_factory=Site)
    building: Building = Field(default_factory=Building)
    constraints: dict[str, Any] = Field(
        default_factory=lambda: {
            "hard_constraints": [],
            "soft_constraints": [],
            "free_text": "",
            "structured_enabled": True,
            "notes": None,
        }
    )
    priorities: Priorities = Field(default_factory=Priorities)
    provenance: Provenance = Field(default_factory=Provenance)
    assumptions: list[str] = Field(default_factory=list)
    validation_issues: list[ValidationIssue] = Field(default_factory=list)
    parsed_constraints: ParsedConstraints = Field(default_factory=ParsedConstraints)
    climate_context: dict[str, Any] = Field(default_factory=dict)
    baseline_results: BaselineResults = Field(default_factory=BaselineResults)
    mitigation_options: list[MitigationOption] = Field(default_factory=list)

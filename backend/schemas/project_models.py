"""Project workspace request/response models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from backend.schemas.api_models import AgentReviewResponse
from shared.project_state import ProjectState


class ProjectMeta(BaseModel):
    """Lightweight metadata for project listing and workspace context."""

    project_id: str
    project_name: str
    created_at: datetime
    updated_at: datetime
    notes: str | None = None


class ProjectSummaryResponse(BaseModel):
    """List item for project selection in workspace UI."""

    project_id: str
    project_name: str
    created_at: datetime
    updated_at: datetime
    run_count: int = 0


class CreateProjectRequest(BaseModel):
    """Payload for creating a new project workspace."""

    project_name: str = Field(min_length=1, max_length=120)
    brief_text: str | None = None
    notes: str | None = None


class UpdateProjectRequest(BaseModel):
    """Payload for saving updated current design state."""

    project_state: ProjectState
    notes: str | None = None


class ProjectDetailResponse(BaseModel):
    """Project detail with current editable state and recent run ids."""

    project: ProjectMeta
    current_state: ProjectState
    recent_run_ids: list[str] = Field(default_factory=list)


class RunSnapshot(BaseModel):
    """Persisted design negotiation cycle output."""

    run_id: str
    created_at: datetime
    input_state: ProjectState
    baseline_state: ProjectState
    agent_review: AgentReviewResponse
    top_recommendation: str | None = None
    climate_provider: str | None = None
    climate_source_tier: str | None = None


class RunDiff(BaseModel):
    """Simple change visibility model between two runs."""

    changed_inputs: list[str] = Field(default_factory=list)
    changed_baseline_metrics: dict[str, dict[str, float | str | None]] = Field(default_factory=dict)
    changed_top_recommendation: dict[str, str | None] = Field(default_factory=dict)
    changed_agent_deltas: dict[str, dict[str, float | None]] = Field(default_factory=dict)


class RunExecutionRequest(BaseModel):
    """Payload for creating a run from current or supplied project state."""

    project_state: ProjectState | None = None


class RunExecutionResponse(BaseModel):
    """Response for a completed run and optional diff against previous run."""

    run: RunSnapshot
    diff_from_previous: RunDiff | None = None


class ProjectRunsResponse(BaseModel):
    """History payload of saved run snapshots."""

    project_id: str
    runs: list[RunSnapshot] = Field(default_factory=list)


class ProjectsListResponse(BaseModel):
    """Top-level list response for project workspace sidebar."""

    projects: list[ProjectSummaryResponse] = Field(default_factory=list)

"""File-backed project persistence and run-history orchestration."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from fastapi import HTTPException

from backend.core.config import settings
from backend.schemas.api_models import AgentReviewResponse
from backend.schemas.project_models import (
    ProjectMeta,
    ProjectSummaryResponse,
    RunDiff,
    RunSnapshot,
)
from backend.services.agent_review_service import run_agent_review
from backend.services.orchestration_service import run_baseline_pipeline
from shared.project_state import ProjectState

_DEFAULT_PROJECTS_DIR = "data/projects"


class ProjectService:
    """Local file-backed project workspace service."""

    def __init__(self, base_dir: str | None = None) -> None:
        resolved_base = base_dir or os.getenv("PROJECTS_DATA_DIR") or settings.projects_data_dir or _DEFAULT_PROJECTS_DIR
        self.base_dir = Path(resolved_base)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list_projects(self) -> list[ProjectSummaryResponse]:
        projects: list[ProjectSummaryResponse] = []
        for project_dir in self._project_dirs():
            meta = self._read_json(project_dir / "project_meta.json")
            run_count = len(list((project_dir / "runs").glob("*.json"))) if (project_dir / "runs").exists() else 0
            projects.append(
                ProjectSummaryResponse(
                    project_id=meta["project_id"],
                    project_name=meta["project_name"],
                    created_at=_parse_datetime(meta["created_at"]),
                    updated_at=_parse_datetime(meta["updated_at"]),
                    run_count=run_count,
                )
            )

        projects.sort(key=lambda item: item.updated_at, reverse=True)
        return projects

    def create_project(self, project_name: str, brief_text: str | None = None, notes: str | None = None) -> dict[str, Any]:
        project_id = f"proj-{uuid4().hex[:10]}"
        project_dir = self.base_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=False)
        (project_dir / "runs").mkdir(parents=True, exist_ok=True)

        now = _utc_now_iso()
        state = ProjectState(project_name=project_name, brief_text=brief_text)

        meta = {
            "project_id": project_id,
            "project_name": project_name,
            "created_at": now,
            "updated_at": now,
            "notes": notes,
        }

        self._write_json(project_dir / "project_meta.json", meta)
        self._write_json(project_dir / "current_state.json", state.model_dump(mode="json"))

        return {
            "project": ProjectMeta(
                project_id=project_id,
                project_name=project_name,
                created_at=_parse_datetime(now),
                updated_at=_parse_datetime(now),
                notes=notes,
            ),
            "current_state": state,
            "recent_run_ids": [],
        }

    def get_project(self, project_id: str) -> dict[str, Any]:
        project_dir = self._project_dir(project_id)
        meta = self._read_json(project_dir / "project_meta.json")
        current_state_payload = self._read_json(project_dir / "current_state.json")
        recent_ids = [run.run_id for run in self.list_runs(project_id)[:8]]

        return {
            "project": ProjectMeta(
                project_id=meta["project_id"],
                project_name=meta["project_name"],
                created_at=_parse_datetime(meta["created_at"]),
                updated_at=_parse_datetime(meta["updated_at"]),
                notes=meta.get("notes"),
            ),
            "current_state": ProjectState.model_validate(current_state_payload),
            "recent_run_ids": recent_ids,
        }

    def update_project(self, project_id: str, state: ProjectState, notes: str | None = None) -> dict[str, Any]:
        project_dir = self._project_dir(project_id)
        meta = self._read_json(project_dir / "project_meta.json")

        state.project_name = state.project_name or meta["project_name"]
        meta["project_name"] = state.project_name
        meta["updated_at"] = _utc_now_iso()
        if notes is not None:
            meta["notes"] = notes

        self._write_json(project_dir / "current_state.json", state.model_dump(mode="json"))
        self._write_json(project_dir / "project_meta.json", meta)

        return self.get_project(project_id)

    def create_run(self, project_id: str, state: ProjectState | None = None) -> tuple[RunSnapshot, RunDiff | None]:
        project_dir = self._project_dir(project_id)
        if state is None:
            current_state_payload = self._read_json(project_dir / "current_state.json")
            state = ProjectState.model_validate(current_state_payload)

        baseline_state = run_baseline_pipeline(state.model_copy(deep=True))
        review = run_agent_review(baseline_state)

        run_id = f"run-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid4().hex[:6]}"
        created_at = _parse_datetime(_utc_now_iso())
        top_recommendation = review.ranked_options[0].title if review.ranked_options else None

        climate_context = baseline_state.climate_context or {}
        snapshot = RunSnapshot(
            run_id=run_id,
            created_at=created_at,
            input_state=state,
            baseline_state=baseline_state,
            agent_review=AgentReviewResponse.model_validate(review.model_dump(mode="json")),
            top_recommendation=top_recommendation,
            climate_provider=climate_context.get("provider"),
            climate_source_tier=climate_context.get("source_tier"),
        )

        run_path = project_dir / "runs" / f"{run_id}.json"
        self._write_json(run_path, snapshot.model_dump(mode="json"))

        # Persist latest state as current working state after analysis cycle.
        self._write_json(project_dir / "current_state.json", baseline_state.model_dump(mode="json"))

        meta = self._read_json(project_dir / "project_meta.json")
        meta["updated_at"] = _utc_now_iso()
        self._write_json(project_dir / "project_meta.json", meta)

        runs = self.list_runs(project_id)
        previous = runs[1] if len(runs) > 1 else None
        diff = diff_runs(snapshot, previous) if previous else None
        return snapshot, diff

    def list_runs(self, project_id: str) -> list[RunSnapshot]:
        project_dir = self._project_dir(project_id)
        runs_dir = project_dir / "runs"
        if not runs_dir.exists():
            return []

        snapshots: list[RunSnapshot] = []
        for run_file in sorted(runs_dir.glob("*.json"), reverse=True):
            payload = self._read_json(run_file)
            snapshots.append(RunSnapshot.model_validate(payload))
        return snapshots

    def _project_dirs(self) -> list[Path]:
        return [path for path in self.base_dir.iterdir() if path.is_dir()]

    def _project_dir(self, project_id: str) -> Path:
        project_dir = self.base_dir / project_id
        if not project_dir.exists() or not project_dir.is_dir():
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")
        return project_dir

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Missing project file: {path.name}")
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)


def diff_runs(current: RunSnapshot, previous: RunSnapshot | None) -> RunDiff:
    """Compute simple change visibility between run snapshots."""

    if previous is None:
        return RunDiff()

    current_inputs = _flatten(current.input_state.model_dump(mode="json"), prefix="state")
    previous_inputs = _flatten(previous.input_state.model_dump(mode="json"), prefix="state")

    changed_inputs: list[str] = []
    all_input_keys = sorted(set(current_inputs) | set(previous_inputs))
    for key in all_input_keys:
        if current_inputs.get(key) != previous_inputs.get(key):
            changed_inputs.append(key)

    current_baseline = current.baseline_state.baseline_results.model_dump(mode="json")
    previous_baseline = previous.baseline_state.baseline_results.model_dump(mode="json")

    baseline_keys = [
        "energy_risk",
        "daylight_potential",
        "ventilation_potential",
        "heat_exposure_score",
        "solar_exposure_score",
        "climate_ventilation_score",
    ]
    changed_baseline_metrics: dict[str, dict[str, float | str | None]] = {}
    for key in baseline_keys:
        if current_baseline.get(key) != previous_baseline.get(key):
            changed_baseline_metrics[key] = {
                "previous": previous_baseline.get(key),
                "current": current_baseline.get(key),
            }

    top_change: dict[str, str | None] = {}
    if current.top_recommendation != previous.top_recommendation:
        top_change = {
            "previous": previous.top_recommendation,
            "current": current.top_recommendation,
        }

    current_deltas = current.agent_review.metric_deltas.model_dump(mode="json")
    previous_deltas = previous.agent_review.metric_deltas.model_dump(mode="json")
    changed_agent_deltas: dict[str, dict[str, float | None]] = {}
    for key, current_value in current_deltas.items():
        previous_value = previous_deltas.get(key)
        if current_value != previous_value:
            changed_agent_deltas[key] = {
                "previous": previous_value,
                "current": current_value,
            }

    return RunDiff(
        changed_inputs=changed_inputs,
        changed_baseline_metrics=changed_baseline_metrics,
        changed_top_recommendation=top_change,
        changed_agent_deltas=changed_agent_deltas,
    )


def _flatten(value: Any, prefix: str) -> dict[str, Any]:
    if isinstance(value, dict):
        output: dict[str, Any] = {}
        for key, nested in value.items():
            output.update(_flatten(nested, f"{prefix}.{key}"))
        return output
    if isinstance(value, list):
        return {prefix: value}
    return {prefix: value}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)

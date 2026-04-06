"""Project workspace routes for file-backed persistence and iteration runs."""

from __future__ import annotations

from fastapi import APIRouter

from backend.schemas.project_models import (
    CreateProjectRequest,
    ProjectDetailResponse,
    ProjectRunsResponse,
    ProjectsListResponse,
    RunExecutionRequest,
    RunExecutionResponse,
    UpdateProjectRequest,
)
from backend.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=ProjectsListResponse)
def list_projects() -> ProjectsListResponse:
    service = ProjectService()
    return ProjectsListResponse(projects=service.list_projects())


@router.post("", response_model=ProjectDetailResponse)
def create_project(request: CreateProjectRequest) -> ProjectDetailResponse:
    service = ProjectService()
    result = service.create_project(
        project_name=request.project_name,
        brief_text=request.brief_text,
        notes=request.notes,
    )
    return ProjectDetailResponse(**result)


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str) -> ProjectDetailResponse:
    service = ProjectService()
    return ProjectDetailResponse(**service.get_project(project_id))


@router.put("/{project_id}", response_model=ProjectDetailResponse)
def update_project(project_id: str, request: UpdateProjectRequest) -> ProjectDetailResponse:
    service = ProjectService()
    updated = service.update_project(project_id, request.project_state, notes=request.notes)
    return ProjectDetailResponse(**updated)


@router.post("/{project_id}/runs", response_model=RunExecutionResponse)
def create_run(project_id: str, request: RunExecutionRequest) -> RunExecutionResponse:
    service = ProjectService()
    run, diff = service.create_run(project_id, state=request.project_state)
    return RunExecutionResponse(run=run, diff_from_previous=diff)


@router.get("/{project_id}/runs", response_model=ProjectRunsResponse)
def list_runs(project_id: str) -> ProjectRunsResponse:
    service = ProjectService()
    runs = service.list_runs(project_id)
    return ProjectRunsResponse(project_id=project_id, runs=runs)

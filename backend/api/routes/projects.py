"""Project workspace routes for file-backed persistence and iteration runs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, UploadFile

from backend.agents.floor_plan_agent import FloorPlanAgent
from backend.schemas.project_models import (
    CreateProjectRequest,
    FloorPlanUploadResponse,
    ProjectDetailResponse,
    ProjectRunsResponse,
    ProjectsListResponse,
    RunExecutionRequest,
    RunExecutionResponse,
    UpdateProjectRequest,
)
from backend.services.floor_plan_service import FloorPlanService
from backend.services.project_service import ProjectService

router = APIRouter()

_ACCEPTED_CONTENT_TYPES = FloorPlanAgent.SUPPORTED_MEDIA_TYPES


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


@router.post("/{project_id}/upload-plan", response_model=FloorPlanUploadResponse)
async def upload_floor_plan(project_id: str, file: UploadFile) -> FloorPlanUploadResponse:
    """Upload a floor plan image or PDF and run AI-assisted environmental analysis.

    Accepted file types: JPEG, PNG, GIF, WebP, PDF.
    Results are persisted into the project's current design state.
    """

    content_type = (file.content_type or "").split(";")[0].strip().lower()
    if content_type not in _ACCEPTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type '{content_type}'. "
                f"Accepted: {', '.join(sorted(_ACCEPTED_CONTENT_TYPES))}"
            ),
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    service = FloorPlanService()
    try:
        result = service.analyse_and_persist(project_id, image_bytes, content_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return FloorPlanUploadResponse(
        project_id=result["project_id"],
        floor_plan_analysis=result["floor_plan_analysis"],
        updated_building=result["updated_building"],
    )

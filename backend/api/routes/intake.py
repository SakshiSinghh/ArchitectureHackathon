"""Intake route group for parsing and normalizing user inputs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.schemas.api_models import (
    ConstraintInterpretRequest,
    ConstraintInterpretResponse,
    IntakeRequest,
    IntakeResponse,
    ParseMetadata,
)
from backend.services.constraint_parsing_service import interpret_constraints
from backend.services.intake_service import parse_intake
from backend.services.validation_service import validate_project_state

router = APIRouter()


@router.get("/ping")
def ping() -> dict[str, str]:
    """Simple health endpoint for intake route group."""

    return {"status": "ok", "service": "intake"}


@router.post("/parse", response_model=IntakeResponse)
def parse(request: IntakeRequest) -> IntakeResponse:
    """Normalize input payload into canonical project state."""

    try:
        parse_result = parse_intake(request.input_mode, request.payload)
        issues = validate_project_state(parse_result.project_state)
        parse_result.project_state.validation_issues = issues

        return IntakeResponse(
            project_state=parse_result.project_state,
            validation_issues=issues,
            assumptions=parse_result.project_state.assumptions,
            provenance=parse_result.project_state.provenance,
            parse_metadata=ParseMetadata(
                input_mode=request.input_mode,
                parser_note=parse_result.parser_note,
                extraction_confidence=parse_result.extraction_confidence,
                unparsed_items=parse_result.unparsed_items,
            ),
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/interpret-constraints", response_model=ConstraintInterpretResponse)
def interpret(request: ConstraintInterpretRequest) -> ConstraintInterpretResponse:
    """Interpret free-text constraints into normalized structured candidates."""

    try:
        parsed = interpret_constraints(request.project_state, preferred_provider=request.preferred_provider)
        return ConstraintInterpretResponse(parsed_constraints=parsed)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

"""Intake agent: normalize raw user input into project state."""

from __future__ import annotations

from typing import Any

from backend.services.intake_service import parse_intake
from shared.project_state import ProjectState


class IntakeAgent:
    """Wraps intake parsing logic for orchestrated workflows."""

    def run(self, input_mode: str, payload: Any) -> ProjectState:
        return parse_intake(input_mode=input_mode, payload=payload)

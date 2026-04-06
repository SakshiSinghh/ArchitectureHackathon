"""Intake parsing logic that normalizes input into canonical project state."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from pydantic import ValidationError

from shared.project_state import ProjectState


@dataclass
class IntakeParseResult:
    """Structured parse result with metadata for frontend explainability."""

    project_state: ProjectState
    parser_note: str
    extraction_confidence: str
    unparsed_items: list[str]


def _to_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _append_unique(target: list[str], values: list[str]) -> None:
    for value in values:
        if value and value not in target:
            target.append(value)


def _parse_brief_heuristically(brief_text: str) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
    extracted: dict[str, Any] = {}
    notes: list[str] = []
    unparsed_items: list[str] = []
    inferred_fields: list[str] = []

    if not brief_text:
        notes.append("No brief text provided.")
        return extracted, notes, unparsed_items, inferred_fields

    lines = [line.strip() for line in brief_text.splitlines() if line.strip()]
    key_map = {
        "project_name": "project_name",
        "location": "location_name",
        "location_name": "location_name",
        "latitude": "latitude",
        "longitude": "longitude",
        "building_type": "building_type",
        "width": "width_m",
        "width_m": "width_m",
        "depth": "depth_m",
        "depth_m": "depth_m",
        "height": "height_m",
        "height_m": "height_m",
        "floors": "floors",
        "orientation": "orientation_deg",
        "orientation_deg": "orientation_deg",
        "window_to_wall_ratio": "window_to_wall_ratio",
        "hard_constraints": "hard_constraints",
        "soft_constraints": "soft_constraints",
    }

    for line in lines:
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        normalized_key = key_map.get(key.strip().lower())
        if not normalized_key:
            unparsed_items.append(line)
            continue
        extracted[normalized_key] = raw_value.strip()

    if not extracted:
        location_match = re.search(r"location\s+([A-Za-z\s\-]+)", brief_text, re.IGNORECASE)
        if location_match:
            extracted["location_name"] = location_match.group(1).strip()
            inferred_fields.append("site.location_name")

        wwr_match = re.search(r"wwr\s*[:=]?\s*(0?\.\d+|1(?:\.0+)?)", brief_text, re.IGNORECASE)
        if wwr_match:
            extracted["window_to_wall_ratio"] = wwr_match.group(1)
            inferred_fields.append("building.window_to_wall_ratio")

    if "location_name" not in extracted:
        notes.append("Could not reliably extract site location from brief.")
    if "building_type" not in extracted:
        notes.append("Could not reliably extract building type from brief.")

    notes.append(
        "Brief parsing uses key:value and lightweight keyword heuristics in Phase 2; manual review is required."
    )
    return extracted, notes, unparsed_items, inferred_fields


def _apply_manual_payload(state: ProjectState, payload: dict[str, Any]) -> None:
    state.project_name = payload.get("project_name") or state.project_name
    state.site.location_name = payload.get("location_name")
    state.site.latitude = _to_float(payload.get("latitude"))
    state.site.longitude = _to_float(payload.get("longitude"))
    state.site.climate_notes = payload.get("climate_notes")

    state.building.building_type = payload.get("building_type")
    state.building.width_m = _to_float(payload.get("width_m"))
    state.building.depth_m = _to_float(payload.get("depth_m"))
    state.building.height_m = _to_float(payload.get("height_m"))
    state.building.floors = _to_int(payload.get("floors"))
    state.building.orientation_deg = _to_float(payload.get("orientation_deg"))
    state.building.window_to_wall_ratio = _to_float(payload.get("window_to_wall_ratio"))
    state.building.geometry_notes = payload.get("geometry_notes")

    state.constraints["hard_constraints"] = _parse_list(payload.get("hard_constraints"))
    state.constraints["soft_constraints"] = _parse_list(payload.get("soft_constraints"))

    for priority_key in ["energy", "daylight", "ventilation", "cost", "aesthetics"]:
        raw_value = payload.get(f"priority_{priority_key}")
        parsed = _to_float(raw_value)
        if parsed is not None:
            setattr(state.priorities, priority_key, parsed)


def _resolve_defaults_and_unresolved(state: ProjectState) -> None:
    if state.building.window_to_wall_ratio is None:
        state.building.window_to_wall_ratio = 0.35
        _append_unique(state.provenance.defaulted_fields, ["building.window_to_wall_ratio"])
        state.assumptions.append("Defaulted window-to-wall ratio to 0.35.")

    required_fields = {
        "building.building_type": state.building.building_type,
        "building.width_m": state.building.width_m,
        "building.depth_m": state.building.depth_m,
        "building.height_m": state.building.height_m,
        "building.orientation_deg": state.building.orientation_deg,
    }
    unresolved = [field for field, value in required_fields.items() if value in (None, "")]

    has_location_name = bool(state.site.location_name)
    has_coordinates = state.site.latitude is not None and state.site.longitude is not None

    if not has_location_name and not has_coordinates:
        unresolved.append("site.location_name")

    if not has_coordinates:
        unresolved.extend(["site.latitude", "site.longitude"])

    _append_unique(state.provenance.unresolved_fields, unresolved)

    priorities = [
        state.priorities.energy,
        state.priorities.daylight,
        state.priorities.ventilation,
        state.priorities.cost,
        state.priorities.aesthetics,
    ]
    if sum(priorities) <= 0:
        state.priorities.energy = 0.25
        state.priorities.daylight = 0.2
        state.priorities.ventilation = 0.2
        state.priorities.cost = 0.2
        state.priorities.aesthetics = 0.15
        _append_unique(
            state.provenance.defaulted_fields,
            [
                "priorities.energy",
                "priorities.daylight",
                "priorities.ventilation",
                "priorities.cost",
                "priorities.aesthetics",
            ],
        )
        state.assumptions.append("All priorities were non-positive; reverted to default MVP priority weights.")


def _capture_provenance(state: ProjectState, payload: dict[str, Any]) -> None:
    for key, value in payload.items():
        if value in (None, "", []):
            continue
        state.provenance.user_provided_fields.append(key)


def parse_intake(input_mode: str, payload: Any) -> IntakeParseResult:
    """Parse manual, pasted, or JSON inputs into a ProjectState."""


    if input_mode == "uploaded_json":
        if not isinstance(payload, dict):
            raise ValueError("Uploaded JSON payload must be an object.")
        try:
            parsed = ProjectState.model_validate(payload)
        except ValidationError as error:
            raise ValueError(f"Uploaded JSON does not match canonical schema: {error}") from error
        parsed.input_mode = "uploaded_json"
        _append_unique(parsed.provenance.user_provided_fields, ["uploaded_json"])
        _resolve_defaults_and_unresolved(parsed)
        return IntakeParseResult(
            project_state=parsed,
            parser_note="Strict canonical-schema validation for uploaded JSON.",
            extraction_confidence="high",
            unparsed_items=[],
        )

    if input_mode == "pasted_brief":
        brief_text = str(payload or "").strip()
        state = ProjectState(input_mode="pasted_brief", brief_text=brief_text or None)
        extracted, notes, unparsed_items, inferred_fields = _parse_brief_heuristically(brief_text)
        _apply_manual_payload(state, extracted)
        _append_unique(state.assumptions, notes)
        _append_unique(state.provenance.user_provided_fields, ["brief_text"])
        _append_unique(state.provenance.inferred_fields, inferred_fields)
        _capture_provenance(state, extracted)
        _resolve_defaults_and_unresolved(state)
        confidence = "low" if state.provenance.unresolved_fields else "medium"
        return IntakeParseResult(
            project_state=state,
            parser_note="Heuristic key:value extraction only; no advanced NLP.",
            extraction_confidence=confidence,
            unparsed_items=unparsed_items,
        )

    if input_mode == "manual_form":
        if not isinstance(payload, dict):
            raise ValueError("Manual form payload must be an object.")
        state = ProjectState(input_mode="manual_form")
        _apply_manual_payload(state, payload)
        _capture_provenance(state, payload)
        _resolve_defaults_and_unresolved(state)
        return IntakeParseResult(
            project_state=state,
            parser_note="Direct mapping from manual form to canonical schema.",
            extraction_confidence="high",
            unparsed_items=[],
        )

    raise ValueError(f"Unsupported input mode: {input_mode}")

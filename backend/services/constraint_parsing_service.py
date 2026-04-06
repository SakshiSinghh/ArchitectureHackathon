"""Constraint interpretation service for free-text to structured candidates."""

from __future__ import annotations

import re
from typing import Any

from backend.services.llm_service import LLMService, LLMServiceError
from shared.project_state import ParsedConstraintItem, ParsedConstraints, ProjectState


SUPPORTED_KEYS = {
    "orientation_locked",
    "facade_locked",
    "max_floors",
    "glazing_ratio_target",
    "west_facing_preference",
}


def interpret_constraints(project: ProjectState, preferred_provider: str | None = None) -> ParsedConstraints:
    """Interpret free-text constraints with LLM-first, heuristic fallback behavior.

    Returns transparent parsed output with confidence and unresolved items.
    """

    constraints = project.constraints or {}
    free_text = str(constraints.get("free_text") or "").strip()
    if not free_text:
        return ParsedConstraints(
            extracted_items=[],
            unresolved_items=[],
            confidence_label="low",
            confidence_score=0.0,
            parser_provider="none",
            parser_mode="none",
            notes=["No free-text constraints provided."],
            conflict_warnings=[],
        )

    llm = LLMService()
    provider = llm.selected_provider(preferred_provider=preferred_provider)
    if provider:
        try:
            payload, provider_name = llm.parse_constraints_json(free_text, preferred_provider=preferred_provider)
            parsed = _to_parsed_constraints(
                payload,
                parser_provider=provider_name,
                parser_mode="llm",
            )
            parsed.conflict_warnings = _detect_conflicts(project, parsed)
            return parsed
        except LLMServiceError as error:
            heuristic = _heuristic_parse(free_text)
            heuristic.notes.append(f"LLM parsing failed; used heuristic fallback: {error}")
            heuristic.conflict_warnings = _detect_conflicts(project, heuristic)
            return heuristic

    heuristic = _heuristic_parse(free_text)
    heuristic.notes.append("No LLM provider key detected; used heuristic parser.")
    heuristic.conflict_warnings = _detect_conflicts(project, heuristic)
    return heuristic


def prepare_constraints_context(project: ProjectState) -> ProjectState:
    """Apply accepted interpreted constraints into effective analysis context.

    Precedence rule:
    - manual hard_constraints remain authoritative
    - accepted parsed items are added as supplemental constraints
    - conflicts are surfaced in parsed_constraints.conflict_warnings
    """

    constraints = project.constraints or {}
    free_text = str(constraints.get("free_text") or "").strip()
    parsed = project.parsed_constraints or ParsedConstraints()

    constraints.setdefault("hard_constraints", [])
    constraints.setdefault("soft_constraints", [])
    constraints.setdefault("structured_enabled", True)
    constraints.setdefault("parsed_hard_constraints", [])
    constraints.setdefault("effective_hard_constraints", list(constraints.get("hard_constraints") or []))

    accepted_items = [item for item in parsed.extracted_items if item.status in {"accepted", "edited"}]
    parsed_hard = [_item_to_constraint_text(item) for item in accepted_items if _item_to_constraint_text(item)]

    manual_hard = list(constraints.get("hard_constraints") or [])
    effective_hard = list(manual_hard)
    for candidate in parsed_hard:
        if candidate not in effective_hard:
            effective_hard.append(candidate)

    constraints["parsed_hard_constraints"] = parsed_hard
    constraints["effective_hard_constraints"] = effective_hard

    if free_text:
        note = (
            "Free-text constraints were interpreted with human review. "
            "Only accepted or edited parsed items were applied as supplemental constraints."
        )
        if note not in project.assumptions:
            project.assumptions.append(note)

    if parsed.conflict_warnings:
        conflict_note = "Constraint conflicts detected between manual and parsed constraints; manual constraints take precedence."
        if conflict_note not in project.assumptions:
            project.assumptions.append(conflict_note)

    constraints["notes"] = (
        "Manual hard_constraints take precedence over parsed constraints in conflicts. "
        "Accepted parsed constraints are appended as supplemental context."
    )
    project.constraints = constraints
    project.parsed_constraints = parsed
    return project


def _to_parsed_constraints(payload: dict[str, Any], parser_provider: str, parser_mode: str) -> ParsedConstraints:
    extracted_items: list[ParsedConstraintItem] = []
    for raw_item in payload.get("extracted_items", []):
        if not isinstance(raw_item, dict):
            continue
        normalized_key = str(raw_item.get("normalized_key") or "").strip()
        if normalized_key not in SUPPORTED_KEYS:
            continue
        confidence = _clamp(float(raw_item.get("confidence") or 0.0))
        extracted_items.append(
            ParsedConstraintItem(
                source_text=str(raw_item.get("source_text") or "").strip() or "(unspecified)",
                normalized_key=normalized_key,
                normalized_value=raw_item.get("normalized_value"),
                confidence=confidence,
                rationale=str(raw_item.get("rationale") or ""),
                status="proposed",
            )
        )

    unresolved_items = [str(item).strip() for item in payload.get("unresolved_items", []) if str(item).strip()]
    confidence_score = _clamp(float(payload.get("confidence_score") or 0.0))

    return ParsedConstraints(
        extracted_items=extracted_items,
        unresolved_items=unresolved_items,
        confidence_label=_confidence_label(confidence_score),
        confidence_score=confidence_score,
        parser_provider=parser_provider,
        parser_mode=parser_mode,
        notes=[str(note).strip() for note in payload.get("notes", []) if str(note).strip()],
        conflict_warnings=[],
    )


def _heuristic_parse(free_text: str) -> ParsedConstraints:
    text = free_text.lower()
    extracted: list[ParsedConstraintItem] = []
    unresolved: list[str] = []

    if re.search(r"orientation\s+(cannot|can't|must not|locked|fixed)", text):
        extracted.append(
            ParsedConstraintItem(
                source_text="Orientation cannot change / locked",
                normalized_key="orientation_locked",
                normalized_value=True,
                confidence=0.8,
                rationale="Detected orientation lock language.",
            )
        )

    if re.search(r"facade\s+(must|should).*(locked|fixed|preserve|remain)", text):
        extracted.append(
            ParsedConstraintItem(
                source_text="Facade intent locked",
                normalized_key="facade_locked",
                normalized_value=True,
                confidence=0.75,
                rationale="Detected facade preservation language.",
            )
        )

    floors_match = re.search(r"(?:max|capped|cap|limit(?:ed)?)\s*(?:at\s*)?(\d+)\s*floors?", text)
    if floors_match:
        max_floors = int(floors_match.group(1))
        extracted.append(
            ParsedConstraintItem(
                source_text=f"Max floors {max_floors}",
                normalized_key="max_floors",
                normalized_value=max_floors,
                confidence=0.85,
                rationale="Detected explicit floor cap.",
            )
        )

    if "mostly glazed" in text or "high glazing" in text or "glazed facade" in text:
        extracted.append(
            ParsedConstraintItem(
                source_text="Facade mostly glazed",
                normalized_key="glazing_ratio_target",
                normalized_value="high",
                confidence=0.7,
                rationale="Detected glazing preference language.",
            )
        )

    if "west-facing" in text or "west facing" in text:
        extracted.append(
            ParsedConstraintItem(
                source_text="West-facing preference",
                normalized_key="west_facing_preference",
                normalized_value=True,
                confidence=0.75,
                rationale="Detected west-facing preference language.",
            )
        )

    if not extracted:
        unresolved.append(free_text)

    confidence_score = 0.0 if not extracted else min(0.8, sum(item.confidence for item in extracted) / len(extracted))
    return ParsedConstraints(
        extracted_items=extracted,
        unresolved_items=unresolved,
        confidence_label=_confidence_label(confidence_score),
        confidence_score=round(confidence_score, 3),
        parser_provider="none",
        parser_mode="heuristic",
        notes=["Heuristic parser used deterministic pattern matching."],
        conflict_warnings=[],
    )


def _item_to_constraint_text(item: ParsedConstraintItem) -> str:
    key = item.normalized_key
    value = item.normalized_value
    if key == "orientation_locked" and bool(value):
        return "orientation locked"
    if key == "facade_locked" and bool(value):
        return "facade intent locked"
    if key == "max_floors" and value is not None:
        return f"max floors {value}"
    if key == "glazing_ratio_target" and value is not None:
        return f"glazing ratio target {value}"
    if key == "west_facing_preference" and bool(value):
        return "west-facing preference"
    return ""


def _detect_conflicts(project: ProjectState, parsed: ParsedConstraints) -> list[str]:
    manual = [str(item).lower() for item in (project.constraints or {}).get("hard_constraints", [])]
    warnings: list[str] = []

    for item in parsed.extracted_items:
        key = item.normalized_key
        if key == "orientation_locked" and any("orientation unlocked" in token for token in manual):
            warnings.append("Manual constraints indicate unlocked orientation while parsed constraints indicate orientation lock.")
        if key == "facade_locked" and any("facade flexible" in token for token in manual):
            warnings.append("Manual constraints indicate flexible facade while parsed constraints indicate facade lock.")
        if key == "max_floors":
            manual_floor_values = [
                int(match.group(1))
                for token in manual
                for match in [re.search(r"max\s*floors\s*(\d+)", token)]
                if match
            ]
            if manual_floor_values and int(item.normalized_value or 0) != manual_floor_values[0]:
                warnings.append(
                    f"Manual max floors ({manual_floor_values[0]}) differs from parsed max floors ({item.normalized_value})."
                )
    return warnings


def _confidence_label(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.45:
        return "medium"
    return "low"


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

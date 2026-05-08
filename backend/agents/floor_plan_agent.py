"""Floor plan agent: extract environmental room-level data from an uploaded plan."""

from __future__ import annotations

from backend.core.config import settings
from backend.services.llm_service import LLMService, LLMServiceError
from shared.project_state import FloorPlanAnalysis, RoomAnalysis

_MOCK_ANALYSIS = FloorPlanAnalysis(
    primary_orientation_deg=0.0,
    north_assumption="top of image assumed as north",
    rooms=[
        RoomAnalysis(
            room_name="Living Room",
            facade_orientations=["south", "west"],
            is_external=True,
            environmental_issues=["West-facing glazing risks afternoon heat gain"],
            suggestions=["Add horizontal shading fins on west facade", "Reduce WWR on west to 0.25"],
        ),
        RoomAnalysis(
            room_name="Master Bedroom",
            facade_orientations=["east"],
            is_external=True,
            environmental_issues=[],
            suggestions=["East orientation is favourable for morning light — maintain current glazing"],
        ),
        RoomAnalysis(
            room_name="Kitchen",
            facade_orientations=["north"],
            is_external=True,
            environmental_issues=["North-facing in tropics receives limited direct daylight"],
            suggestions=["Consider a skylight or high-level clerestory window for diffuse daylight"],
        ),
    ],
    overall_issues=[
        "West elevation exposes living zones to peak afternoon heat gain",
        "Limited cross-ventilation — primary openings share the same south facade",
    ],
    overall_suggestions=[
        "Introduce openings on north facade to enable cross-ventilation",
        "Consider external louvres or a deep overhang on the west elevation",
        "Glazing ratio on west facade should not exceed 0.20",
    ],
    confidence="low",
    analysis_notes="Mock analysis — upload a real floor plan with ANTHROPIC_API_KEY set for live results.",
    provider="mock",
)


class FloorPlanAgent:
    """Runs AI-assisted floor plan analysis via Claude vision."""

    SUPPORTED_MEDIA_TYPES = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
    }

    def __init__(self) -> None:
        self._llm = LLMService()

    def run(self, image_bytes: bytes, media_type: str) -> FloorPlanAnalysis:
        """Analyse a floor plan and return structured environmental data.

        Falls back to a deterministic mock when:
        - MOCK_MODE is enabled, or
        - No Anthropic API key is present.
        """

        if media_type not in self.SUPPORTED_MEDIA_TYPES:
            raise ValueError(
                f"Unsupported file type '{media_type}'. "
                f"Accepted: {', '.join(sorted(self.SUPPORTED_MEDIA_TYPES))}"
            )

        if settings.mock_mode or not self._llm.anthropic_key_detected():
            return _MOCK_ANALYSIS

        try:
            raw, provider = self._llm.analyse_floor_plan(image_bytes, media_type)
        except LLMServiceError as exc:
            # Surface a low-confidence mock rather than crashing the endpoint.
            fallback = _MOCK_ANALYSIS.model_copy()
            fallback = FloorPlanAnalysis(
                **{
                    **_MOCK_ANALYSIS.model_dump(),
                    "analysis_notes": f"LLM call failed ({exc}); showing mock data.",
                    "provider": "fallback",
                    "confidence": "low",
                }
            )
            return fallback

        rooms = [
            RoomAnalysis(
                room_name=r.get("room_name", "Unknown Room"),
                facade_orientations=r.get("facade_orientations", []),
                is_external=bool(r.get("is_external", False)),
                environmental_issues=r.get("environmental_issues", []),
                suggestions=r.get("suggestions", []),
            )
            for r in raw.get("rooms", [])
        ]

        return FloorPlanAnalysis(
            primary_orientation_deg=raw.get("primary_orientation_deg"),
            north_assumption=raw.get("north_assumption", "top of image assumed as north"),
            rooms=rooms,
            overall_issues=raw.get("overall_issues", []),
            overall_suggestions=raw.get("overall_suggestions", []),
            confidence=raw.get("confidence", "low"),
            analysis_notes=raw.get("analysis_notes"),
            provider=provider,
        )

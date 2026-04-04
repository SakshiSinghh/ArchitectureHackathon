"""Optional LLM integration wrapper with safe mock fallback."""

from __future__ import annotations

from backend.core.config import settings


class LLMService:
    """Provides text-generation behavior with mock fallback by default."""

    def generate(self, prompt: str) -> str:
        """Return a mock response unless keys are configured and mock mode is disabled."""

        if settings.mock_mode:
            return "[MOCK] Mitigation suggestions are running in demo mode."

        # TODO: Add real Anthropic/OpenAI provider integration in a later phase.
        return "[TODO] Real LLM provider integration pending."

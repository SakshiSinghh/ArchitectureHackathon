"""LLM readiness wrapper with safe fallback behavior.

This service intentionally avoids direct SDK calls in the current phase.
It centralizes key detection and provider-selection behavior so downstream
features can adopt a consistent integration surface.
"""

from __future__ import annotations

import json
import re
from typing import Any

import requests

from backend.core.config import settings


class LLMServiceError(RuntimeError):
    """Raised when LLM-backed operations fail."""


class LLMService:
    """Provides provider-aware text generation behavior with safe fallbacks."""

    def anthropic_key_detected(self) -> bool:
        """Return whether Anthropic key is available via centralized settings."""

        return bool(settings.anthropic_api_key)

    def openai_key_detected(self) -> bool:
        """Return whether OpenAI key is available via centralized settings."""

        return bool(settings.openai_api_key)

    def available_providers(self) -> list[str]:
        """Return configured providers in stable preference order."""

        providers: list[str] = []
        if self.anthropic_key_detected():
            providers.append("anthropic")
        if self.openai_key_detected():
            providers.append("openai")
        return providers

    def selected_provider(self, preferred_provider: str | None = None) -> str | None:
        """Return selected provider, honoring preferred provider when possible."""

        available = self.available_providers()
        if not available:
            return None

        if preferred_provider and preferred_provider in available:
            return preferred_provider

        return available[0]

    def generate(self, prompt: str, preferred_provider: str | None = None) -> str:
        """Return safe fallback output until real provider SDK clients are added."""

        _ = prompt  # Prompt is intentionally unused until provider SDK integration is enabled.

        if settings.mock_mode:
            return "[MOCK] Mitigation suggestions are running in demo mode."

        provider = self.selected_provider(preferred_provider=preferred_provider)
        if provider is None:
            return "[DETERMINISTIC] No LLM provider key detected; using deterministic behavior."

        return (
            f"[PLACEHOLDER:{provider}] Provider key detected but external client integration "
            "is not enabled in this phase."
        )

    def parse_constraints_json(self, free_text: str, preferred_provider: str | None = None) -> tuple[dict[str, Any], str]:
        """Interpret free-text constraints using available LLM provider.

        Returns validated JSON payload and provider name.
        """

        provider = self.selected_provider(preferred_provider=preferred_provider)
        if provider is None:
            raise LLMServiceError("No LLM provider key detected.")

        prompt = self._constraint_prompt(free_text)
        if provider == "anthropic":
            content = self._anthropic_completion(prompt)
        elif provider == "openai":
            content = self._openai_completion(prompt)
        else:
            raise LLMServiceError(f"Unsupported provider: {provider}")

        parsed = self._extract_and_validate_json(content)
        return parsed, provider

    def _constraint_prompt(self, free_text: str) -> str:
        return (
            "You are a strict constraint extraction assistant for architecture workflows.\n"
            "Extract only supported keys and return strict JSON with no markdown.\n"
            "Supported keys: orientation_locked, facade_locked, max_floors, glazing_ratio_target, west_facing_preference.\n"
            "If ambiguous or unsupported, place text into unresolved_items instead of guessing.\n"
            "Return format exactly:\n"
            "{\n"
            '  "extracted_items": [\n'
            "    {\n"
            '      "source_text": "...",\n'
            '      "normalized_key": "...",\n'
            '      "normalized_value": true,\n'
            '      "confidence": 0.0,\n'
            '      "rationale": "..."\n'
            "    }\n"
            "  ],\n"
            '  "unresolved_items": ["..."],\n'
            '  "confidence_score": 0.0,\n'
            '  "notes": ["..."]\n'
            "}\n"
            "Text to interpret:\n"
            f"{free_text}"
        )

    def _anthropic_completion(self, prompt: str) -> str:
        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": "claude-3-5-haiku-latest",
            "max_tokens": 900,
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            content = response.json().get("content") or []
            text_parts = [part.get("text", "") for part in content if part.get("type") == "text"]
            return "\n".join(text_parts).strip()
        except (requests.RequestException, ValueError) as error:
            raise LLMServiceError(f"Anthropic request failed: {error}") from error

    def _openai_completion(self, prompt: str) -> str:
        headers = {
            "authorization": f"Bearer {settings.openai_api_key}",
            "content-type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            choices = response.json().get("choices") or []
            message = choices[0].get("message", {}) if choices else {}
            return str(message.get("content") or "").strip()
        except (requests.RequestException, ValueError) as error:
            raise LLMServiceError(f"OpenAI request failed: {error}") from error

    def _extract_and_validate_json(self, raw_text: str) -> dict[str, Any]:
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        if not text.startswith("{"):
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                raise LLMServiceError("LLM response did not contain valid JSON object.")
            text = match.group(0)

        try:
            payload = json.loads(text)
        except json.JSONDecodeError as error:
            raise LLMServiceError(f"Invalid JSON from LLM response: {error}") from error

        if not isinstance(payload.get("extracted_items", []), list):
            raise LLMServiceError("LLM JSON missing list field: extracted_items")
        if not isinstance(payload.get("unresolved_items", []), list):
            raise LLMServiceError("LLM JSON missing list field: unresolved_items")

        payload.setdefault("confidence_score", 0.0)
        payload.setdefault("notes", [])
        return payload

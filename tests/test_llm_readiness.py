from __future__ import annotations

from backend.core.config import Settings
from backend.services.llm_service import LLMService


def _settings(
    *,
    mock_mode: bool,
    anthropic_key: str = "",
    openai_key: str = "",
) -> Settings:
    return Settings(
        app_env="test",
        anthropic_api_key=anthropic_key,
        openai_api_key=openai_key,
        visual_crossing_api_key="",
        open_meteo_base_url="https://api.open-meteo.com/v1/forecast",
        projects_data_dir="data/projects",
        mock_mode=mock_mode,
    )


def test_generate_returns_mock_when_mock_mode_enabled(monkeypatch) -> None:
    monkeypatch.setattr("backend.services.llm_service.settings", _settings(mock_mode=True, anthropic_key="a"))

    service = LLMService()
    result = service.generate("hello")

    assert result.startswith("[MOCK]")


def test_generate_returns_deterministic_when_no_provider_keys(monkeypatch) -> None:
    monkeypatch.setattr("backend.services.llm_service.settings", _settings(mock_mode=False))

    service = LLMService()
    result = service.generate("hello")

    assert result.startswith("[DETERMINISTIC]")
    assert service.available_providers() == []


def test_selected_provider_prefers_available_requested_provider(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.services.llm_service.settings",
        _settings(mock_mode=False, anthropic_key="a", openai_key="o"),
    )

    service = LLMService()

    assert service.selected_provider() == "anthropic"
    assert service.selected_provider(preferred_provider="openai") == "openai"
    assert service.generate("hello", preferred_provider="openai").startswith("[PLACEHOLDER:openai]")

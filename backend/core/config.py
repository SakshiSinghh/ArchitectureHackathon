"""Application configuration with safe defaults for local MVP mode."""

from __future__ import annotations

import os
from dataclasses import dataclass


DEFAULT_OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_env: str
    anthropic_api_key: str
    openai_api_key: str
    open_meteo_base_url: str
    mock_mode: bool


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    """Load settings and force mock mode when keys are missing."""

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    env_mock_mode = _to_bool(os.getenv("MOCK_MODE"), default=False)

    no_llm_keys = not anthropic_api_key and not openai_api_key
    resolved_mock_mode = env_mock_mode or no_llm_keys

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key,
        open_meteo_base_url=os.getenv("OPEN_METEO_BASE_URL", DEFAULT_OPEN_METEO_BASE_URL),
        mock_mode=resolved_mock_mode,
    )


settings = get_settings()

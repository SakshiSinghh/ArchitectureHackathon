"""Application configuration with safe defaults for local MVP mode."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


def load_environment() -> bool:
    """Load local .env variables for development without overriding process env."""

    return load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"), override=False)


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_env: str
    anthropic_api_key: str
    openai_api_key: str
    visual_crossing_api_key: str
    open_meteo_base_url: str
    projects_data_dir: str
    mock_mode: bool


def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    """Load runtime settings from environment variables."""

    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
    env_mock_mode = _to_bool(os.getenv("MOCK_MODE"), default=False)

    return Settings(
        app_env=os.getenv("APP_ENV", "development"),
        anthropic_api_key=anthropic_api_key,
        openai_api_key=openai_api_key,
        visual_crossing_api_key=os.getenv("VISUAL_CROSSING_API_KEY", "").strip(),
        open_meteo_base_url=os.getenv("OPEN_METEO_BASE_URL", DEFAULT_OPEN_METEO_BASE_URL),
        projects_data_dir=os.getenv("PROJECTS_DATA_DIR", "data/projects"),
        mock_mode=env_mock_mode,
    )


load_environment()
settings = get_settings()

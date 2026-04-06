from __future__ import annotations

import os
from pathlib import Path

from backend.core.config import get_settings, load_environment


def test_load_environment_reads_local_dotenv_without_override(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("VISUAL_CROSSING_API_KEY=from-dotenv\nMOCK_MODE=true\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VISUAL_CROSSING_API_KEY", raising=False)
    monkeypatch.delenv("MOCK_MODE", raising=False)

    loaded = load_environment()
    settings = get_settings()

    assert loaded is True
    assert settings.visual_crossing_api_key == "from-dotenv"
    assert settings.mock_mode is True


def test_load_environment_does_not_override_existing_env(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("VISUAL_CROSSING_API_KEY=from-dotenv\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("VISUAL_CROSSING_API_KEY", "from-process")

    load_environment()
    settings = get_settings()

    assert settings.visual_crossing_api_key == "from-process"

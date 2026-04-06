"""Compatibility wrapper for the provider-based climate service."""

from __future__ import annotations

from typing import Any

from shared.project_state import Site

from backend.services.climate import ClimateService


_climate_service = ClimateService()


def get_climate_context(site: Site) -> dict[str, Any]:
    """Return normalized climate context with provider metadata and metrics."""

    return _climate_service.get_climate_summary(site)

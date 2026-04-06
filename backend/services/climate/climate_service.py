"""Climate orchestration service with provider fallback chain."""

from __future__ import annotations

from typing import Any

from shared.project_state import Site

from backend.core.config import settings
from backend.services.climate.base_provider import ClimateProviderError
from backend.services.climate.environmental_metrics import derive_environmental_metrics
from backend.services.climate.geocoding_service import GeocodingService
from backend.services.climate.mock_provider import MockWeatherProvider
from backend.services.climate.openmeteo_provider import OpenMeteoProvider
from backend.services.climate.visualcrossing_provider import VisualCrossingProvider

_DEFAULT_OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class ClimateService:
    """Resolves coordinates and returns normalized climate summaries."""

    def __init__(
        self,
        mock_mode: bool | None = None,
        visual_crossing_api_key: str | None = None,
        open_meteo_base_url: str | None = None,
    ) -> None:
        self.mock_mode = settings.mock_mode if mock_mode is None else mock_mode
        self.visual_crossing_api_key = (
            settings.visual_crossing_api_key if visual_crossing_api_key is None else visual_crossing_api_key
        ).strip()
        self.open_meteo_base_url = (
            settings.open_meteo_base_url
            if open_meteo_base_url is None
            else open_meteo_base_url
        )

        self.geocoding_service = GeocodingService()
        self.mock_provider = MockWeatherProvider()
        self.open_meteo_provider = OpenMeteoProvider(base_url=self.open_meteo_base_url)
        self.visual_crossing_provider = VisualCrossingProvider(api_key=self.visual_crossing_api_key)

    def resolve_coordinates(self, site: Site) -> tuple[Site, dict[str, Any]]:
        return self.geocoding_service.resolve(site)

    def get_climate_data(self, latitude: float, longitude: float) -> dict[str, Any]:
        if self.mock_mode:
            payload = self.mock_provider.get_weather(latitude, longitude)
            payload["source_tier"] = "mock_mode_forced"
            return payload

        if self.visual_crossing_api_key:
            try:
                payload = self.visual_crossing_provider.get_weather(latitude, longitude)
                payload["source_tier"] = "primary_visualcrossing"
                return payload
            except ClimateProviderError:
                pass

        try:
            payload = self.open_meteo_provider.get_weather(latitude, longitude)
            payload["source_tier"] = (
                "fallback_openmeteo_after_primary_failure"
                if self.visual_crossing_api_key
                else "openmeteo_without_primary_key"
            )
            return payload
        except ClimateProviderError:
            payload = self.mock_provider.get_weather(latitude, longitude)
            payload["source_tier"] = "final_mock_after_real_provider_failures"
            return payload

    def get_climate_summary(self, site: Site) -> dict[str, Any]:
        resolved_site, geocoding_meta = self.resolve_coordinates(site)
        if resolved_site.latitude is None or resolved_site.longitude is None:
            return {
                "status": "unresolved_coordinates",
                "provider": "none",
                "geocoding": geocoding_meta,
                "current": {},
                "hourly": [],
                "environmental_metrics": {},
                "location": resolved_site.location_name or "Unknown",
            }

        weather = self.get_climate_data(resolved_site.latitude, resolved_site.longitude)
        metrics = derive_environmental_metrics(weather)

        return {
            "status": "ok",
            "provider": weather.get("provider"),
            "source_tier": weather.get("source_tier", "unknown"),
            "location": resolved_site.location_name or "Unknown",
            "latitude": resolved_site.latitude,
            "longitude": resolved_site.longitude,
            "timezone": weather.get("timezone"),
            "current": weather.get("current", {}),
            "hourly": weather.get("hourly", []),
            "geocoding": geocoding_meta,
            "environmental_metrics": metrics,
        }


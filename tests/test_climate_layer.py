from __future__ import annotations

from typing import Any

import requests

from backend.services.climate.base_provider import ClimateProviderError
from backend.services.climate.climate_service import ClimateService
from backend.services.climate.environmental_metrics import derive_environmental_metrics
from backend.services.climate.geocoding_service import GeocodingService
from backend.services.climate.openmeteo_provider import OpenMeteoProvider
from backend.services.climate.visualcrossing_provider import VisualCrossingProvider
from shared.project_state import Site


class _FakeResponse:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status={self.status_code}")

    def json(self) -> dict[str, Any]:
        return self._payload


def test_provider_selection_uses_mock_when_mock_mode_enabled() -> None:
    service = ClimateService(mock_mode=True, visual_crossing_api_key="example-key")
    payload = service.get_climate_data(18.52, 73.85)
    assert payload["provider"] == "mock"
    assert payload["source_tier"] == "mock_mode_forced"


def test_provider_selection_falls_back_to_mock_on_real_provider_failures() -> None:
    service = ClimateService(mock_mode=False, visual_crossing_api_key="example-key")

    service.visual_crossing_provider.get_weather = lambda *_: (_ for _ in ()).throw(ClimateProviderError("vc down"))
    service.open_meteo_provider.get_weather = lambda *_: (_ for _ in ()).throw(ClimateProviderError("om down"))

    payload = service.get_climate_data(18.52, 73.85)
    assert payload["provider"] == "mock"
    assert payload["source_tier"] == "final_mock_after_real_provider_failures"


def test_provider_selection_labels_openmeteo_when_no_primary_key() -> None:
    service = ClimateService(mock_mode=False, visual_crossing_api_key="")
    service.open_meteo_provider.get_weather = lambda *_: {
        "provider": "open-meteo",
        "timezone": "Asia/Kolkata",
        "current": {},
        "hourly": [],
    }

    payload = service.get_climate_data(18.52, 73.85)
    assert payload["provider"] == "open-meteo"
    assert payload["source_tier"] == "openmeteo_without_primary_key"


def test_geocoding_skips_lookup_when_coordinates_present() -> None:
    service = GeocodingService()
    site = Site(location_name="Pune", latitude=18.52, longitude=73.85)

    resolved, meta = service.resolve(site)
    assert resolved.latitude == 18.52
    assert meta["status"] == "provided"


def test_geocoding_handles_no_match_gracefully(monkeypatch) -> None:
    def _fake_get(*args, **kwargs):
        return _FakeResponse({"results": []})

    monkeypatch.setattr(requests, "get", _fake_get)

    service = GeocodingService()
    site = Site(location_name="Nowhere")
    resolved, meta = service.resolve(site)

    assert resolved.latitude is None
    assert meta["status"] == "no_match"


def test_visualcrossing_normalization(monkeypatch) -> None:
    visual_payload = {
        "timezone": "Asia/Kolkata",
        "currentConditions": {
            "datetime": "12:00:00",
            "temp": 33.0,
            "humidity": 46,
            "windspeed": 18,
            "winddir": 205,
            "cloudcover": 22,
            "solarradiation": 620,
        },
        "days": [
            {
                "hours": [
                    {
                        "datetime": "12:00:00",
                        "temp": 34.0,
                        "humidity": 44,
                        "windspeed": 21.6,
                        "winddir": 210,
                        "cloudcover": 18,
                        "solarradiation": 700,
                    }
                ]
            }
        ],
    }

    def _fake_get(*args, **kwargs):
        return _FakeResponse(visual_payload)

    monkeypatch.setattr(requests, "get", _fake_get)

    provider = VisualCrossingProvider(api_key="test-key")
    normalized = provider.get_weather(18.52, 73.85)

    assert normalized["provider"] == "visualcrossing"
    assert normalized["current"]["wind_speed_mps"] == 5.0
    assert normalized["hourly"][0]["wind_speed_mps"] == 6.0
    assert normalized["hourly"][0]["solar_radiation_wm2"] == 700.0


def test_openmeteo_normalization(monkeypatch) -> None:
    openmeteo_payload = {
        "timezone": "Asia/Kolkata",
        "current": {
            "time": "2026-04-06T10:00",
            "temperature_2m": 30.0,
            "relative_humidity_2m": 58,
            "wind_speed_10m": 3.5,
            "wind_direction_10m": 175,
            "cloud_cover": 45,
            "shortwave_radiation": 520,
        },
        "hourly": {
            "time": ["2026-04-06T10:00", "2026-04-06T11:00"],
            "temperature_2m": [30.0, 31.5],
            "relative_humidity_2m": [58, 56],
            "wind_speed_10m": [3.5, 4.2],
            "wind_direction_10m": [175, 180],
            "cloud_cover": [45, 40],
            "shortwave_radiation": [520, 610],
        },
    }

    def _fake_get(*args, **kwargs):
        return _FakeResponse(openmeteo_payload)

    monkeypatch.setattr(requests, "get", _fake_get)

    provider = OpenMeteoProvider()
    normalized = provider.get_weather(18.52, 73.85)

    assert normalized["provider"] == "open-meteo"
    assert normalized["current"]["temperature_c"] == 30.0
    assert normalized["hourly"][1]["solar_radiation_wm2"] == 610.0


def test_environmental_metrics_calculation() -> None:
    climate_payload = {
        "hourly": [
            {
                "temperature_c": 28,
                "wind_speed_mps": 3,
                "wind_direction_deg": 170,
                "solar_radiation_wm2": 600,
                "cloud_cover_percent": 35,
            },
            {
                "temperature_c": 32,
                "wind_speed_mps": 4,
                "wind_direction_deg": 190,
                "solar_radiation_wm2": 700,
                "cloud_cover_percent": 30,
            },
        ]
    }

    metrics = derive_environmental_metrics(climate_payload)

    assert 0.0 <= float(metrics["heat_exposure_score"]) <= 1.0
    assert 0.0 <= float(metrics["solar_exposure_score"]) <= 1.0
    assert 0.0 <= float(metrics["ventilation_potential_score"]) <= 1.0
    assert metrics["avg_temp"] == 30.0
    assert metrics["peak_solar_radiation"] == 700.0


def test_climate_summary_uses_fallback_provider_with_metrics() -> None:
    service = ClimateService(mock_mode=False, visual_crossing_api_key="example-key")
    service.visual_crossing_provider.get_weather = lambda *_: (_ for _ in ()).throw(ClimateProviderError("vc down"))
    service.open_meteo_provider.get_weather = lambda *_: (_ for _ in ()).throw(ClimateProviderError("om down"))

    site = Site(location_name="Pune", latitude=18.52, longitude=73.85)
    summary = service.get_climate_summary(site)

    assert summary["status"] == "ok"
    assert summary["provider"] == "mock"
    assert summary["source_tier"] == "final_mock_after_real_provider_failures"
    assert "environmental_metrics" in summary
    assert "heat_exposure_score" in summary["environmental_metrics"]

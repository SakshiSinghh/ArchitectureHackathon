"""Open-Meteo fallback weather provider implementation."""

from __future__ import annotations

from typing import Any

import requests

from backend.services.climate.base_provider import ClimateProviderError, WeatherProvider

_DEFAULT_OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


class OpenMeteoProvider(WeatherProvider):
    """Fetches weather from Open-Meteo forecast endpoint."""

    provider_name = "open-meteo"

    def __init__(self, base_url: str = _DEFAULT_OPEN_METEO_FORECAST_URL, timeout_seconds: int = 12) -> None:
        self.base_url = base_url or _DEFAULT_OPEN_METEO_FORECAST_URL
        self.timeout_seconds = timeout_seconds

    def get_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
            "forecast_days": 2,
            "hourly": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "cloud_cover",
                    "shortwave_radiation",
                ]
            ),
            "current": ",".join(
                [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "cloud_cover",
                    "shortwave_radiation",
                ]
            ),
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            raise ClimateProviderError(f"Open-Meteo request failed: {error}") from error

        return _normalize_openmeteo_payload(payload, latitude, longitude)


def _normalize_openmeteo_payload(payload: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any]:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []

    def _pick(name: str, index: int) -> float | None:
        series = hourly.get(name) or []
        if index >= len(series):
            return None
        try:
            value = series[index]
            if value is None:
                return None
            return float(value)
        except (TypeError, ValueError):
            return None

    normalized_hours: list[dict[str, float | str | None]] = []
    for idx, timestamp in enumerate(times[:24]):
        normalized_hours.append(
            {
                "timestamp": str(timestamp),
                "temperature_c": _pick("temperature_2m", idx),
                "humidity_percent": _pick("relative_humidity_2m", idx),
                "wind_speed_mps": _pick("wind_speed_10m", idx),
                "wind_direction_deg": _pick("wind_direction_10m", idx),
                "cloud_cover_percent": _pick("cloud_cover", idx),
                "solar_radiation_wm2": _pick("shortwave_radiation", idx),
            }
        )

    current = payload.get("current") or {}
    current_block = {
        "timestamp": str(current.get("time") or ""),
        "temperature_c": _safe_float(current.get("temperature_2m")),
        "humidity_percent": _safe_float(current.get("relative_humidity_2m")),
        "wind_speed_mps": _safe_float(current.get("wind_speed_10m")),
        "wind_direction_deg": _safe_float(current.get("wind_direction_10m")),
        "cloud_cover_percent": _safe_float(current.get("cloud_cover")),
        "solar_radiation_wm2": _safe_float(current.get("shortwave_radiation")),
    }

    return {
        "provider": "open-meteo",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": payload.get("timezone"),
        "current": current_block,
        "hourly": normalized_hours,
    }


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

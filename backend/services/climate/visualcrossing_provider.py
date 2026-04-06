"""Visual Crossing provider implementation (primary weather source)."""

from __future__ import annotations

from typing import Any

import requests

from backend.services.climate.base_provider import ClimateProviderError, WeatherProvider

_VISUAL_CROSSING_BASE_URL = (
    "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"
)


class VisualCrossingProvider(WeatherProvider):
    """Fetches weather using Visual Crossing timeline API."""

    provider_name = "visualcrossing"

    def __init__(self, api_key: str, timeout_seconds: int = 12) -> None:
        self.api_key = api_key.strip()
        self.timeout_seconds = timeout_seconds

    def get_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        if not self.api_key:
            raise ClimateProviderError("VISUAL_CROSSING_API_KEY is missing.")

        params = {
            "unitGroup": "metric",
            "include": "current,hours",
            "key": self.api_key,
            "contentType": "json",
        }
        url = f"{_VISUAL_CROSSING_BASE_URL}/{latitude},{longitude}"

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = requests.get(url, params=params, timeout=self.timeout_seconds)
                if response.status_code in {429, 500, 502, 503, 504} and attempt == 0:
                    continue
                response.raise_for_status()
                payload = response.json()
                return _normalize_visualcrossing_payload(payload, latitude, longitude)
            except (requests.RequestException, ValueError) as error:
                last_error = error
                if attempt == 0:
                    continue
                raise ClimateProviderError(f"Visual Crossing request failed: {error}") from error

        raise ClimateProviderError(f"Visual Crossing request failed: {last_error}")


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_visualcrossing_payload(payload: dict[str, Any], latitude: float, longitude: float) -> dict[str, Any]:
    current = payload.get("currentConditions") or {}

    days = payload.get("days") or []
    day0 = days[0] if days else {}
    hours = day0.get("hours") or []

    normalized_hours: list[dict[str, float | str | None]] = []
    for hour in hours[:24]:
        normalized_hours.append(
            {
                "timestamp": str(hour.get("datetimeEpoch") or hour.get("datetime") or ""),
                "temperature_c": _to_float(hour.get("temp")),
                "humidity_percent": _to_float(hour.get("humidity")),
                "wind_speed_mps": None
                if _to_float(hour.get("windspeed")) is None
                else round((_to_float(hour.get("windspeed")) or 0.0) / 3.6, 3),
                "wind_direction_deg": _to_float(hour.get("winddir")),
                "cloud_cover_percent": _to_float(hour.get("cloudcover")),
                "solar_radiation_wm2": _to_float(hour.get("solarradiation")),
            }
        )

    current_block = {
        "timestamp": str(current.get("datetimeEpoch") or current.get("datetime") or ""),
        "temperature_c": _to_float(current.get("temp")),
        "humidity_percent": _to_float(current.get("humidity")),
        "wind_speed_mps": None
        if _to_float(current.get("windspeed")) is None
        else round((_to_float(current.get("windspeed")) or 0.0) / 3.6, 3),
        "wind_direction_deg": _to_float(current.get("winddir")),
        "cloud_cover_percent": _to_float(current.get("cloudcover")),
        "solar_radiation_wm2": _to_float(current.get("solarradiation")),
    }

    return {
        "provider": "visualcrossing",
        "latitude": latitude,
        "longitude": longitude,
        "timezone": payload.get("timezone"),
        "current": current_block,
        "hourly": normalized_hours,
    }

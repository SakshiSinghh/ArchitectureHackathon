"""Deterministic synthetic weather provider used for mock/demo mode."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from backend.services.climate.base_provider import WeatherProvider


class MockWeatherProvider(WeatherProvider):
    """Returns deterministic synthetic weather values for stable tests/demo."""

    provider_name = "mock"

    def get_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        base_temp = 23.0 + ((abs(latitude) % 10) * 0.2)
        base_humidity = 55.0 + ((abs(longitude) % 10) * 1.1)
        base_wind = 3.0 + ((abs(latitude + longitude) % 5) * 0.2)

        start = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
        hourly: list[dict[str, float | str | None]] = []
        for hour in range(24):
            timestamp = (start + timedelta(hours=hour)).isoformat()
            diurnal = max(0.0, 1.0 - abs(hour - 13) / 12)
            temperature = round(base_temp + 8.0 * diurnal - 2.0 * (1.0 - diurnal), 2)
            solar = round(780.0 * diurnal, 2)
            cloud = round(65.0 - 35.0 * diurnal, 2)
            wind = round(base_wind + (0.8 if 10 <= hour <= 18 else -0.4), 2)
            humidity = round(base_humidity + (6.0 if hour <= 7 or hour >= 21 else -5.0), 2)
            hourly.append(
                {
                    "timestamp": timestamp,
                    "temperature_c": temperature,
                    "humidity_percent": max(20.0, min(95.0, humidity)),
                    "wind_speed_mps": max(0.1, wind),
                    "wind_direction_deg": float((110 + hour * 7) % 360),
                    "cloud_cover_percent": max(0.0, min(100.0, cloud)),
                    "solar_radiation_wm2": max(0.0, solar),
                }
            )

        return {
            "provider": "mock",
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "UTC",
            "current": hourly[0],
            "hourly": hourly,
        }

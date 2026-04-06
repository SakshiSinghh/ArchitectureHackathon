"""Provider abstractions for normalized weather access."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ClimateProviderError(RuntimeError):
    """Raised when an external climate provider cannot return usable data."""


@dataclass(frozen=True)
class NormalizedSample:
    """Single normalized weather sample used for summaries and scoring."""

    timestamp: str
    temperature_c: float | None
    humidity_percent: float | None
    wind_speed_mps: float | None
    wind_direction_deg: float | None
    cloud_cover_percent: float | None
    solar_radiation_wm2: float | None


class WeatherProvider(ABC):
    """Contract for weather providers returning a normalized payload."""

    provider_name: str = "unknown"

    @abstractmethod
    def get_weather(self, latitude: float, longitude: float) -> dict[str, Any]:
        """Return normalized weather payload for given coordinates."""

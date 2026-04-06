"""Location name to coordinate resolution with graceful failure behavior."""

from __future__ import annotations

from typing import Any

import requests

from shared.project_state import Site

_DEFAULT_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


class GeocodingService:
    """Resolves location names to coordinates using Open-Meteo geocoding."""

    def __init__(self, base_url: str = _DEFAULT_GEOCODING_URL, timeout_seconds: int = 10) -> None:
        self.base_url = base_url or _DEFAULT_GEOCODING_URL
        self.timeout_seconds = timeout_seconds

    def resolve(self, site: Site) -> tuple[Site, dict[str, Any]]:
        if site.latitude is not None and site.longitude is not None:
            return site, {
                "geocoded": False,
                "status": "provided",
                "message": "Coordinates provided directly by input.",
            }

        if not site.location_name:
            return site, {
                "geocoded": False,
                "status": "missing_location_name",
                "message": "No location name available for geocoding.",
            }

        params = {"name": site.location_name, "count": 1, "language": "en", "format": "json"}
        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except (requests.RequestException, ValueError) as error:
            return site, {
                "geocoded": False,
                "status": "geocoding_failed",
                "message": f"Geocoding request failed: {error}",
            }

        results = payload.get("results") or []
        if not results:
            return site, {
                "geocoded": False,
                "status": "no_match",
                "message": f"No geocoding match found for '{site.location_name}'.",
            }

        best_match = results[0]
        site.latitude = _safe_float(best_match.get("latitude"))
        site.longitude = _safe_float(best_match.get("longitude"))

        if site.latitude is None or site.longitude is None:
            return site, {
                "geocoded": False,
                "status": "invalid_match",
                "message": "Best geocoding match did not contain valid coordinates.",
            }

        return site, {
            "geocoded": True,
            "status": "resolved",
            "message": "Coordinates resolved from location name.",
            "name": best_match.get("name"),
            "country": best_match.get("country"),
            "admin1": best_match.get("admin1"),
            "latitude": site.latitude,
            "longitude": site.longitude,
        }


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None

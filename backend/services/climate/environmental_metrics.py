"""Translate normalized weather into design-relevant environmental metrics."""

from __future__ import annotations

from typing import Any


def derive_environmental_metrics(climate_payload: dict[str, Any]) -> dict[str, float | str | None]:
    """Compute compact, explainable scores and summary values.

    Assumptions:
    - Solar exposure increases with shortwave radiation.
    - Heat exposure increases with both temperature and solar radiation.
    - Ventilation potential is best with moderate wind speed (about 2 to 6 m/s).
    """

    hourly = climate_payload.get("hourly") or []
    temperatures = _collect(hourly, "temperature_c")
    wind_speeds = _collect(hourly, "wind_speed_mps")
    wind_directions = _collect(hourly, "wind_direction_deg")
    solar_values = _collect(hourly, "solar_radiation_wm2")
    cloud_values = _collect(hourly, "cloud_cover_percent")

    avg_temp = _avg(temperatures)
    peak_temp = _max(temperatures)
    avg_wind = _avg(wind_speeds)
    dominant_wind_direction = _dominant_wind_direction(wind_directions)
    avg_solar = _avg(solar_values)
    peak_solar = _max(solar_values)
    avg_cloud = _avg(cloud_values)

    solar_exposure_score = _clamp01((avg_solar or 0.0) / 800.0)

    temp_component = _clamp01((((avg_temp or 0.0) - 18.0) / 20.0))
    solar_component = _clamp01((avg_solar or 0.0) / 900.0)
    heat_exposure_score = _clamp01(0.6 * temp_component + 0.4 * solar_component)

    wind_component = _wind_usefulness(avg_wind or 0.0)
    cloud_component = 1.0 - _clamp01((avg_cloud or 0.0) / 100.0)
    ventilation_potential_score = _clamp01(0.8 * wind_component + 0.2 * cloud_component)

    return {
        "heat_exposure_score": round(heat_exposure_score, 3),
        "solar_exposure_score": round(solar_exposure_score, 3),
        "ventilation_potential_score": round(ventilation_potential_score, 3),
        "avg_temp": _round(avg_temp),
        "peak_temp": _round(peak_temp),
        "avg_wind_speed": _round(avg_wind),
        "dominant_wind_direction": _round(dominant_wind_direction),
        "avg_solar_radiation": _round(avg_solar),
        "peak_solar_radiation": _round(peak_solar),
        "avg_cloud_cover": _round(avg_cloud),
    }


def _collect(hourly: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for sample in hourly:
        raw = sample.get(key)
        try:
            if raw is None:
                continue
            values.append(float(raw))
        except (TypeError, ValueError):
            continue
    return values


def _avg(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _max(values: list[float]) -> float | None:
    if not values:
        return None
    return max(values)


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 3)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _wind_usefulness(avg_wind_speed: float) -> float:
    if avg_wind_speed <= 0.5:
        return 0.1
    if avg_wind_speed < 2.0:
        return 0.4
    if avg_wind_speed <= 6.0:
        return 1.0
    if avg_wind_speed <= 9.0:
        return 0.7
    return 0.35


def _dominant_wind_direction(directions: list[float]) -> float | None:
    if not directions:
        return None

    bins: dict[int, int] = {}
    for direction in directions:
        bucket = int(direction // 45) * 45
        bins[bucket] = bins.get(bucket, 0) + 1

    dominant = max(bins.items(), key=lambda item: item[1])[0]
    return float(dominant)

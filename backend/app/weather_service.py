"""
Talks to OpenWeatherMap and applies the caching layer from cache.py.

Kelvin -> Celsius conversion happens here because OpenWeatherMap's default
units are Kelvin (see the sample response in the assignment: temp: 299.12).
"""
import json
from pathlib import Path

import httpx

from .cache import raw_weather_cache, processed_cache
from .comfort_index import compute_comfort_index
from .config import get_settings

CITIES_FILE = Path(__file__).parent / "cities.json"


def load_city_codes() -> list[dict]:
    """
    cities.json (as provided) is wrapped in a top-level "List" key, and
    CityCode arrives as a string, e.g.:
        {"List": [{"CityCode": "1248991", "CityName": "Colombo", ...}]}
    We unwrap it here and cast CityCode to int once, so the rest of the
    codebase (cache keys, the OpenWeatherMap `id` query param) can just
    treat city ids as ints consistently.
    """
    with open(CITIES_FILE) as f:
        data = json.load(f)
    cities = data["List"]
    for city in cities:
        city["CityCode"] = int(city["CityCode"])
    return cities


async def fetch_raw_weather(city_id: int) -> tuple[dict, str]:
    """Returns (weather_json, cache_status) for a single city id."""
    cached, status = raw_weather_cache.get(city_id)
    if cached is not None:
        return cached, status

    settings = get_settings()
    url = f"{settings.openweather_base_url}/weather"
    params = {"id": city_id, "appid": settings.openweather_api_key}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    raw_weather_cache.set(city_id, data)
    return data, status  # status here is "MISS" (we just fetched it)


def _kelvin_to_celsius(k: float) -> float:
    return round(k - 273.15, 1)


async def fetch_forecast(city_id: int) -> tuple[list[dict], str]:
    """
    5-day/3-hour forecast, trimmed down to (timestamp, temp_c) pairs for the
    frontend's trend chart. Cached the same way as raw weather, just under
    a different key namespace so it doesn't collide with current-weather
    entries for the same city id.
    """
    cache_key = f"forecast:{city_id}"
    cached, status = raw_weather_cache.get(cache_key)
    if cached is not None:
        return cached, status

    settings = get_settings()
    url = f"{settings.openweather_base_url}/forecast"
    params = {"id": city_id, "appid": settings.openweather_api_key}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

    points = [
        {"dt": entry["dt_txt"], "temp_c": _kelvin_to_celsius(entry["main"]["temp"])}
        for entry in data.get("list", [])[:16]  # ~2 days of 3-hour steps
    ]
    raw_weather_cache.set(cache_key, points)
    return points, status


async def get_ranked_cities() -> tuple[list[dict], str]:
    """
    Returns (ranked_city_list, processed_cache_status).
    This is what /api/cities calls. It's a thin orchestration layer:
    load city ids -> fetch each (cache-aware) -> score -> sort -> return.
    """
    cache_key = "ranked_cities"
    cached, status = processed_cache.get(cache_key)
    if cached is not None:
        return cached, status

    cities = load_city_codes()
    results = []

    for city in cities:
        raw, _ = await fetch_raw_weather(city["CityCode"])
        main = raw["main"]
        wind = raw.get("wind", {})
        clouds = raw.get("clouds", {})
        weather_desc = raw["weather"][0]["description"] if raw.get("weather") else ""

        breakdown = compute_comfort_index(
            temp_c=_kelvin_to_celsius(main["temp"]),
            humidity_pct=main["humidity"],
            wind_speed_ms=wind.get("speed", 0),
            cloud_pct=clouds.get("all", 0),
        )

        results.append(
            {
                "city_id": city["CityCode"],
                "city_name": raw.get("name", city.get("CityName", "Unknown")),
                "country": raw.get("sys", {}).get("country"),
                "temperature_c": _kelvin_to_celsius(main["temp"]),
                "humidity_pct": main["humidity"],
                "wind_speed_ms": wind.get("speed", 0),
                "cloudiness_pct": clouds.get("all", 0),
                "weather_description": weather_desc,
                "comfort_score": breakdown.final_score,
                "comfort_breakdown": breakdown.__dict__,
            }
        )

    # Rank: highest comfort score = rank 1 (Most Comfortable)
    results.sort(key=lambda r: r["comfort_score"], reverse=True)
    for idx, r in enumerate(results, start=1):
        r["rank"] = idx

    processed_cache.set(cache_key, results)
    return results, status  # status here is "MISS" for the processed list

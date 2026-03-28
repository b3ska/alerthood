"""OpenWeatherMap severe weather alerts scraper.

Fetches weather alerts for monitored areas using the One Call API 3.0.
Requires a free API key from openweathermap.org (instant signup).
https://openweathermap.org/api/one-call-3
"""

import logging
from datetime import datetime, timezone

import httpx

from config import get_settings
from db import get_supabase

logger = logging.getLogger(__name__)

OWM_ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"

SEVERITY_BY_EVENT = {
    "tornado": "critical",
    "hurricane": "critical",
    "typhoon": "critical",
    "tsunami": "critical",
    "extreme heat": "high",
    "extreme cold": "high",
    "flood": "high",
    "flash flood": "high",
    "thunderstorm": "medium",
    "hail": "medium",
    "wind": "medium",
    "fog": "low",
    "frost": "low",
    "rain": "low",
}


def _event_to_severity(event_name: str) -> str:
    event_lower = event_name.lower()
    for keyword, severity in SEVERITY_BY_EVENT.items():
        if keyword in event_lower:
            return severity
    return "medium"


async def fetch_weather_alerts(lat: float, lng: float) -> list[dict]:
    """Fetch weather alerts for a location."""
    settings = get_settings()

    if not settings.openweather_api_key:
        logger.warning("OpenWeatherMap API key not configured, cannot fetch alerts")
        return []

    params = {
        "lat": lat,
        "lon": lng,
        "appid": settings.openweather_api_key,
        "exclude": "current,minutely,hourly,daily",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(OWM_ONECALL_URL, params=params)
        if resp.status_code == 401:
            logger.warning("OpenWeatherMap API key invalid or not activated")
            return []
        if resp.status_code != 200:
            logger.error("OpenWeatherMap API returned HTTP %d", resp.status_code)
            return []
        data = resp.json()

    alerts = data.get("alerts", [])
    events = []

    for alert in alerts:
        event_name = alert.get("event", "Weather Alert")
        severity = _event_to_severity(event_name)
        start = alert.get("start")
        occurred_at = (
            datetime.fromtimestamp(start, tz=timezone.utc).isoformat()
            if start
            else datetime.now(timezone.utc).isoformat()
        )

        description = (alert.get("description", "") or "")[:500]
        sender = alert.get("sender_name", "OpenWeatherMap")

        events.append({
            "title": f"Weather: {event_name}",
            "description": f"{description}\nSource: {sender}",
            "threat_type": "natural",
            "severity": severity,
            "occurred_at": occurred_at,
            "location": f"SRID=4326;POINT({lng} {lat})",
            "location_label": None,
            "source_type": "openweather",
            "source_url": None,
            "relevance_score": {"critical": 95, "high": 80, "medium": 60, "low": 40}.get(severity, 50),
        })

    return events


async def run_openweather_scraper():
    """Fetch weather alerts for all monitored areas."""
    settings = get_settings()

    if not settings.openweather_api_key:
        logger.info("OpenWeatherMap API key not configured, skipping")
        return

    db = get_supabase()

    try:
        areas = (
            db.table("areas")
            .select("id, name")
            .eq("is_active", True)
            .execute()
        )
    except Exception:
        logger.exception("Failed to query areas for OpenWeatherMap scraper")
        return

    if not areas.data:
        return

    total_inserted = 0
    checked_coords = []

    for area in areas.data:
        try:
            center = db.rpc("area_center_coords", {"area_id": area["id"]}).execute()
        except Exception:
            logger.exception("Failed to get center for area %s", area["name"])
            continue

        if not center.data or len(center.data) == 0:
            continue

        lat = center.data[0].get("lat")
        lng = center.data[0].get("lng")
        if not lat or not lng:
            continue

        # Skip nearby areas already checked
        skip = False
        for clat, clng in checked_coords:
            if abs(lat - clat) < 0.5 and abs(lng - clng) < 0.5:
                skip = True
                break
        if skip:
            continue
        checked_coords.append((lat, lng))

        try:
            alerts = await fetch_weather_alerts(lat, lng)
        except httpx.HTTPStatusError as e:
            logger.error("OpenWeatherMap HTTP %d for %s", e.response.status_code, area["name"])
            continue
        except httpx.RequestError as e:
            logger.error("Network error fetching OpenWeatherMap for %s: %s", area["name"], e)
            continue
        except Exception:
            logger.exception("OpenWeatherMap scraper failed for area %s", area["name"])
            continue

        for alert in alerts:
            alert["area_id"] = area["id"]
            try:
                db.table("events").insert(alert).execute()
                total_inserted += 1
            except Exception:
                logger.exception("Failed to insert weather alert for %s", area["name"])

    logger.info("OpenWeatherMap scraper: inserted %d alerts", total_inserted)

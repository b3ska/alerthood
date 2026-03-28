import logging
from datetime import datetime, timedelta

import httpx

from db import get_supabase

logger = logging.getLogger(__name__)

ACLED_API_URL = "https://api.acleddata.com/acled/read"

ACLED_TO_THREAT_TYPE = {
    "Battles": "crime",
    "Violence against civilians": "crime",
    "Explosions/Remote violence": "crime",
    "Riots": "disturbance",
    "Protests": "disturbance",
    "Strategic developments": "infrastructure",
}

ACLED_SEVERITY_MAP = {
    0: "low",
    1: "medium",
    2: "medium",
    3: "high",
    4: "high",
    5: "critical",
}


async def import_acled_data(
    country: str = "United States",
    days_back: int = 90,
    limit: int = 500,
) -> int:
    """Bulk import historical events from ACLED API."""
    sb = get_supabase()

    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")

    params = {
        "country": country,
        "event_date": f"{since}|{datetime.utcnow().strftime('%Y-%m-%d')}",
        "event_date_where": "BETWEEN",
        "limit": limit,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(ACLED_API_URL, params=params)
        if resp.status_code != 200:
            logger.error(f"ACLED API error: {resp.status_code}")
            return 0

        data = resp.json().get("data", [])

    imported = 0
    for event in data:
        lat = event.get("latitude")
        lng = event.get("longitude")
        if not lat or not lng:
            continue

        try:
            lat_f = float(lat)
            lng_f = float(lng)
        except (ValueError, TypeError):
            continue

        event_type = event.get("event_type", "")
        threat_type = ACLED_TO_THREAT_TYPE.get(event_type, "disturbance")

        fatalities = int(event.get("fatalities", 0))
        severity = ACLED_SEVERITY_MAP.get(min(fatalities, 5), "medium")

        event_date = event.get("event_date", datetime.utcnow().isoformat())

        title = event.get("event_type", "Incident")
        notes = event.get("notes", "")
        description = notes[:500] if notes else None
        source = event.get("source", "ACLED")

        # Find matching area
        area_result = sb.rpc(
            "find_nearest_area",
            {"user_point": f"SRID=4326;POINT({lng_f} {lat_f})"},
        ).execute()

        area_id = None
        if area_result.data and len(area_result.data) > 0:
            area_id = area_result.data[0].get("id")

        row = {
            "title": title[:200],
            "description": description,
            "threat_type": threat_type,
            "severity": severity,
            "status": "active",
            "occurred_at": event_date,
            "location": f"SRID=4326;POINT({lng_f} {lat_f})",
            "location_label": event.get("location", None),
            "source_type": "acled",
            "source_url": None,
            "relevance_score": min(50 + fatalities * 10, 100),
            "area_id": area_id,
        }

        try:
            sb.table("events").insert(row).execute()
            imported += 1
        except Exception as e:
            logger.warning(f"Failed to insert ACLED event: {e}")

    logger.info(f"Imported {imported} ACLED events")
    return imported

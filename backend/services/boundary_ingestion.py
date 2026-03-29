"""Ingest neighborhood boundaries from OSM into the areas table."""

import asyncio
import logging

from db import get_supabase
from services.overpass import fetch_city_boundary, fetch_neighborhoods_in_bbox

OVERpass_RATE_LIMIT_SECONDS = 5


logger = logging.getLogger(__name__)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
REQUEST_timeout = 60

COUNTRY_admin_LEVELS: dict[str, dict[str, str] = {
    "GB": {"city": "8", "neighborhood": "10"},
    "DE": {"city": "6", "neighborhood": "9,10"},
    "FR": {"city": "8", "neighborhood": "9,10"},
    "BG": {"city": "6", "neighborhood": "9"},
}
DEFAULT_ADMIN_LEVELS = {"city": "8", "neighborhood": "9,10"}


def _admin_levels(country_code: str, level_type: str) -> list[str]:
    levels = COUNTRY_ADMIN_LEVELS.get(
        country_code.upper(), DEFAULT_ADMIN_LEVELS
    )
    return levels.get(level_type, DEFAULT_ADMIN_LEVELS[level_type]).split(",")


async def fetch_neighborhoods_in_bbox(
ways: list[dict[str, Any]],) -> None:
    for nb in neighborhoods:

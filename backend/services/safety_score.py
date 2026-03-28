import logging
import math
from datetime import datetime, timezone

from fastapi import HTTPException, status
from supabase import Client

from models.schemas import HeatmapCell, TimeBucket

logger = logging.getLogger(__name__)

SEVERITY_WEIGHTS = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}

TIME_BUCKET_HOURS = {
    TimeBucket.morning: (6, 12),
    TimeBucket.afternoon: (12, 18),
    TimeBucket.evening: (18, 24),
    TimeBucket.night: (0, 6),
}

HALF_LIFE_DAYS = 7


def _parse_timestamp(occurred_at: str) -> datetime:
    return datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))


def _recency_weight(ts: datetime) -> float:
    age_days = (datetime.now(timezone.utc) - ts).total_seconds() / 86400
    return math.exp(-0.693 * age_days / HALF_LIFE_DAYS)


def _matches_time_bucket(ts: datetime, bucket: TimeBucket) -> bool:
    if bucket == TimeBucket.all:
        return True
    start, end = TIME_BUCKET_HOURS[bucket]
    return start <= ts.hour < end


def compute_heatmap(
    db: Client,
    area_id: str,
    time_bucket: TimeBucket,
    grid_size: int = 30,
) -> list[HeatmapCell]:
    """Compute heatmap grid cells from events in an area."""
    try:
        events = (
            db.rpc(
                "events_in_area",
                {"target_area_id": area_id},
            ).execute()
        )
    except Exception:
        logger.exception("Failed to fetch events for area %s", area_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Area not found or query failed")

    if not events.data:
        return []

    # Parse timestamps once, filter by time bucket
    parsed = []
    for e in events.data:
        ts = _parse_timestamp(e["occurred_at"])
        if _matches_time_bucket(ts, time_bucket):
            parsed.append((e, ts))

    if not parsed:
        return []

    # Get bounding box from events
    lats = [e["lat"] for e, _ in parsed]
    lngs = [e["lng"] for e, _ in parsed]
    min_lat, max_lat = min(lats), max(lats)
    min_lng, max_lng = min(lngs), max(lngs)

    # Add padding
    lat_pad = (max_lat - min_lat) * 0.1 or 0.01
    lng_pad = (max_lng - min_lng) * 0.1 or 0.01
    min_lat -= lat_pad
    max_lat += lat_pad
    min_lng -= lng_pad
    max_lng += lng_pad

    lat_step = (max_lat - min_lat) / grid_size
    lng_step = (max_lng - min_lng) / grid_size

    # Build grid and accumulate weights
    grid: dict[tuple[int, int], dict] = {}

    for event, ts in parsed:
        row = min(int((event["lat"] - min_lat) / lat_step), grid_size - 1)
        col = min(int((event["lng"] - min_lng) / lng_step), grid_size - 1)

        key = (row, col)
        if key not in grid:
            grid[key] = {"weight": 0.0, "count": 0}

        severity_w = SEVERITY_WEIGHTS.get(event["severity"], 0.5)
        recency_w = _recency_weight(ts)
        grid[key]["weight"] += severity_w * recency_w
        grid[key]["count"] += 1

    # Normalize weights to 0-1
    max_weight = max((c["weight"] for c in grid.values()), default=1.0) or 1.0

    cells = []
    for (row, col), data in grid.items():
        cells.append(
            HeatmapCell(
                lat=min_lat + (row + 0.5) * lat_step,
                lng=min_lng + (col + 0.5) * lng_step,
                weight=round(data["weight"] / max_weight, 3),
                event_count=data["count"],
            )
        )

    return cells

from db import get_supabase


async def detect_area_from_coords(lat: float, lng: float) -> dict | None:
    """Find the nearest area to given coordinates, or return None."""
    sb = get_supabase()

    result = sb.rpc(
        "find_nearest_area",
        {"user_point": f"SRID=4326;POINT({lng} {lat})"},
    ).execute()

    if result.data and len(result.data) > 0:
        return result.data[0]
    return None

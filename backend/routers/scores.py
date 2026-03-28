from datetime import datetime

from fastapi import APIRouter

from db import get_supabase
from models.schemas import NeighborhoodScore, NeighborhoodScoresResponse
from services.neighborhood_scores import refresh_all_scores

router = APIRouter(prefix="/api/scores", tags=["scores"])


@router.get("", response_model=NeighborhoodScoresResponse)
async def get_neighborhood_scores():
    """Get safety scores for all active areas."""
    sb = get_supabase()

    result = (
        sb.table("areas")
        .select(
            "id, name, crime_count, crime_rate_per_km2, poverty_index, safety_score, score_updated_at"
        )
        .eq("is_active", True)
        .order("safety_score", desc=False)
        .execute()
    )

    scores = [
        NeighborhoodScore(
            area_id=row["id"],
            area_name=row["name"],
            crime_count=row.get("crime_count", 0),
            crime_rate_per_km2=float(row.get("crime_rate_per_km2", 0)),
            poverty_index=float(row.get("poverty_index", 0)),
            safety_score=float(row.get("safety_score", 50)),
            score_updated_at=row.get("score_updated_at"),
        )
        for row in (result.data or [])
    ]

    return NeighborhoodScoresResponse(
        scores=scores,
        computed_at=datetime.utcnow().isoformat(),
    )


@router.post("/refresh")
async def refresh_scores():
    """Recompute all neighborhood safety scores."""
    count = await refresh_all_scores()
    return {"updated": count}

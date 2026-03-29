"""Article text fetcher using trafilatura for clean extraction."""

import logging

import httpx
import trafilatura

logger = logging.getLogger(__name__)


async def fetch_article_text(url: str) -> str | None:
    """Fetch article HTML and extract clean text. Returns None on any failure."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "AlertHood/1.0"})
            resp.raise_for_status()
            html = resp.text
    except httpx.HTTPError as e:
        logger.warning("Failed to fetch article %s: %s", url, e)
        return None

    text = trafilatura.extract(html)
    if not text:
        logger.debug("trafilatura extracted nothing from %s", url)
        return None
    return text

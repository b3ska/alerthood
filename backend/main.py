import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routers import events, areas
from services.scraper import run_scraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scraper_loop():
    settings = get_settings()
    interval = settings.scraper_interval_minutes * 60
    while True:
        try:
            logger.info("Running GDELT scraper...")
            await run_scraper()
        except Exception:
            logger.exception("Scraper loop iteration failed; will retry next cycle")
        await asyncio.sleep(interval)


def _scraper_task_done(task: asyncio.Task):
    if task.cancelled():
        logger.warning("Scraper task was cancelled")
    elif exc := task.exception():
        logger.critical("Scraper task died unexpectedly: %s", exc, exc_info=exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(scraper_loop())
    task.add_done_callback(_scraper_task_done)
    yield
    task.cancel()


app = FastAPI(title="AlertHood API", version="0.1.0", lifespan=lifespan)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(areas.router)


@app.get("/health")
async def health():
    return {"status": "ok"}

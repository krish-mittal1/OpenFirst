
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


def start_scheduler():
    from app.services.github_sync import run_full_sync

    scheduler.add_job(
        run_full_sync,
        trigger=IntervalTrigger(hours=settings.sync_interval_hours),
        id="full_sync",
        name="Full GitHub Sync",
        replace_existing=True,
        kwargs={"max_repos": 200},
    )

    scheduler.start()
    logger.info(
        "Scheduler started — full sync every %d hours",
        settings.sync_interval_hours,
    )


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")

"""APScheduler setup and management."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scheduler.jobs import autonomous_pilot_job
from app.config import settings
from loguru import logger

scheduler = AsyncIOScheduler()


def start_scheduler():
    """
    Start APScheduler with configured jobs.

    Adds autonomous pilot job based on cron schedule from config.
    """
    # Parse cron expression from settings
    # Format: "minute hour day month day_of_week"
    # Example: "0 9,15 * * 1-5" = 9am and 3pm Mon-Fri

    # Add autonomous pilot job
    scheduler.add_job(
        autonomous_pilot_job,
        trigger=CronTrigger(
            hour="9,15",  # 9am and 3pm
            day_of_week="mon-fri",
            timezone="America/New_York",
        ),
        id="autonomous_pilot",
        name="Autonomous Paper Trading Pilot",
        replace_existing=True,
        max_instances=1,  # Prevent overlapping runs
    )

    scheduler.start()
    logger.info("Scheduler started with autonomous pilot job (9am, 3pm Mon-Fri EST)")


def stop_scheduler():
    """Stop scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")


def get_scheduler() -> AsyncIOScheduler:
    """Get scheduler instance."""
    return scheduler

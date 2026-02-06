"""APScheduler setup and management."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.scheduler.jobs import autonomous_pilot_job, agent_competition_job
from app.config import settings
from loguru import logger

scheduler = AsyncIOScheduler()


def start_scheduler():
    """
    Start APScheduler with configured jobs.

    Adds autonomous pilot job and agent competition based on cron schedules.
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

    # Add AI agent competition job (daily at 10am EST)
    scheduler.add_job(
        agent_competition_job,
        trigger=CronTrigger(
            hour="10",  # 10am EST
            day_of_week="mon-fri",  # Market days only
            timezone="America/New_York",
        ),
        id="agent_competition",
        name="AI Agent Trading Competition",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info("Scheduler started:")
    logger.info("  - Autonomous pilot: 9am, 3pm Mon-Fri EST")
    logger.info("  - Agent competition: 10am Mon-Fri EST")


def stop_scheduler():
    """Stop scheduler gracefully."""
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler stopped")


def get_scheduler() -> AsyncIOScheduler:
    """Get scheduler instance."""
    return scheduler

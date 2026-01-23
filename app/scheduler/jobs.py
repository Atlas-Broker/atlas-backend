"""Job definitions for APScheduler."""

from app.agents.autonomous_pilot import run_autonomous_pilot
from loguru import logger


async def autonomous_pilot_job():
    """
    Scheduled job to run autonomous pilot.

    This job is triggered by APScheduler on a cron schedule.
    """
    logger.info("Starting scheduled autonomous pilot job")

    try:
        result = await run_autonomous_pilot()
        logger.info(
            f"Pilot job complete: run_id={result['run_id']}, "
            f"status={result['status']}"
        )
    except Exception as e:
        logger.error(f"Pilot job failed: {e}", exc_info=True)
        raise

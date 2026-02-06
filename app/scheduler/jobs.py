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


async def agent_competition_job():
    """
    Scheduled job to run daily AI agent competition.

    All 4 Gemini models trade autonomously every day.
    """
    logger.info("🏆 Starting daily agent competition")

    try:
        from app.agents.competition_coordinator import competition_coordinator

        # Initialize if not already done
        if not competition_coordinator.agents:
            await competition_coordinator.initialize_agents()

        # Define NASDAQ watchlist (top traded stocks)
        watchlist = [
            "AAPL",  # Apple
            "MSFT",  # Microsoft
            "GOOGL", # Alphabet
            "AMZN",  # Amazon
            "NVDA",  # NVIDIA
            "TSLA",  # Tesla
            "META",  # Meta
            "AMD",   # AMD
            "NFLX",  # Netflix
            "INTC",  # Intel
        ]

        # Run competition
        results = await competition_coordinator.run_daily_competition(watchlist)

        logger.info(f"🏆 Competition complete: {len(results)} agents traded")

    except Exception as e:
        logger.error(f"❌ Competition job failed: {e}", exc_info=True)
        raise

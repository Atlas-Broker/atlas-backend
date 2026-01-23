"""Manually run autonomous pilot."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.autonomous_pilot import run_autonomous_pilot
from app.db.supabase.client import init_db, close_db
from app.db.mongodb.client import init_mongodb, close_mongodb
from loguru import logger


async def main():
    """Run autonomous pilot manually."""
    logger.info("Initializing databases...")

    try:
        await init_db()
        await init_mongodb()

        logger.info("Running autonomous pilot...")
        result = await run_autonomous_pilot()

        logger.info("Pilot run complete!")
        logger.info(f"Run ID: {result['run_id']}")
        logger.info(f"Status: {result['status']}")

        if result.get("reflection"):
            reflection = result["reflection"]
            logger.info(f"Trades executed: {reflection['trades_executed']}")
            logger.info(f"P&L: ${reflection['total_pnl']:+.2f}")
            logger.info(f"Performance: {reflection['performance_notes']}")

    except Exception as e:
        logger.error(f"Pilot run failed: {e}", exc_info=True)
        raise

    finally:
        await close_db()
        await close_mongodb()


if __name__ == "__main__":
    asyncio.run(main())

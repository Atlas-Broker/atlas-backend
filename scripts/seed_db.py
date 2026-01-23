"""Seed database with test data."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import (
    get_or_create_pilot_account,
    create_paper_order,
    save_equity_snapshot,
)
from app.db.mongodb.client import get_database, init_mongodb
from app.db.mongodb.queries import save_agent_run
from datetime import datetime, timedelta
import random
from loguru import logger


async def seed_supabase():
    """Seed Supabase with test data."""
    logger.info("Seeding Supabase...")

    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get pilot account
        account = await get_or_create_pilot_account(session)
        logger.info(f"Pilot account: {account.id}")

        # Create sample orders
        symbols = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL"]

        for i, symbol in enumerate(symbols):
            order = await create_paper_order(
                session,
                account.id,
                symbol,
                "BUY",
                10,
                f"test-run-{i}",
                confidence_score=0.75,
                reasoning_summary=f"Test order for {symbol}",
            )
            logger.info(f"Created order: {order.id} - {symbol}")

        # Create equity snapshots (past week)
        base_equity = 100000.00
        for days_ago in range(7, 0, -1):
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            equity = base_equity + random.uniform(-2000, 2000)

            await save_equity_snapshot(
                session,
                {
                    "account_id": account.id,
                    "equity": equity,
                    "cash": equity * 0.7,
                    "positions_value": equity * 0.3,
                    "timestamp": timestamp,
                },
            )
            logger.info(f"Created equity snapshot: {timestamp.date()} - ${equity:.2f}")


async def seed_mongodb():
    """Seed MongoDB with test agent runs."""
    logger.info("Seeding MongoDB...")

    await init_mongodb()
    db = get_database()

    # Clear existing test data
    await db.agent_runs.delete_many({"user_id": "test-user"})

    # Create sample agent runs
    for i in range(5):
        trace = {
            "run_id": f"test-run-{i}",
            "user_id": "test-user",
            "timestamp": datetime.utcnow() - timedelta(hours=i),
            "input": f"Test analysis request {i}",
            "mode": "copilot",
            "tools_called": [
                {
                    "tool": "get_market_data",
                    "symbol": "NVDA",
                    "params": {"symbol": "NVDA"},
                    "result": {"current_price": 140.50, "cached": False},
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "reasoning": {"raw_thoughts": f"Test reasoning for run {i}"},
            "proposal": {
                "action": "BUY",
                "symbol": "NVDA",
                "quantity": 10,
                "confidence": 0.75,
            },
            "status": "COMPLETE",
        }

        await save_agent_run(trace)
        logger.info(f"Created agent run: {trace['run_id']}")


async def main():
    """Run all seeding tasks."""
    logger.info("Starting database seeding...")

    try:
        await seed_supabase()
        await seed_mongodb()

        logger.info("Database seeding completed successfully!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

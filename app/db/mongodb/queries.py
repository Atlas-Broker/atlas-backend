"""Reusable MongoDB queries."""

from app.db.mongodb.client import get_database
from app.db.mongodb.models import AgentRun, MarketDataCache
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger


async def save_agent_run(trace: Dict[str, Any]) -> str:
    """
    Save agent run trace to MongoDB.

    Args:
        trace: Agent run dictionary (will be validated against AgentRun model)

    Returns:
        run_id of saved trace
    """
    db = get_database()

    # Validate with Pydantic model
    agent_run = AgentRun(**trace)

    # Convert to dict and save
    doc = agent_run.model_dump(mode="json")

    await db.agent_runs.insert_one(doc)
    logger.info(f"Saved agent run: {agent_run.run_id}")

    return agent_run.run_id


async def get_agent_run(run_id: str) -> Optional[Dict[str, Any]]:
    """Fetch agent run by ID."""
    db = get_database()
    doc = await db.agent_runs.find_one({"run_id": run_id})

    if doc:
        # Remove MongoDB _id field
        doc.pop("_id", None)

    return doc


async def get_recent_agent_runs(
    user_id: str, limit: int = 20, mode: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get recent agent runs for a user."""
    db = get_database()

    query = {"user_id": user_id}
    if mode:
        query["mode"] = mode

    cursor = db.agent_runs.find(query).sort("timestamp", -1).limit(limit)

    runs = []
    async for doc in cursor:
        doc.pop("_id", None)
        runs.append(doc)

    return runs


async def update_agent_run(run_id: str, updates: Dict[str, Any]):
    """Update agent run with new data."""
    db = get_database()

    await db.agent_runs.update_one({"run_id": run_id}, {"$set": updates})
    logger.info(f"Updated agent run: {run_id}")


async def save_market_data_snapshot(snapshot: Dict[str, Any]) -> str:
    """
    Save market data snapshot to MongoDB cache.

    Args:
        snapshot: Market data dictionary

    Returns:
        cache_key of saved snapshot
    """
    db = get_database()

    # Create cache key
    cache_key = f"{snapshot['symbol']}_{snapshot['timestamp'].isoformat()}"
    snapshot["cache_key"] = cache_key

    # Validate with Pydantic
    cache_doc = MarketDataCache(**snapshot)

    # Save
    doc = cache_doc.model_dump(mode="json")
    await db.market_data_cache.replace_one(
        {"cache_key": cache_key}, doc, upsert=True
    )

    logger.debug(f"Saved market data cache: {cache_key}")
    return cache_key


async def get_cached_market_data(
    symbol: str, max_age_minutes: int = 15
) -> Optional[Dict[str, Any]]:
    """
    Get cached market data if available and not expired.

    Args:
        symbol: Stock symbol
        max_age_minutes: Maximum age of cache in minutes

    Returns:
        Cached data dictionary or None if not found/expired
    """
    db = get_database()

    cutoff_time = datetime.utcnow() - timedelta(minutes=max_age_minutes)

    doc = await db.market_data_cache.find_one(
        {"symbol": symbol.upper(), "timestamp": {"$gte": cutoff_time}}
    )

    if doc:
        doc.pop("_id", None)
        logger.debug(f"Cache hit for {symbol}")
        return doc

    logger.debug(f"Cache miss for {symbol}")
    return None


async def get_market_data_at_time(symbol: str, timestamp: datetime) -> Optional[Dict[str, Any]]:
    """
    Get market data snapshot from a specific time (for reproducibility).

    Args:
        symbol: Stock symbol
        timestamp: Timestamp to query

    Returns:
        Market data snapshot or None
    """
    db = get_database()

    # Find closest snapshot before or at timestamp
    doc = await db.market_data_cache.find_one(
        {"symbol": symbol.upper(), "timestamp": {"$lte": timestamp}},
        sort=[("timestamp", -1)],
    )

    if doc:
        doc.pop("_id", None)
        return doc

    return None

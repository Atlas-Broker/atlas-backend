"""MongoDB async client using Motor."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from loguru import logger
from typing import Optional

# Global client and database
_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_client() -> AsyncIOMotorClient:
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
        )
        logger.info("Created MongoDB client")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    """Get or create MongoDB database."""
    global _db
    if _db is None:
        client = get_client()
        _db = client[settings.MONGODB_DB_NAME]
        logger.info(f"Connected to MongoDB database: {settings.MONGODB_DB_NAME}")
    return _db


async def init_mongodb():
    """Initialize MongoDB connection and indexes (called on startup)."""
    db = get_database()

    try:
        # Create indexes for agent_runs collection
        await db.agent_runs.create_index("run_id", unique=True)
        await db.agent_runs.create_index("user_id")
        await db.agent_runs.create_index("timestamp")
        await db.agent_runs.create_index([("timestamp", -1)])  # Descending for recent queries

        # Create indexes for market_data_cache collection
        await db.market_data_cache.create_index("symbol")
        # Use sparse=True to allow null values, only enforce uniqueness on non-null
        await db.market_data_cache.create_index("cache_key", unique=True, sparse=True)
        await db.market_data_cache.create_index("expires_at", expireAfterSeconds=0)  # TTL index

        logger.info("MongoDB indexes created")
    except Exception as e:
        # If index already exists or has duplicate keys, handle gracefully
        error_str = str(e).lower()
        if "already exists" in error_str or "duplicate key" in error_str:
            logger.warning(f"MongoDB index warning (non-critical): {e}")
            logger.info("Continuing with existing indexes")
        else:
            raise


async def close_mongodb():
    """Close MongoDB connection (called on shutdown)."""
    global _client, _db
    if _client:
        _client.close()
        logger.info("MongoDB connection closed")
        _client = None
        _db = None

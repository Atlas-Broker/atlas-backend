"""Fix MongoDB indexes by dropping and recreating collections."""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "atlas-mongodb")


async def fix_indexes():
    """Drop market_data_cache collection and let server recreate indexes."""
    
    print("Connecting to MongoDB...")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    
    try:
        # Drop the problematic collection
        print(f"Dropping market_data_cache collection in {MONGODB_DB_NAME}...")
        await db.market_data_cache.drop()
        print("✅ Collection dropped successfully!")
        
        print("\nThe server will recreate the collection with proper indexes on next startup.")
        print("You can now run: uvicorn app.main:app --reload")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()
        print("\n✅ MongoDB connection closed")


if __name__ == "__main__":
    print("=" * 60)
    print("MongoDB Index Fix Script")
    print("=" * 60)
    print()
    
    asyncio.run(fix_indexes())

"""Shared dependencies for FastAPI."""

from app.db.supabase.client import get_db
from app.db.mongodb.client import get_database


def get_supabase_session():
    """Dependency to get Supabase session."""
    return get_db()


def get_mongodb():
    """Dependency to get MongoDB database."""
    return get_database()

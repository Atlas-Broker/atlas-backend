"""Configuration management using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str

    # Supabase (PostgreSQL)
    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str

    # MongoDB
    MONGODB_URI: str
    MONGODB_DB_NAME: str = "atlas_production"

    # S3 (AWS)
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "atlas-artifacts"

    # Google AI (Gemini)
    GOOGLE_AI_API_KEY: str

    # Yahoo Finance
    YAHOO_RATE_LIMIT_CALLS: int = 100
    YAHOO_RATE_LIMIT_PERIOD: int = 3600

    # Paper Trading
    PAPER_STARTING_CASH: float = 100000.00
    PAPER_MAX_POSITIONS: int = 10
    PAPER_MAX_POSITION_SIZE: float = 10000.00

    # Autonomous Pilot Schedule
    PILOT_SCHEDULE_CRON: str = "0 9,15 * * 1-5"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

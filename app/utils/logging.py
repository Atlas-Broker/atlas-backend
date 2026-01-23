"""Logging configuration using Loguru."""

import sys
from loguru import logger
from app.config import settings


def setup_logging():
    """Configure Loguru logger with structured output."""

    # Remove default handler
    logger.remove()

    # Add custom handler with formatting
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.LOG_LEVEL,
        colorize=True,
    )

    # Add file handler for production
    if settings.ENVIRONMENT != "development":
        logger.add(
            "logs/atlas_{time:YYYY-MM-DD}.log",
            rotation="1 day",
            retention="30 days",
            level=settings.LOG_LEVEL,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        )

    return logger

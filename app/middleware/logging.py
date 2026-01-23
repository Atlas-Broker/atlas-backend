"""Request logging middleware."""

from fastapi import Request
from loguru import logger
import time
from typing import Callable


async def log_requests(request: Request, call_next: Callable):
    """
    Log all HTTP requests with timing.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    start_time = time.time()

    # Log request
    logger.info(f"{request.method} {request.url.path}")

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(duration)

    return response

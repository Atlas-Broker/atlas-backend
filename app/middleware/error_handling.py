"""Global error handling."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger


async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle uncaught exceptions globally.

    Args:
        request: FastAPI request
        exc: Exception raised

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if logger.level("DEBUG").no <= logger._core.min_level else None,
        },
    )


async def value_error_handler(request: Request, exc: ValueError):
    """
    Handle ValueError as 400 Bad Request.

    Args:
        request: FastAPI request
        exc: ValueError raised

    Returns:
        JSON error response
    """
    logger.warning(f"ValueError: {exc}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Bad request", "detail": str(exc)},
    )

"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import settings
from app.utils.logging import setup_logging
from app.api.v1.router import router as v1_router
from app.db.supabase.client import init_db, close_db
from app.db.mongodb.client import init_mongodb, close_mongodb
from app.scheduler.scheduler import start_scheduler, stop_scheduler
from app.middleware.logging import log_requests
from app.middleware.error_handling import global_exception_handler, value_error_handler

from loguru import logger

# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Initialize database connections, start scheduler
    - Shutdown: Close connections, stop scheduler
    """
    # Startup
    logger.info("Starting Atlas Backend...")

    try:
        await init_db()
        await init_mongodb()
        start_scheduler()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Atlas Backend...")
    try:
        await close_db()
        await close_mongodb()
        stop_scheduler()
        logger.info("All services shut down successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="Atlas Intelligence API",
    description="Agentic AI Swing Trading Backend with Streaming",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS - MUST allow streaming
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)

# Request logging middleware
app.middleware("http")(log_requests)

# Exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

# Include API routers
app.include_router(v1_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Atlas Intelligence API",
        "version": "1.0.0",
        "status": "healthy",
        "streaming": "enabled",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "streaming_enabled": True,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )

"""Main v1 router aggregating all endpoints."""

from fastapi import APIRouter
from app.api.v1 import agent, orders, portfolio, trades, traces, jobs

# Create v1 router
router = APIRouter(prefix="/v1")

# Include all sub-routers
router.include_router(agent.router)
router.include_router(orders.router)
router.include_router(portfolio.router)
router.include_router(trades.router)
router.include_router(traces.router)
router.include_router(jobs.router)

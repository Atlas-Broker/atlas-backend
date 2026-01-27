"""Job management endpoints (admin only)."""

from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth import verify_clerk_token, User
from app.agents.autonomous_pilot import run_autonomous_pilot
from app.scheduler.scheduler import get_scheduler
from app.db.mongodb.queries import get_recent_agent_runs
from loguru import logger

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/run-pilot")
async def trigger_pilot_run(user: User = Depends(verify_clerk_token)):
    """
    Manually trigger an autonomous pilot run (admin only).

    This bypasses the scheduled cron job and runs the pilot immediately.

    Useful for:
    - Testing
    - Manual intervention
    - Debugging

    TODO: Add admin role check
    """
    logger.info(f"User {user.id} manually triggered pilot run")

    try:
        result = await run_autonomous_pilot()

        return {
            "run_id": result["run_id"],
            "status": result["status"],
            "trades_executed": result.get("reflection", {}).get("trades_executed", 0),
            "message": "Pilot run completed successfully",
        }

    except Exception as e:
        logger.error(f"Manual pilot run failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pilot run failed: {str(e)}")


@router.get("/pilot-status")
async def get_pilot_status(user: User = Depends(verify_clerk_token)):
    """
    Get status of autonomous pilot.

    Returns:
    - Last run timestamp and result
    - Next scheduled run time
    - Scheduler status
    """
    # Get last pilot run from MongoDB
    recent_runs = await get_recent_agent_runs("AUTONOMOUS_PILOT", limit=1, mode="autonomous")

    last_run = recent_runs[0] if recent_runs else None

    # Get scheduler info
    scheduler = get_scheduler()
    pilot_job = scheduler.get_job("autonomous_pilot")

    next_run = pilot_job.next_run_time if pilot_job else None

    return {
        "scheduler_running": scheduler.running,
        "next_run": next_run.isoformat() if next_run else None,
        "last_run": {
            "run_id": last_run["run_id"],
            "timestamp": last_run["timestamp"],
            "status": last_run["status"],
            "trades_executed": last_run.get("reflection", {}).get("trades_executed", 0),
        }
        if last_run
        else None,
    }


# ============================================================
# DEVELOPMENT ENDPOINTS (No Authentication Required)
# ============================================================

@router.post("/run-pilot-dev")
async def trigger_pilot_dev():
    """
    🔓 DEV ONLY: Trigger autonomous pilot without authentication.
    
    ⚠️ WARNING: This endpoint bypasses authentication!
    Only available in development mode.
    
    Use this for local testing without setting up Clerk authentication.
    """
    from app.config import settings
    
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development mode"
        )
    
    logger.info("DEV: Manually triggered pilot run (no auth)")
    
    try:
        result = await run_autonomous_pilot()
        
        return {
            "run_id": result["run_id"],
            "status": result["status"],
            "mode": "development",
            "trades_executed": result.get("reflection", {}).get("trades_executed", 0),
            "total_decisions": len(result.get("decisions", [])),
            "duration_ms": result.get("duration_ms"),
            "message": "✅ Pilot run completed successfully (DEV MODE)",
            "decisions_summary": [
                {
                    "symbol": d.get("symbol"),
                    "action": d.get("action"),
                    "quantity": d.get("quantity"),
                    "confidence": d.get("confidence", 0)
                }
                for d in result.get("decisions", [])
            ]
        }
        
    except Exception as e:
        logger.error(f"DEV pilot run failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Pilot run failed: {str(e)}")

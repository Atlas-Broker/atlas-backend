"""Agent trace endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from app.middleware.auth import verify_clerk_token, User
from app.db.mongodb.queries import get_agent_run, get_recent_agent_runs
from typing import Optional

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/{run_id}")
async def get_trace(
    run_id: str,
    user: User = Depends(verify_clerk_token),
):
    """
    Get complete agent run trace from MongoDB.

    Returns full black box flight recorder data:
    - All tool calls with raw results
    - Agent reasoning and thoughts
    - Trade proposal
    - Execution timeline

    This is useful for debugging and understanding agent decisions.
    """
    trace = await get_agent_run(run_id)

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    # Verify ownership (unless it's a pilot trace)
    if trace["user_id"] != "AUTONOMOUS_PILOT" and trace["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return trace


@router.get("")
async def list_traces(
    user: User = Depends(verify_clerk_token),
    mode: Optional[str] = Query(None, description="Filter by mode (copilot/autonomous)"),
    limit: int = Query(20, le=50),
):
    """
    List recent agent runs for the user.

    Query parameters:
    - `mode`: Filter by mode (copilot or autonomous)
    - `limit`: Number of traces (default 20, max 50)
    """
    traces = await get_recent_agent_runs(user.id, limit, mode)

    # Return summary view (not full traces)
    summaries = [
        {
            "run_id": t["run_id"],
            "timestamp": t["timestamp"],
            "input": t["input"][:100],  # Truncate
            "mode": t["mode"],
            "status": t["status"],
            "proposal": t.get("proposal", {}).get("action"),
            "symbol": t.get("proposal", {}).get("symbol"),
            "tools_called_count": len(t.get("tools_called", [])),
        }
        for t in traces
    ]

    return {"traces": summaries, "total": len(summaries)}

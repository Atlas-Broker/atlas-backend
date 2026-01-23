"""Agent copilot endpoints with streaming support."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.agents.orchestrator import run_orchestrator_streaming
from app.middleware.auth import verify_clerk_token, User
from app.schemas.agent import AgentRequest
from app.utils.streaming import create_sse_headers
from loguru import logger
import json

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/analyze")
async def analyze_intent(
    request: AgentRequest,
    user: User = Depends(verify_clerk_token),
):
    """
    Stream agent reasoning and proposals in real-time.

    **This is the centerpiece of the demo - streaming agent analysis.**

    Returns Server-Sent Events (SSE) with:
    - `status`: ANALYZING | PROPOSING | COMPLETE | ERROR
    - `thinking`: Agent's current thought process
    - `tool_call`: Tool being executed
    - `tool_result`: Tool output summary
    - `proposal`: Final trade proposal
    - `complete`: Final event with trace_id and order_id

    The frontend should listen to these events and display live updates
    as the agent thinks, calls tools, and makes decisions.

    Example event stream:
    ```
    event: status
    data: {"status": "ANALYZING", "run_id": "abc-123"}

    event: thinking
    data: {"thought": "Let me check NVDA's current price..."}

    event: tool_call
    data: {"tool": "get_market_data", "params": {"symbol": "NVDA"}}

    event: tool_result
    data: {"tool": "get_market_data", "summary": "NVDA: $140.50 (+2.34%)"}

    event: proposal
    data: {"action": "BUY", "symbol": "NVDA", "quantity": 10, ...}

    event: complete
    data: {"trace_id": "abc-123", "order_id": "order-456"}
    ```
    """
    logger.info(f"User {user.id} requested analysis: {request.intent[:50]}...")

    async def event_generator():
        try:
            async for event in run_orchestrator_streaming(
                user_id=user.id, intent=request.intent
            ):
                # Format as SSE
                yield f"event: {event['type']}\n"
                yield f"data: {json.dumps(event['data'])}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}", exc_info=True)
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers=create_sse_headers(),
    )

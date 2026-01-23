"""SSE (Server-Sent Events) streaming utilities."""

import json
from typing import Dict, Any, AsyncGenerator


async def format_sse(event_type: str, data: Dict[str, Any]) -> str:
    """
    Format data as Server-Sent Event.

    Args:
        event_type: Type of event (status, thinking, tool_call, etc.)
        data: Event payload

    Returns:
        Formatted SSE string with event and data fields
    """
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def sse_generator(events: AsyncGenerator[Dict[str, Any], None]) -> AsyncGenerator[str, None]:
    """
    Convert event dictionaries to SSE format.

    Args:
        events: Async generator yielding event dictionaries with 'type' and 'data' keys

    Yields:
        SSE-formatted strings
    """
    async for event in events:
        yield await format_sse(event["type"], event["data"])


def create_sse_headers() -> Dict[str, str]:
    """
    Create HTTP headers for SSE streaming.

    Returns:
        Dictionary of headers for streaming responses
    """
    return {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",  # Disable nginx buffering
        "Content-Type": "text/event-stream",
    }

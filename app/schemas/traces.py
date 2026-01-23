"""Trace schemas."""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime


class ToolCallDetail(BaseModel):
    """Tool call detail."""

    tool: str
    symbol: Optional[str] = None
    params: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: str
    cache_hit: bool = False
    duration_ms: Optional[int] = None


class TraceResponse(BaseModel):
    """Agent run trace."""

    run_id: str
    user_id: str
    timestamp: datetime
    input: str
    mode: str
    tools_called: List[ToolCallDetail]
    reasoning: Dict[str, Any]
    proposal: Optional[Dict[str, Any]] = None
    decisions: List[Dict[str, Any]] = []
    reflection: Optional[Dict[str, Any]] = None
    status: str
    error: Optional[str] = None
    duration_ms: Optional[int] = None

"""Order schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class OrderResponse(BaseModel):
    """Order details."""

    id: str
    symbol: str
    side: str
    quantity: int
    status: str
    filled_price: Optional[float] = None
    filled_at: Optional[datetime] = None
    confidence_score: Optional[float] = None
    reasoning_summary: Optional[str] = None
    created_at: datetime
    agent_run_id: Optional[str] = None


class ApproveOrderRequest(BaseModel):
    """Request to approve an order."""

    pass  # No body needed, just order_id in path


class RejectOrderRequest(BaseModel):
    """Request to reject an order."""

    pass  # No body needed


class OrderListResponse(BaseModel):
    """List of orders."""

    orders: list[OrderResponse]
    total: int

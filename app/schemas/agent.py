"""Agent request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List


class AgentRequest(BaseModel):
    """Request to agent for analysis."""

    intent: str = Field(..., description="User's trading intent or question", min_length=1)

    class Config:
        json_schema_extra = {
            "example": {"intent": "Should I buy NVDA? What does the chart look like?"}
        }


class AgentProposal(BaseModel):
    """Agent's trade proposal."""

    action: str = Field(..., description="BUY, SELL, or HOLD")
    symbol: Optional[str] = Field(None, description="Stock ticker")
    quantity: Optional[int] = Field(None, description="Number of shares")
    entry_price: Optional[float] = Field(None, description="Entry price")
    stop_loss: Optional[float] = Field(None, description="Stop loss level")
    target_price: Optional[float] = Field(None, description="Target price")
    confidence: float = Field(..., description="Confidence score 0-1")
    rationale: Optional[str] = Field(None, description="Reasoning")
    order_id: Optional[str] = Field(None, description="Created order ID")


class AgentResponse(BaseModel):
    """Complete agent response (non-streaming)."""

    run_id: str
    proposal: AgentProposal
    trace_url: Optional[str] = None

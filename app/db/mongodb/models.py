"""Pydantic models for MongoDB documents."""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class ToolCall(BaseModel):
    """Record of a tool execution."""

    tool: str
    symbol: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cache_hit: bool = False
    duration_ms: Optional[int] = None


class Reasoning(BaseModel):
    """Agent reasoning and analysis."""

    technical_signals: List[str] = Field(default_factory=list)
    trend_analysis: Optional[str] = None
    sentiment: Optional[str] = None
    risk_factors: List[str] = Field(default_factory=list)
    raw_thoughts: Optional[str] = None
    confidence_rationale: Optional[str] = None


class TradeProposal(BaseModel):
    """Proposed trade action."""

    action: str  # BUY, SELL, HOLD
    symbol: str
    quantity: int
    entry_price: float
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None
    confidence: float
    holding_window: Optional[str] = None  # e.g., "3-5 days"
    rationale: Optional[str] = None


class AgentDecision(BaseModel):
    """Single decision in autonomous mode (per symbol)."""

    symbol: str
    action: str  # BUY, SELL, HOLD
    quantity: Optional[int] = None
    reasoning: str
    confidence: float
    trade_result: Optional[Dict[str, Any]] = None


class Reflection(BaseModel):
    """Post-execution reflection."""

    portfolio_change: Dict[str, Any] = Field(default_factory=dict)
    trades_executed: int = 0
    total_pnl: Optional[float] = None
    lessons_learned: List[str] = Field(default_factory=list)
    performance_notes: Optional[str] = None


class AgentRun(BaseModel):
    """Complete agent run trace (black box flight recorder)."""

    run_id: str
    user_id: str  # "AUTONOMOUS_PILOT" for pilot
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    input: str  # User intent or autonomous trigger
    mode: str = "copilot"  # copilot | autonomous

    # Execution trace
    tools_called: List[ToolCall] = Field(default_factory=list)
    reasoning: Reasoning = Field(default_factory=Reasoning)
    proposal: Optional[TradeProposal] = None

    # Autonomous mode specific
    decisions: List[AgentDecision] = Field(default_factory=list)
    reflection: Optional[Reflection] = None

    # Metadata
    status: str = "ANALYZING"  # ANALYZING | PROPOSING | COMPLETE | ERROR
    error: Optional[str] = None
    duration_ms: Optional[int] = None
    ended_at: Optional[datetime] = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class MarketDataCache(BaseModel):
    """Cached market data with raw Yahoo Finance response."""

    symbol: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = "yahoo_finance"

    # Raw data from source (reproducibility)
    data: Dict[str, Any] = Field(default_factory=dict)

    # Processed/cleaned data
    processed: Dict[str, Any] = Field(default_factory=dict)

    # Cache metadata
    expires_at: datetime
    cache_key: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

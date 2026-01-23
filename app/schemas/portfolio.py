"""Portfolio schemas."""

from pydantic import BaseModel
from typing import List


class Position(BaseModel):
    """Portfolio position."""

    symbol: str
    quantity: int
    avg_entry_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float


class PortfolioSummary(BaseModel):
    """Portfolio summary."""

    account_id: str
    cash: float
    positions: List[Position]
    positions_value: float
    total_equity: float
    starting_cash: float
    return_pct: float


class EquityPoint(BaseModel):
    """Single equity curve data point."""

    timestamp: str
    equity: float
    cash: float
    positions_value: float


class EquityCurveResponse(BaseModel):
    """Equity curve data."""

    points: List[EquityPoint]
    current_equity: float
    starting_equity: float
    total_return_pct: float

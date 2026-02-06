"""
Public API endpoints for AI Agent Competition.

No authentication required - public landing page data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.supabase.client import get_session
from app.db.supabase import queries
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

router = APIRouter(prefix="/competition", tags=["Agent Competition"])


# ============================================
# RESPONSE MODELS
# ============================================


class CompetitorResponse(BaseModel):
    """Competitor information."""

    id: str
    name: str
    model_id: str
    description: Optional[str]
    initial_capital: float
    current_equity: float
    total_return: float
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    win_rate: Optional[float]
    total_trades: int
    started_at: str
    last_trade_at: Optional[str]


class DailyPerformanceResponse(BaseModel):
    """Daily performance data."""

    competitor_id: str
    competitor_name: str
    trading_date: str
    equity: float
    daily_return: Optional[float]
    cumulative_return: Optional[float]


class LeaderboardResponse(BaseModel):
    """Leaderboard entry."""

    rank: int
    competitor_id: str
    name: str
    model_id: str
    equity: float
    total_return: float
    win_rate: Optional[float]
    total_trades: int


class PositionResponse(BaseModel):
    """Agent position."""

    symbol: str
    quantity: int
    avg_entry_price: float
    current_price: Optional[float]
    unrealized_pnl: Optional[float]
    market_value: Optional[float]
    weight: Optional[float]


class TradeResponse(BaseModel):
    """Agent trade."""

    id: str
    symbol: str
    side: str
    quantity: int
    price: float
    total_amount: float
    reasoning_summary: Optional[str]
    confidence_score: Optional[float]
    executed_at: str


class ReasoningResponse(BaseModel):
    """Agent reasoning detail."""

    reasoning_type: str
    content: str
    created_at: str


# ============================================
# PUBLIC ENDPOINTS (No Auth Required)
# ============================================


@router.get("/leaderboard", response_model=List[LeaderboardResponse])
async def get_leaderboard(session: AsyncSession = Depends(get_session)):
    """
    Get current leaderboard rankings.

    Public endpoint - no authentication required.
    """
    leaderboard = await queries.get_current_leaderboard(session)

    if not leaderboard:
        # If no leaderboard today, return competitors sorted by equity
        competitors = await queries.get_all_competitors(session)
        return [
            LeaderboardResponse(
                rank=i + 1,
                competitor_id=str(c.id),
                name=c.name,
                model_id=c.model_id,
                equity=float(c.current_equity),
                total_return=float(c.total_return) if c.total_return else 0.0,
                win_rate=float(c.win_rate) if c.win_rate else None,
                total_trades=c.total_trades,
            )
            for i, c in enumerate(competitors)
        ]

    # Return today's leaderboard
    result = []
    for entry in leaderboard:
        competitor = await queries.get_competitor_by_id(session, entry.competitor_id)
        result.append(
            LeaderboardResponse(
                rank=entry.rank,
                competitor_id=str(entry.competitor_id),
                name=competitor.name,
                model_id=competitor.model_id,
                equity=float(entry.equity),
                total_return=float(entry.total_return),
                win_rate=float(entry.win_rate) if entry.win_rate else None,
                total_trades=entry.total_trades,
            )
        )

    return result


@router.get("/performance", response_model=List[DailyPerformanceResponse])
async def get_performance_chart(
    days: int = 30, session: AsyncSession = Depends(get_session)
):
    """
    Get daily performance data for all agents (for chart).

    Public endpoint - no authentication required.
    """
    performance_data = await queries.get_daily_performance(session, days=days)

    # Group by competitor and get names
    result = []
    competitor_cache = {}

    for perf in performance_data:
        if perf.competitor_id not in competitor_cache:
            competitor = await queries.get_competitor_by_id(session, perf.competitor_id)
            competitor_cache[perf.competitor_id] = competitor

        competitor = competitor_cache[perf.competitor_id]

        result.append(
            DailyPerformanceResponse(
                competitor_id=str(perf.competitor_id),
                competitor_name=competitor.name,
                trading_date=perf.trading_date.isoformat(),
                equity=float(perf.equity),
                daily_return=float(perf.daily_return) if perf.daily_return else None,
                cumulative_return=float(perf.cumulative_return)
                if perf.cumulative_return
                else None,
            )
        )

    return result


@router.get("/competitors", response_model=List[CompetitorResponse])
async def get_all_competitors_endpoint(session: AsyncSession = Depends(get_session)):
    """
    Get all active competitors.

    Public endpoint - no authentication required.
    """
    competitors = await queries.get_all_competitors(session)

    return [
        CompetitorResponse(
            id=str(c.id),
            name=c.name,
            model_id=c.model_id,
            description=c.description,
            initial_capital=float(c.initial_capital),
            current_equity=float(c.current_equity),
            total_return=float(c.total_return) if c.total_return else 0.0,
            sharpe_ratio=float(c.sharpe_ratio) if c.sharpe_ratio else None,
            max_drawdown=float(c.max_drawdown) if c.max_drawdown else None,
            win_rate=float(c.win_rate) if c.win_rate else None,
            total_trades=c.total_trades,
            started_at=c.started_at.isoformat(),
            last_trade_at=c.last_trade_at.isoformat() if c.last_trade_at else None,
        )
        for c in competitors
    ]


@router.get("/portfolio/{competitor_id}", response_model=List[PositionResponse])
async def get_agent_portfolio(
    competitor_id: UUID, session: AsyncSession = Depends(get_session)
):
    """
    Get current portfolio for a specific agent.

    Public endpoint - no authentication required.
    """
    positions = await queries.get_agent_positions(session, competitor_id)

    return [
        PositionResponse(
            symbol=p.symbol,
            quantity=p.quantity,
            avg_entry_price=float(p.avg_entry_price),
            current_price=float(p.current_price) if p.current_price else None,
            unrealized_pnl=float(p.unrealized_pnl) if p.unrealized_pnl else None,
            market_value=float(p.market_value) if p.market_value else None,
            weight=float(p.weight) if p.weight else None,
        )
        for p in positions
    ]


@router.get("/trades/{competitor_id}", response_model=List[TradeResponse])
async def get_agent_trades_endpoint(
    competitor_id: UUID, limit: int = 50, session: AsyncSession = Depends(get_session)
):
    """
    Get trade history for a specific agent.

    Public endpoint - no authentication required.
    """
    trades = await queries.get_agent_trades(session, competitor_id, limit)

    return [
        TradeResponse(
            id=str(t.id),
            symbol=t.symbol,
            side=t.side.value,
            quantity=t.quantity,
            price=float(t.price),
            total_amount=float(t.total_amount),
            reasoning_summary=t.reasoning_summary,
            confidence_score=float(t.confidence_score) if t.confidence_score else None,
            executed_at=t.executed_at.isoformat(),
        )
        for t in trades
    ]


@router.get("/reasoning/{competitor_id}", response_model=List[ReasoningResponse])
async def get_agent_reasoning_endpoint(
    competitor_id: UUID,
    reasoning_type: Optional[str] = None,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    """
    Get reasoning records for explainable AI.

    Public endpoint - no authentication required.
    Shows WHY the agent made decisions.
    """
    reasoning = await queries.get_agent_reasoning(
        session, competitor_id=competitor_id, reasoning_type=reasoning_type, limit=limit
    )

    return [
        ReasoningResponse(
            reasoning_type=r.reasoning_type,
            content=r.content,
            created_at=r.created_at.isoformat(),
        )
        for r in reasoning
    ]

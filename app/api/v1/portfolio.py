"""Portfolio endpoints."""

from fastapi import APIRouter, Depends
from app.middleware.auth import verify_clerk_token, User
from app.services.portfolio import get_portfolio_state
from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import get_equity_curve, get_account_by_user_id
from loguru import logger

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/summary")
async def get_portfolio_summary(user: User = Depends(verify_clerk_token)):
    """
    Get current portfolio summary.

    Returns:
    - Cash balance
    - Current positions with P&L
    - Total equity
    - Overall return percentage
    """
    portfolio = await get_portfolio_state(user.id)

    logger.info(f"Portfolio summary for {user.id}: equity=${portfolio['total_equity']:.2f}")

    return portfolio


@router.get("/equity-curve")
async def get_equity_curve_endpoint(
    user: User = Depends(verify_clerk_token),
    limit: int = 100,
):
    """
    Get historical equity curve data.

    Returns time series of portfolio equity values for charting.

    Query parameters:
    - `limit`: Number of data points (default 100)
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        account = await get_account_by_user_id(session, user.id)

        if not account:
            return {
                "points": [],
                "current_equity": 0,
                "starting_equity": 0,
                "total_return_pct": 0,
            }

        snapshots = await get_equity_curve(session, account.id, limit)

        points = [
            {
                "timestamp": s.timestamp.isoformat(),
                "equity": float(s.equity),
                "cash": float(s.cash),
                "positions_value": float(s.positions_value),
            }
            for s in reversed(snapshots)  # Oldest first for charting
        ]

        current_equity = float(snapshots[0].equity) if snapshots else 0
        starting_equity = float(account.starting_cash)
        total_return_pct = (
            ((current_equity - starting_equity) / starting_equity * 100)
            if starting_equity > 0
            else 0
        )

        return {
            "points": points,
            "current_equity": current_equity,
            "starting_equity": starting_equity,
            "total_return_pct": total_return_pct,
        }


@router.get("/positions")
async def get_positions(user: User = Depends(verify_clerk_token)):
    """
    Get current portfolio positions with P&L.

    Returns detailed position information including:
    - Entry price and current price
    - Unrealized P&L (dollar and percentage)
    - Market value
    """
    portfolio = await get_portfolio_state(user.id)

    return {
        "positions": portfolio["positions"],
        "total_value": portfolio["positions_value"],
        "count": len(portfolio["positions"]),
    }

"""Trade history endpoints."""

from fastapi import APIRouter, Depends, Query
from app.middleware.auth import verify_clerk_token, User
from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import get_recent_orders, get_account_by_user_id
from app.db.supabase.models import OrderStatus

router = APIRouter(prefix="/trades", tags=["trades"])


@router.get("/recent")
async def get_recent_trades(
    user: User = Depends(verify_clerk_token),
    limit: int = Query(50, le=100),
):
    """
    Get recent filled trades.

    Returns only FILLED orders (executed trades), sorted by most recent.

    Query parameters:
    - `limit`: Maximum number of trades (default 50, max 100)
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        account = await get_account_by_user_id(session, user.id)

        if not account:
            return {"trades": [], "total": 0}

        orders = await get_recent_orders(session, account.id, limit)

        # Filter to only filled orders
        filled_orders = [o for o in orders if o.status == OrderStatus.FILLED]

        trades = [
            {
                "id": str(o.id),
                "symbol": o.symbol,
                "side": o.side,
                "quantity": o.quantity,
                "filled_price": float(o.filled_price),
                "filled_at": o.filled_at,
                "cost": o.quantity * float(o.filled_price),
                "confidence_score": float(o.confidence_score) if o.confidence_score else None,
                "reasoning_summary": o.reasoning_summary,
                "agent_run_id": o.agent_run_id,
            }
            for o in filled_orders
        ]

        return {"trades": trades, "total": len(trades)}

"""Order management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.middleware.auth import verify_clerk_token, User
from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import (
    approve_order,
    reject_order,
    get_recent_orders,
    get_account_by_user_id,
)
from app.db.supabase.models import PaperOrder
from app.services.order_execution import execute_paper_trade
from app.services.market_data import get_market_data
from app.services.portfolio import update_position_after_trade
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from loguru import logger
from typing import Optional

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/{order_id}/approve")
async def approve_order_endpoint(
    order_id: str,
    user: User = Depends(verify_clerk_token),
):
    """
    Approve a proposed trade and execute it.

    This transitions the order from PROPOSED → APPROVED → FILLED.

    Steps:
    1. Verify order belongs to user
    2. Mark as approved
    3. Execute at current market price
    4. Update portfolio positions
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get order
        result = await session.execute(
            select(PaperOrder).where(PaperOrder.id == UUID(order_id))
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Verify ownership
        result = await session.execute(
            select(PaperOrder).where(PaperOrder.id == UUID(order_id))
        )
        order_with_account = result.scalar_one_or_none()

        # Check user owns this account
        account = await get_account_by_user_id(session, user.id)
        if not account or str(order.account_id) != str(account.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Approve order
        approved_order = await approve_order(session, UUID(order_id))

        # Execute trade
        from app.db.supabase.queries import fill_order
        from app.db.supabase.models import PaperAccount

        # Get current price
        market_data = await get_market_data(order.symbol)
        current_price = market_data["current_price"]

        # Fill order
        filled_order = await fill_order(session, UUID(order_id), current_price)

        # Update cash balance
        if order.side == "BUY":
            cost = order.quantity * current_price
            await session.execute(
                update(PaperAccount)
                .where(PaperAccount.id == order.account_id)
                .values(cash_balance=PaperAccount.cash_balance - cost)
            )
        elif order.side == "SELL":
            proceeds = order.quantity * current_price
            await session.execute(
                update(PaperAccount)
                .where(PaperAccount.id == order.account_id)
                .values(cash_balance=PaperAccount.cash_balance + proceeds)
            )

        await session.commit()

        # Update position
        await update_position_after_trade(
            order.account_id, order.symbol, order.side, order.quantity, current_price
        )

        logger.info(f"Approved and executed order {order_id}")

        return {
            "order_id": str(filled_order.id),
            "status": "FILLED",
            "filled_price": float(filled_order.filled_price),
            "message": "Order approved and executed successfully",
        }


@router.post("/{order_id}/reject")
async def reject_order_endpoint(
    order_id: str,
    user: User = Depends(verify_clerk_token),
):
    """
    Reject a proposed trade.

    The order will be marked as REJECTED and will not execute.
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get order
        result = await session.execute(
            select(PaperOrder).where(PaperOrder.id == UUID(order_id))
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Verify ownership
        account = await get_account_by_user_id(session, user.id)
        if not account or str(order.account_id) != str(account.id):
            raise HTTPException(status_code=403, detail="Not authorized")

        # Reject order
        rejected_order = await reject_order(session, UUID(order_id))

        logger.info(f"Rejected order {order_id}")

        return {
            "order_id": str(rejected_order.id),
            "status": "REJECTED",
            "message": "Order rejected",
        }


@router.get("")
async def list_orders(
    user: User = Depends(verify_clerk_token),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, le=100),
):
    """
    List orders for the authenticated user.

    Query parameters:
    - `status`: Filter by status (PROPOSED, APPROVED, FILLED, REJECTED)
    - `limit`: Maximum number of orders to return (default 50, max 100)
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        account = await get_account_by_user_id(session, user.id)

        if not account:
            return {"orders": [], "total": 0}

        orders = await get_recent_orders(session, account.id, limit)

        # Filter by status if requested
        if status_filter:
            orders = [o for o in orders if o.status.value.upper() == status_filter.upper()]

        orders_list = [
            {
                "id": str(o.id),
                "symbol": o.symbol,
                "side": o.side,
                "quantity": o.quantity,
                "status": o.status.value,
                "filled_price": float(o.filled_price) if o.filled_price else None,
                "filled_at": o.filled_at,
                "confidence_score": float(o.confidence_score) if o.confidence_score else None,
                "reasoning_summary": o.reasoning_summary,
                "created_at": o.created_at,
                "agent_run_id": o.agent_run_id,
            }
            for o in orders
        ]

        return {"orders": orders_list, "total": len(orders_list)}

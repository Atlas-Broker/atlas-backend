"""Reusable Supabase queries."""

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.supabase.models import PaperAccount, PaperOrder, PaperPosition, EquitySnapshot, OrderStatus
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from loguru import logger


async def get_or_create_pilot_account(session: AsyncSession) -> PaperAccount:
    """
    Get or create the autonomous pilot account.

    Args:
        session: Database session

    Returns:
        Pilot account object
    """
    result = await session.execute(
        select(PaperAccount).where(PaperAccount.user_id.is_(None))
    )
    account = result.scalar_one_or_none()

    if not account:
        from app.config import settings

        account = PaperAccount(
            user_id=None,
            cash_balance=settings.PAPER_STARTING_CASH,
            starting_cash=settings.PAPER_STARTING_CASH,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)
        logger.info(f"Created pilot account: {account.id}")

    return account


async def get_account_by_user_id(session: AsyncSession, user_id: str) -> Optional[PaperAccount]:
    """Get paper account for a user."""
    result = await session.execute(
        select(PaperAccount).where(PaperAccount.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_paper_order(
    session: AsyncSession,
    account_id: UUID,
    symbol: str,
    side: str,
    quantity: int,
    agent_run_id: str,
    confidence_score: Optional[float] = None,
    reasoning_summary: Optional[str] = None,
) -> PaperOrder:
    """
    Create a new paper order in PROPOSED status.

    Args:
        session: Database session
        account_id: Account UUID
        symbol: Stock symbol
        side: BUY or SELL
        quantity: Number of shares
        agent_run_id: MongoDB trace ID
        confidence_score: Agent confidence (0-1)
        reasoning_summary: Brief reasoning text

    Returns:
        Created order object
    """
    order = PaperOrder(
        account_id=account_id,
        symbol=symbol.upper(),
        side=side.upper(),
        quantity=quantity,
        status=OrderStatus.PROPOSED,
        agent_run_id=agent_run_id,
        confidence_score=confidence_score,
        reasoning_summary=reasoning_summary,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    logger.info(f"Created order {order.id}: {side} {quantity} {symbol}")
    return order


async def approve_order(session: AsyncSession, order_id: UUID) -> PaperOrder:
    """Approve a proposed order."""
    result = await session.execute(select(PaperOrder).where(PaperOrder.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    if order.status != OrderStatus.PROPOSED:
        raise ValueError(f"Order {order_id} is not in PROPOSED status")

    order.status = OrderStatus.APPROVED
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Approved order {order_id}")
    return order


async def reject_order(session: AsyncSession, order_id: UUID) -> PaperOrder:
    """Reject a proposed order."""
    result = await session.execute(select(PaperOrder).where(PaperOrder.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    if order.status != OrderStatus.PROPOSED:
        raise ValueError(f"Order {order_id} is not in PROPOSED status")

    order.status = OrderStatus.REJECTED
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Rejected order {order_id}")
    return order


async def fill_order(
    session: AsyncSession, order_id: UUID, filled_price: float
) -> PaperOrder:
    """Mark order as filled with execution price."""
    result = await session.execute(select(PaperOrder).where(PaperOrder.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    order.status = OrderStatus.FILLED
    order.filled_price = filled_price
    order.filled_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Filled order {order_id} at ${filled_price}")
    return order


async def get_account_positions(
    session: AsyncSession, account_id: UUID
) -> List[PaperPosition]:
    """Get all current positions for an account."""
    result = await session.execute(
        select(PaperPosition).where(PaperPosition.account_id == account_id)
    )
    return list(result.scalars().all())


async def upsert_position(
    session: AsyncSession,
    account_id: UUID,
    symbol: str,
    quantity: int,
    avg_entry_price: float,
) -> PaperPosition:
    """Create or update a position."""
    result = await session.execute(
        select(PaperPosition).where(
            and_(PaperPosition.account_id == account_id, PaperPosition.symbol == symbol)
        )
    )
    position = result.scalar_one_or_none()

    if position:
        # Update existing position
        position.quantity = quantity
        position.avg_entry_price = avg_entry_price
        position.updated_at = datetime.utcnow()
    else:
        # Create new position
        position = PaperPosition(
            account_id=account_id,
            symbol=symbol.upper(),
            quantity=quantity,
            avg_entry_price=avg_entry_price,
        )
        session.add(position)

    await session.commit()
    await session.refresh(position)
    return position


async def delete_position(session: AsyncSession, account_id: UUID, symbol: str):
    """Delete a position (when sold completely)."""
    result = await session.execute(
        select(PaperPosition).where(
            and_(PaperPosition.account_id == account_id, PaperPosition.symbol == symbol)
        )
    )
    position = result.scalar_one_or_none()

    if position:
        await session.delete(position)
        await session.commit()
        logger.info(f"Deleted position {symbol} for account {account_id}")


async def save_equity_snapshot(session: AsyncSession, snapshot: Dict[str, Any]) -> EquitySnapshot:
    """Save equity snapshot for equity curve."""
    snap = EquitySnapshot(
        account_id=snapshot["account_id"],
        equity=snapshot["equity"],
        cash=snapshot["cash"],
        positions_value=snapshot["positions_value"],
        timestamp=snapshot.get("timestamp", datetime.utcnow()),
    )
    session.add(snap)
    await session.commit()
    await session.refresh(snap)
    return snap


async def get_equity_curve(
    session: AsyncSession, account_id: UUID, limit: int = 100
) -> List[EquitySnapshot]:
    """Get equity curve history."""
    result = await session.execute(
        select(EquitySnapshot)
        .where(EquitySnapshot.account_id == account_id)
        .order_by(EquitySnapshot.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_recent_orders(
    session: AsyncSession, account_id: UUID, limit: int = 50
) -> List[PaperOrder]:
    """Get recent orders for an account."""
    result = await session.execute(
        select(PaperOrder)
        .where(PaperOrder.account_id == account_id)
        .order_by(PaperOrder.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())

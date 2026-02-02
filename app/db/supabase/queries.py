"""Reusable Supabase queries - Unified Schema."""

from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.supabase.models import (
    Profile,
    Account,
    TraderSettings,
    Watchlist,
    Order,
    Position,
    EquitySnapshot,
    AuditLog,
    OrderStatus,
    OrderSide,
    OrderType,
    EnvironmentType,
    UserRole,
)
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from loguru import logger


# ============================================
# PROFILE QUERIES
# ============================================


async def get_pilot_profile(session: AsyncSession) -> Optional[Profile]:
    """
    Get the autonomous pilot profile.

    Returns:
        Pilot profile or None
    """
    result = await session.execute(
        select(Profile).where(Profile.is_system == True)
    )
    return result.scalar_one_or_none()


async def get_or_create_pilot_profile(session: AsyncSession) -> Profile:
    """
    Get or create the autonomous pilot profile.

    Returns:
        Pilot profile object
    """
    profile = await get_pilot_profile(session)

    if not profile:
        profile = Profile(
            clerk_id=None,
            email="pilot@atlas.ai",
            full_name="Autonomous Pilot",
            role=UserRole.SYSTEM,
            is_active=True,
            is_system=True,
        )
        session.add(profile)
        await session.commit()
        await session.refresh(profile)
        logger.info(f"Created pilot profile: {profile.id}")

    return profile


async def get_profile_by_clerk_id(session: AsyncSession, clerk_id: str) -> Optional[Profile]:
    """Get profile by Clerk user ID."""
    result = await session.execute(
        select(Profile).where(Profile.clerk_id == clerk_id)
    )
    return result.scalar_one_or_none()


async def create_profile(
    session: AsyncSession,
    clerk_id: str,
    email: str,
    full_name: Optional[str] = None,
) -> Profile:
    """Create a new user profile."""
    profile = Profile(
        clerk_id=clerk_id,
        email=email,
        full_name=full_name,
        role=UserRole.TRADER,
        is_active=True,
        is_system=False,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    logger.info(f"Created profile for {email}: {profile.id}")
    return profile


# ============================================
# ACCOUNT QUERIES
# ============================================


async def get_or_create_pilot_account(session: AsyncSession) -> Account:
    """
    Get or create the autonomous pilot's paper trading account.

    Returns:
        Pilot account object
    """
    # First get/create pilot profile
    profile = await get_or_create_pilot_profile(session)

    # Then get/create pilot's paper account
    result = await session.execute(
        select(Account)
        .where(Account.user_id == profile.id)
        .where(Account.environment == EnvironmentType.PAPER)
    )
    account = result.scalar_one_or_none()

    if not account:
        from app.config import settings

        account = Account(
            user_id=profile.id,
            environment=EnvironmentType.PAPER,
            cash_balance=settings.PAPER_STARTING_CASH,
            starting_cash=settings.PAPER_STARTING_CASH,
            total_equity=settings.PAPER_STARTING_CASH,
            is_active=True,
        )
        session.add(account)
        await session.commit()
        await session.refresh(account)
        logger.info(f"Created pilot account: {account.id}")

    return account


async def get_account_by_user_id(
    session: AsyncSession, user_id: UUID, environment: EnvironmentType = EnvironmentType.PAPER
) -> Optional[Account]:
    """Get account for a user."""
    result = await session.execute(
        select(Account)
        .where(Account.user_id == user_id)
        .where(Account.environment == environment)
    )
    return result.scalar_one_or_none()


async def create_account(
    session: AsyncSession,
    user_id: UUID,
    environment: EnvironmentType = EnvironmentType.PAPER,
    starting_cash: float = 100000.00,
) -> Account:
    """Create a new trading account."""
    account = Account(
        user_id=user_id,
        environment=environment,
        cash_balance=starting_cash,
        starting_cash=starting_cash,
        total_equity=starting_cash,
        is_active=True,
    )
    session.add(account)
    await session.commit()
    await session.refresh(account)
    logger.info(f"Created {environment.value} account for user {user_id}")
    return account


# ============================================
# ORDER QUERIES
# ============================================


async def create_order(
    session: AsyncSession,
    account_id: UUID,
    user_id: UUID,
    symbol: str,
    side: OrderSide,
    quantity: int,
    order_type: OrderType = OrderType.MARKET,
    environment: EnvironmentType = EnvironmentType.PAPER,
    agent_run_id: Optional[str] = None,
    confidence_score: Optional[float] = None,
    reasoning_summary: Optional[str] = None,
    agent_reasoning: Optional[Dict[str, Any]] = None,
    limit_price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> Order:
    """
    Create a new order in PROPOSED status.

    Args:
        session: Database session
        account_id: Account UUID
        user_id: User UUID (denormalized)
        symbol: Stock symbol
        side: Order side (buy, sell, short, cover)
        quantity: Number of shares
        order_type: Order type (market, limit, etc.)
        environment: Paper or live
        agent_run_id: MongoDB trace ID
        confidence_score: Agent confidence (0-1)
        reasoning_summary: Brief reasoning text
        agent_reasoning: Full reasoning JSONB
        limit_price: Limit price (for limit orders)
        stop_price: Stop price (for stop orders)

    Returns:
        Created order object
    """
    order = Order(
        account_id=account_id,
        user_id=user_id,
        symbol=symbol.upper(),
        side=side,
        quantity=quantity,
        order_type=order_type,
        status=OrderStatus.PROPOSED,
        environment=environment,
        agent_run_id=agent_run_id,
        confidence_score=confidence_score,
        reasoning_summary=reasoning_summary,
        agent_reasoning=agent_reasoning,
        limit_price=limit_price,
        stop_price=stop_price,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    logger.info(f"Created order {order.id}: {side.value} {quantity} {symbol}")
    return order


async def approve_order(
    session: AsyncSession, order_id: UUID, approved_by: UUID
) -> Order:
    """Approve a proposed order."""
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    if order.status != OrderStatus.PROPOSED:
        raise ValueError(f"Order {order_id} is not in PROPOSED status")

    order.status = OrderStatus.APPROVED
    order.approved_by = approved_by
    order.approved_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Approved order {order_id}")
    return order


async def reject_order(
    session: AsyncSession, order_id: UUID, reason: Optional[str] = None
) -> Order:
    """Reject a proposed order."""
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    if order.status != OrderStatus.PROPOSED:
        raise ValueError(f"Order {order_id} is not in PROPOSED status")

    order.status = OrderStatus.REJECTED
    order.rejected_reason = reason
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Rejected order {order_id}: {reason}")
    return order


async def fill_order(
    session: AsyncSession,
    order_id: UUID,
    filled_price: float,
    filled_quantity: Optional[int] = None,
) -> Order:
    """Mark order as filled with execution price."""
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise ValueError(f"Order {order_id} not found")

    order.status = OrderStatus.FILLED
    order.filled_price = filled_price
    order.filled_quantity = filled_quantity or order.quantity
    order.filled_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(order)
    logger.info(f"Filled order {order_id}: {order.filled_quantity} @ ${filled_price}")
    return order


async def get_recent_orders(
    session: AsyncSession,
    account_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None,
    limit: int = 50,
) -> List[Order]:
    """Get recent orders for an account or user."""
    query = select(Order)

    if account_id:
        query = query.where(Order.account_id == account_id)
    elif user_id:
        query = query.where(Order.user_id == user_id)

    query = query.order_by(Order.created_at.desc()).limit(limit)

    result = await session.execute(query)
    return list(result.scalars().all())


# ============================================
# POSITION QUERIES
# ============================================


async def get_account_positions(
    session: AsyncSession, account_id: UUID
) -> List[Position]:
    """Get all current positions for an account."""
    result = await session.execute(
        select(Position).where(Position.account_id == account_id)
    )
    return list(result.scalars().all())


async def upsert_position(
    session: AsyncSession,
    account_id: UUID,
    user_id: UUID,
    symbol: str,
    quantity: int,
    avg_entry_price: float,
    environment: EnvironmentType = EnvironmentType.PAPER,
) -> Position:
    """Create or update a position."""
    result = await session.execute(
        select(Position).where(
            and_(Position.account_id == account_id, Position.symbol == symbol)
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
        position = Position(
            account_id=account_id,
            user_id=user_id,
            symbol=symbol.upper(),
            quantity=quantity,
            avg_entry_price=avg_entry_price,
            environment=environment,
        )
        session.add(position)

    await session.commit()
    await session.refresh(position)
    return position


async def delete_position(session: AsyncSession, account_id: UUID, symbol: str):
    """Delete a position (when sold completely)."""
    result = await session.execute(
        select(Position).where(
            and_(Position.account_id == account_id, Position.symbol == symbol)
        )
    )
    position = result.scalar_one_or_none()

    if position:
        await session.delete(position)
        await session.commit()
        logger.info(f"Deleted position {symbol} for account {account_id}")


# ============================================
# EQUITY SNAPSHOT QUERIES
# ============================================


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


async def get_watchlist(session: AsyncSession, user_id: UUID) -> Optional[Watchlist]:
    """Get user's active watchlist."""
    result = await session.execute(
        select(Watchlist)
        .where(Watchlist.user_id == user_id)
        .where(Watchlist.is_active == True)
        .order_by(Watchlist.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_watchlist(
    session: AsyncSession, user_id: UUID, name: str, symbols: List[str]
) -> Watchlist:
    """Create a new watchlist."""
    watchlist = Watchlist(
        user_id=user_id,
        name=name,
        symbols=symbols,
        is_active=True,
    )
    session.add(watchlist)
    await session.commit()
    await session.refresh(watchlist)
    logger.info(f"Created watchlist '{name}' for user {user_id}")
    return watchlist

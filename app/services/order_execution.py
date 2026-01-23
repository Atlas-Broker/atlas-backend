"""Paper trade execution engine."""

from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import (
    create_paper_order,
    fill_order,
    get_or_create_pilot_account,
    get_account_by_user_id,
)
from app.db.supabase.models import PaperAccount
from app.services.market_data import get_market_data
from app.services.portfolio import update_position_after_trade, validate_trade
from sqlalchemy import select, update
from typing import Dict, Any, Optional
from uuid import UUID
from loguru import logger


async def execute_paper_trade(
    account_id: str,
    symbol: str,
    action: str,
    quantity: int,
    agent_run_id: str,
    confidence: Optional[float] = None,
    reasoning: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Execute a paper trade (for autonomous mode - no approval needed).

    Args:
        account_id: Account ID ("pilot" for autonomous)
        symbol: Stock symbol
        action: BUY or SELL
        quantity: Number of shares
        agent_run_id: MongoDB trace ID
        confidence: Agent confidence score
        reasoning: Brief reasoning summary

    Returns:
        Trade result dictionary:
        {
            "order_id": "...",
            "symbol": "NVDA",
            "side": "BUY",
            "quantity": 10,
            "filled_price": 140.50,
            "cost": 1405.00,
            "status": "FILLED"
        }
    """
    session_maker = get_session_maker()
    symbol = symbol.upper()
    side = action.upper()

    async with session_maker() as session:
        # Get account
        if account_id == "pilot":
            account = await get_or_create_pilot_account(session)
        else:
            result = await session.execute(
                select(PaperAccount).where(PaperAccount.id == UUID(account_id))
            )
            account = result.scalar_one_or_none()
            if not account:
                raise ValueError(f"Account {account_id} not found")

        # Get current market price
        market_data = await get_market_data(symbol)
        current_price = market_data["current_price"]

        # Validate trade
        validation = await validate_trade(
            account.id, symbol, side, quantity, current_price
        )

        if not validation["valid"]:
            raise ValueError(f"Trade validation failed: {validation['reason']}")

        # Create and fill order
        order = await create_paper_order(
            session,
            account.id,
            symbol,
            side,
            quantity,
            agent_run_id,
            confidence,
            reasoning,
        )

        # Execute trade
        filled_order = await fill_order(session, order.id, current_price)

        # Update cash balance
        if side == "BUY":
            cost = quantity * current_price
            new_balance = float(account.cash_balance) - cost
            await session.execute(
                update(PaperAccount)
                .where(PaperAccount.id == account.id)
                .values(cash_balance=new_balance)
            )
        elif side == "SELL":
            proceeds = quantity * current_price
            new_balance = float(account.cash_balance) + proceeds
            await session.execute(
                update(PaperAccount)
                .where(PaperAccount.id == account.id)
                .values(cash_balance=new_balance)
            )

        await session.commit()

        # Update position
        await update_position_after_trade(
            account.id, symbol, side, quantity, current_price
        )

        result = {
            "order_id": str(filled_order.id),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "filled_price": float(filled_order.filled_price),
            "cost": quantity * float(filled_order.filled_price),
            "status": "FILLED",
        }

        logger.info(
            f"Executed paper trade: {side} {quantity} {symbol} @ ${current_price:.2f}"
        )

        return result


async def propose_trade(
    user_id: str,
    symbol: str,
    action: str,
    quantity: int,
    agent_run_id: str,
    confidence: Optional[float] = None,
    reasoning: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Propose a trade for human approval (copilot mode).

    Args:
        user_id: User ID
        symbol: Stock symbol
        action: BUY or SELL
        quantity: Number of shares
        agent_run_id: MongoDB trace ID
        confidence: Agent confidence score
        reasoning: Brief reasoning summary

    Returns:
        Proposal dictionary with order_id
    """
    session_maker = get_session_maker()
    symbol = symbol.upper()
    side = action.upper()

    async with session_maker() as session:
        # Get or create user account
        account = await get_account_by_user_id(session, user_id)

        if not account:
            # Create new account for user
            from app.config import settings

            account = PaperAccount(
                user_id=user_id,
                cash_balance=settings.PAPER_STARTING_CASH,
                starting_cash=settings.PAPER_STARTING_CASH,
            )
            session.add(account)
            await session.commit()
            await session.refresh(account)
            logger.info(f"Created account for user {user_id}")

        # Get current price for validation
        market_data = await get_market_data(symbol)
        current_price = market_data["current_price"]

        # Validate trade
        validation = await validate_trade(
            account.id, symbol, side, quantity, current_price
        )

        if not validation["valid"]:
            raise ValueError(f"Trade validation failed: {validation['reason']}")

        # Create order in PROPOSED status
        order = await create_paper_order(
            session,
            account.id,
            symbol,
            side,
            quantity,
            agent_run_id,
            confidence,
            reasoning,
        )

        proposal = {
            "order_id": str(order.id),
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "estimated_price": current_price,
            "estimated_cost": quantity * current_price,
            "status": "PROPOSED",
            "confidence": confidence,
            "reasoning": reasoning,
        }

        logger.info(f"Proposed trade for user {user_id}: {side} {quantity} {symbol}")

        return proposal

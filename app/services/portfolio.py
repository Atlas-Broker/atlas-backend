"""Paper portfolio accounting and management."""

from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import (
    get_or_create_pilot_account,
    get_account_by_user_id,
    get_account_positions,
    upsert_position,
    delete_position,
)
from app.services.market_data import get_market_data, get_multiple_quotes
from typing import Dict, Any, Optional
from uuid import UUID
from loguru import logger


async def get_portfolio_state(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get current portfolio state including positions, cash, and equity.

    Args:
        user_id: User ID or None for pilot account

    Returns:
        Portfolio state dictionary:
        {
            "account_id": "...",
            "cash": 95000.00,
            "positions": [...],
            "positions_value": 5000.00,
            "total_equity": 100000.00,
            "starting_cash": 100000.00,
            "return_pct": 0.0
        }
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get account
        if user_id is None or user_id == "pilot":
            account = await get_or_create_pilot_account(session)
        else:
            account = await get_account_by_user_id(session, user_id)
            if not account:
                raise ValueError(f"Account not found for user {user_id}")

        # Get positions
        positions = await get_account_positions(session, account.id)

        # Get current prices for all positions
        if positions:
            symbols = [p.symbol for p in positions]
            quotes = await get_multiple_quotes(symbols)

            positions_list = []
            total_positions_value = 0.0

            for pos in positions:
                quote = quotes.get(pos.symbol, {})
                current_price = quote.get("current_price", 0)

                market_value = current_price * pos.quantity
                unrealized_pnl = (current_price - float(pos.avg_entry_price)) * pos.quantity
                unrealized_pnl_pct = (
                    (current_price - float(pos.avg_entry_price)) / float(pos.avg_entry_price) * 100
                    if pos.avg_entry_price > 0
                    else 0
                )

                positions_list.append(
                    {
                        "symbol": pos.symbol,
                        "quantity": pos.quantity,
                        "avg_entry_price": float(pos.avg_entry_price),
                        "current_price": current_price,
                        "market_value": market_value,
                        "unrealized_pnl": unrealized_pnl,
                        "unrealized_pnl_pct": unrealized_pnl_pct,
                    }
                )

                total_positions_value += market_value
        else:
            positions_list = []
            total_positions_value = 0.0

        cash = float(account.cash_balance)
        total_equity = cash + total_positions_value
        starting_cash = float(account.starting_cash)
        return_pct = ((total_equity - starting_cash) / starting_cash * 100) if starting_cash > 0 else 0

        portfolio = {
            "account_id": str(account.id),
            "cash": cash,
            "positions": positions_list,
            "positions_value": total_positions_value,
            "total_equity": total_equity,
            "starting_cash": starting_cash,
            "return_pct": return_pct,
        }

        logger.info(
            f"Portfolio state for {user_id or 'pilot'}: "
            f"Equity=${total_equity:.2f}, Return={return_pct:.2f}%"
        )

        return portfolio


async def update_position_after_trade(
    account_id: UUID,
    symbol: str,
    side: str,
    quantity: int,
    price: float,
):
    """
    Update position after a trade execution.

    Args:
        account_id: Account UUID
        symbol: Stock symbol
        side: BUY or SELL
        quantity: Number of shares
        price: Execution price
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get current position
        positions = await get_account_positions(session, account_id)
        current_pos = next((p for p in positions if p.symbol == symbol), None)

        if side == "BUY":
            if current_pos:
                # Add to existing position (average entry price)
                new_quantity = current_pos.quantity + quantity
                new_avg_price = (
                    (current_pos.quantity * float(current_pos.avg_entry_price) + quantity * price)
                    / new_quantity
                )
                await upsert_position(session, account_id, symbol, new_quantity, new_avg_price)
                logger.info(
                    f"Updated position {symbol}: {new_quantity} shares @ ${new_avg_price:.2f}"
                )
            else:
                # Create new position
                await upsert_position(session, account_id, symbol, quantity, price)
                logger.info(f"Created position {symbol}: {quantity} shares @ ${price:.2f}")

        elif side == "SELL":
            if not current_pos:
                raise ValueError(f"Cannot sell {symbol}: no position exists")

            if current_pos.quantity < quantity:
                raise ValueError(
                    f"Cannot sell {quantity} shares of {symbol}: only {current_pos.quantity} available"
                )

            new_quantity = current_pos.quantity - quantity

            if new_quantity == 0:
                # Close position
                await delete_position(session, account_id, symbol)
                logger.info(f"Closed position {symbol}")
            else:
                # Reduce position
                await upsert_position(
                    session,
                    account_id,
                    symbol,
                    new_quantity,
                    float(current_pos.avg_entry_price),
                )
                logger.info(f"Reduced position {symbol}: {new_quantity} shares remaining")


async def validate_trade(
    account_id: UUID,
    symbol: str,
    side: str,
    quantity: int,
    price: float,
) -> Dict[str, Any]:
    """
    Validate if a trade can be executed.

    Args:
        account_id: Account UUID
        symbol: Stock symbol
        side: BUY or SELL
        quantity: Number of shares
        price: Estimated execution price

    Returns:
        Validation result:
        {
            "valid": true/false,
            "reason": "...",
            "buying_power": ...,
            "cost": ...
        }
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        # Get account
        from app.db.supabase.models import PaperAccount
        from sqlalchemy import select

        result = await session.execute(
            select(PaperAccount).where(PaperAccount.id == account_id)
        )
        account = result.scalar_one_or_none()

        if not account:
            return {"valid": False, "reason": "Account not found"}

        if side == "BUY":
            cost = quantity * price
            cash = float(account.cash_balance)

            if cost > cash:
                return {
                    "valid": False,
                    "reason": f"Insufficient funds: ${cash:.2f} available, ${cost:.2f} needed",
                    "buying_power": cash,
                    "cost": cost,
                }

            return {"valid": True, "buying_power": cash, "cost": cost}

        elif side == "SELL":
            # Check position
            positions = await get_account_positions(session, account_id)
            position = next((p for p in positions if p.symbol == symbol), None)

            if not position:
                return {"valid": False, "reason": f"No position in {symbol}"}

            if position.quantity < quantity:
                return {
                    "valid": False,
                    "reason": f"Insufficient shares: {position.quantity} available, {quantity} needed",
                }

            return {"valid": True, "position_size": position.quantity}

        return {"valid": False, "reason": "Invalid side"}

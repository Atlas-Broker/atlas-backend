"""Post-trade reflection and analysis."""

from typing import Dict, Any, List
from loguru import logger


async def generate_reflection(
    old_portfolio: Dict[str, Any],
    new_portfolio: Dict[str, Any],
    decisions: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Generate reflection on autonomous trading run.

    Args:
        old_portfolio: Portfolio state before trades
        new_portfolio: Portfolio state after trades
        decisions: List of trading decisions made

    Returns:
        Reflection dictionary:
        {
            "portfolio_change": {...},
            "trades_executed": int,
            "total_pnl": float,
            "lessons_learned": [...],
            "performance_notes": "..."
        }
    """
    # Calculate changes
    equity_change = new_portfolio["total_equity"] - old_portfolio["total_equity"]
    equity_change_pct = (
        (equity_change / old_portfolio["total_equity"] * 100)
        if old_portfolio["total_equity"] > 0
        else 0
    )

    # Count executed trades
    trades_executed = sum(
        1 for d in decisions if d.get("action") in ["BUY", "SELL"] and d.get("trade_result")
    )

    # Analyze decisions
    lessons = []

    if trades_executed == 0:
        lessons.append("No trades executed - market conditions may not have met criteria")

    if equity_change > 0:
        lessons.append(f"Positive return: +${equity_change:.2f} ({equity_change_pct:.2f}%)")
    elif equity_change < 0:
        lessons.append(f"Negative return: ${equity_change:.2f} ({equity_change_pct:.2f}%)")

    # Analyze position changes
    old_symbols = {p["symbol"] for p in old_portfolio["positions"]}
    new_symbols = {p["symbol"] for p in new_portfolio["positions"]}

    entered = new_symbols - old_symbols
    exited = old_symbols - new_symbols

    if entered:
        lessons.append(f"Entered new positions: {', '.join(entered)}")

    if exited:
        lessons.append(f"Exited positions: {', '.join(exited)}")

    # Generate performance notes
    performance_notes = (
        f"Executed {trades_executed} trades. "
        f"Portfolio equity changed from ${old_portfolio['total_equity']:.2f} "
        f"to ${new_portfolio['total_equity']:.2f} ({equity_change_pct:+.2f}%). "
        f"Current return: {new_portfolio['return_pct']:.2f}%."
    )

    reflection = {
        "portfolio_change": {
            "old_equity": old_portfolio["total_equity"],
            "new_equity": new_portfolio["total_equity"],
            "change": equity_change,
            "change_pct": equity_change_pct,
        },
        "trades_executed": trades_executed,
        "total_pnl": equity_change,
        "lessons_learned": lessons,
        "performance_notes": performance_notes,
    }

    logger.info(f"Generated reflection: {trades_executed} trades, ${equity_change:+.2f}")

    return reflection

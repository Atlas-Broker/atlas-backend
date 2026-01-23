"""Custom validators for inputs."""

import re
from typing import Optional


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate stock ticker symbol format.

    Args:
        symbol: Stock ticker (e.g., 'NVDA', 'TSLA')

    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False

    # Basic validation: 1-5 uppercase letters
    pattern = r"^[A-Z]{1,5}$"
    return bool(re.match(pattern, symbol.upper()))


def sanitize_symbol(symbol: str) -> str:
    """
    Sanitize and normalize stock symbol.

    Args:
        symbol: Raw symbol input

    Returns:
        Uppercase, stripped symbol

    Raises:
        ValueError: If symbol is invalid
    """
    cleaned = symbol.strip().upper()

    if not validate_stock_symbol(cleaned):
        raise ValueError(f"Invalid stock symbol: {symbol}")

    return cleaned


def validate_quantity(quantity: int, max_value: Optional[int] = None) -> bool:
    """
    Validate trade quantity.

    Args:
        quantity: Number of shares
        max_value: Optional maximum quantity

    Returns:
        True if valid, False otherwise
    """
    if quantity <= 0:
        return False

    if max_value and quantity > max_value:
        return False

    return True

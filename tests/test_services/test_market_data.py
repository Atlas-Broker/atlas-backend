"""Tests for market data service."""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.market_data import get_market_data


@pytest.mark.asyncio
@patch("app.services.market_data._fetch_yahoo_data")
async def test_get_market_data(mock_fetch):
    """Test fetching market data."""
    mock_fetch.return_value = {
        "symbol": "NVDA",
        "current_price": 140.50,
        "change_percent": 2.34,
        "volume": 45000000,
        "cached": False,
    }
    
    data = await get_market_data("NVDA")
    
    assert data["symbol"] == "NVDA"
    assert data["current_price"] == 140.50
    assert "volume" in data

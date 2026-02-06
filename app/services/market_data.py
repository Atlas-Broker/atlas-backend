"""Market data fetching with Yahoo Finance and caching."""

import yfinance as yf
from app.db.mongodb.queries import get_cached_market_data, save_market_data_snapshot
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger
import asyncio


async def get_market_data(
    symbol: str, max_age_minutes: int = 15
) -> Dict[str, Any]:
    """
    Fetch current market data for a symbol with caching.

    Args:
        symbol: Stock ticker symbol
        max_age_minutes: Maximum age of cached data in minutes

    Returns:
        Dictionary with market data:
        {
            "symbol": "NVDA",
            "current_price": 140.50,
            "change_percent": 2.34,
            "volume": 45000000,
            "timestamp": "2025-01-22T10:30:00Z",
            "cached": true/false
        }
    """
    symbol = symbol.upper()

    # Check cache first
    cached = await get_cached_market_data(symbol, max_age_minutes)
    if cached:
        logger.debug(f"Using cached data for {symbol}")
        return {**cached["processed"], "cached": True}

    # Fetch from Yahoo Finance (blocking, so run in executor)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, _fetch_yahoo_data, symbol)

    return data


def _fetch_yahoo_data(symbol: str) -> Dict[str, Any]:
    """
    Fetch data from Yahoo Finance (sync function for executor).

    Args:
        symbol: Stock ticker

    Returns:
        Processed market data dictionary
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")

        if hist.empty:
            raise ValueError(f"No historical data found for {symbol}")

        # Get current price
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        if not current_price:
            current_price = float(hist["Close"].iloc[-1])

        # Get change percent
        change_percent = info.get("regularMarketChangePercent", 0)

        # Get volume
        volume = int(hist["Volume"].iloc[-1])

        # Build processed data
        processed = {
            "symbol": symbol,
            "current_price": float(current_price),
            "change_percent": float(change_percent),
            "volume": volume,
            "timestamp": datetime.utcnow().isoformat(),
            "cached": False,
        }

        # Save to MongoDB cache with raw data
        asyncio.create_task(
            save_market_data_snapshot(
                {
                    "symbol": symbol,
                    "timestamp": datetime.utcnow(),
                    "source": "yahoo_finance",
                    "data": {
                        "info": info,
                        "history": hist.to_dict(),
                    },
                    "processed": processed,
                    "expires_at": datetime.utcnow() + timedelta(minutes=15),
                }
            )
        )

        logger.info(f"Fetched market data for {symbol}: ${current_price}")
        return processed

    except Exception as e:
        logger.error(f"Failed to fetch market data for {symbol}: {e}")
        raise ValueError(f"Failed to fetch market data for {symbol}: {str(e)}")


async def get_historical_data(
    symbol: str, period: str = "1mo", interval: str = "1d"
) -> Dict[str, Any]:
    """
    Fetch historical price data.

    Args:
        symbol: Stock ticker
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)

    Returns:
        Dictionary with OHLCV data
    """
    symbol = symbol.upper()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, _fetch_historical_data, symbol, period, interval
    )


def _fetch_historical_data(symbol: str, period: str, interval: str) -> Dict[str, Any]:
    """Fetch historical data (sync function for executor)."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)

        if hist.empty:
            raise ValueError(f"No historical data found for {symbol}")

        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data": hist.to_dict(),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to fetch historical data for {symbol}: {e}")
        raise ValueError(f"Failed to fetch historical data for {symbol}: {str(e)}")


async def get_multiple_quotes(symbols: list[str]) -> Dict[str, Any]:
    """
    Fetch current quotes for multiple symbols.

    Args:
        symbols: List of stock tickers

    Returns:
        Dictionary mapping symbols to market data
    """
    results = {}

    # Fetch all symbols concurrently
    tasks = [get_market_data(symbol) for symbol in symbols]
    data_list = await asyncio.gather(*tasks, return_exceptions=True)

    for symbol, data in zip(symbols, data_list):
        if isinstance(data, Exception):
            logger.error(f"Failed to fetch {symbol}: {data}")
            results[symbol] = {"error": str(data)}
        else:
            results[symbol] = data

    return results


async def get_stock_price(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get current stock price (simple wrapper).

    Args:
        symbol: Stock ticker

    Returns:
        Dictionary with price data or None if failed
    """
    try:
        data = await get_market_data(symbol)
        return {
            "symbol": symbol,
            "price": data["current_price"],
            "change_percent": data.get("change_percent", 0),
            "timestamp": data["timestamp"],
        }
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        return None

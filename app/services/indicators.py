"""Technical indicators using ta library."""

import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from typing import Dict, Any, Optional
from loguru import logger
import asyncio


async def analyze_technicals(
    symbol: str, period: str = "1mo"
) -> Dict[str, Any]:
    """
    Compute technical indicators for a symbol.

    Args:
        symbol: Stock ticker
        period: Time period for analysis

    Returns:
        Dictionary with technical indicators:
        {
            "rsi": float,
            "macd": {...},
            "moving_averages": {...},
            "trend": "BULLISH" | "BEARISH" | "NEUTRAL",
            "signals": [...]
        }
    """
    symbol = symbol.upper()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _compute_technicals, symbol, period)


def _compute_technicals(symbol: str, period: str) -> Dict[str, Any]:
    """Compute technical indicators (sync function for executor)."""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty or len(hist) < 30:
            raise ValueError(f"Insufficient data for {symbol}")

        df = hist.copy()

        # RSI (14-period)
        rsi_indicator = RSIIndicator(close=df["Close"], window=14)
        rsi = rsi_indicator.rsi()
        current_rsi = float(rsi.iloc[-1]) if not rsi.empty else None

        # MACD
        macd_indicator = MACD(close=df["Close"])
        macd_line = float(macd_indicator.macd().iloc[-1])
        signal_line = float(macd_indicator.macd_signal().iloc[-1])
        histogram = float(macd_indicator.macd_diff().iloc[-1])

        # Moving Averages
        sma_20_indicator = SMAIndicator(close=df["Close"], window=20)
        sma_20 = sma_20_indicator.sma_indicator()
        sma_50_indicator = SMAIndicator(close=df["Close"], window=50)
        sma_50 = sma_50_indicator.sma_indicator()

        current_price = float(df["Close"].iloc[-1])
        sma_20_val = float(sma_20.iloc[-1]) if not sma_20.empty else None
        sma_50_val = float(sma_50.iloc[-1]) if len(sma_50) > 0 else None

        # Determine trend
        trend = "NEUTRAL"
        if sma_20_val and sma_50_val:
            if sma_20_val > sma_50_val and current_price > sma_20_val:
                trend = "BULLISH"
            elif sma_20_val < sma_50_val and current_price < sma_20_val:
                trend = "BEARISH"

        # Generate signals
        signals = []

        if current_rsi:
            if current_rsi > 70:
                signals.append("RSI overbought (>70)")
            elif current_rsi < 30:
                signals.append("RSI oversold (<30)")

        if macd_line and signal_line:
            if macd_line > signal_line:
                signals.append("MACD bullish crossover")
            else:
                signals.append("MACD bearish crossover")

        if sma_20_val and current_price > sma_20_val:
            signals.append("Price above 20-day SMA")
        elif sma_20_val and current_price < sma_20_val:
            signals.append("Price below 20-day SMA")

        result = {
            "symbol": symbol,
            "current_price": current_price,
            "rsi": current_rsi,
            "macd": {
                "macd_line": macd_line,
                "signal_line": signal_line,
                "histogram": histogram,
            },
            "moving_averages": {
                "sma_20": sma_20_val,
                "sma_50": sma_50_val,
            },
            "trend": trend,
            "signals": signals,
        }

        logger.info(f"Computed technicals for {symbol}: {trend}, RSI={current_rsi:.1f}")
        return result

    except Exception as e:
        logger.error(f"Failed to compute technicals for {symbol}: {e}")
        raise ValueError(f"Failed to compute technicals for {symbol}: {str(e)}")


async def check_sentiment(symbol: str) -> Dict[str, Any]:
    """
    Check news sentiment for a symbol.

    Note: This is a placeholder implementation.
    Real implementation would use news APIs or sentiment analysis.

    Args:
        symbol: Stock ticker

    Returns:
        Sentiment dictionary
    """
    # Placeholder - future enhancement
    logger.info(f"Sentiment check for {symbol} (placeholder)")

    return {
        "symbol": symbol,
        "sentiment": "NEUTRAL",
        "score": 0.0,
        "news_count": 0,
        "sources": [],
        "note": "Sentiment analysis not yet implemented",
    }

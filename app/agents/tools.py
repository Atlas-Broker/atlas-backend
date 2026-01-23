"""Tool definitions and execution for agents."""

from app.services.market_data import get_market_data
from app.services.indicators import analyze_technicals, check_sentiment
from typing import Dict, Any, List
from loguru import logger


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Return Gemini function calling tool definitions.

    Returns:
        List of tool definition dictionaries
    """
    return [
        {
            "name": "get_market_data",
            "description": "Fetch current market data for a stock symbol including price, volume, and change percentage. Use this to get real-time market information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., 'NVDA', 'TSLA', 'AAPL')",
                    }
                },
                "required": ["symbol"],
            },
        },
        {
            "name": "analyze_technicals",
            "description": "Compute technical indicators (RSI, MACD, Moving Averages) and identify trend direction for a symbol. Returns detailed technical analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "enum": ["1d", "5d", "1mo", "3mo"],
                    },
                },
                "required": ["symbol"],
            },
        },
        {
            "name": "check_sentiment",
            "description": "Check news sentiment for a symbol (basic implementation). Use this to gauge market sentiment.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock ticker symbol",
                    }
                },
                "required": ["symbol"],
            },
        },
    ]


async def execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool and return results.

    Args:
        tool_name: Name of tool to execute
        params: Tool parameters

    Returns:
        Tool execution result dictionary

    Raises:
        ValueError: If tool name is unknown
    """
    logger.info(f"Executing tool: {tool_name} with params: {params}")

    try:
        if tool_name == "get_market_data":
            result = await get_market_data(params["symbol"])
            return {
                **result,
                "summary": f"{result['symbol']}: ${result['current_price']:.2f} ({result['change_percent']:+.2f}%)",
            }

        elif tool_name == "analyze_technicals":
            period = params.get("period", "1mo")
            result = await analyze_technicals(params["symbol"], period)
            return {
                **result,
                "summary": f"{result['symbol']} - {result['trend']}, RSI: {result['rsi']:.1f}",
            }

        elif tool_name == "check_sentiment":
            result = await check_sentiment(params["symbol"])
            return {
                **result,
                "summary": f"{result['symbol']} sentiment: {result['sentiment']}",
            }

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    except Exception as e:
        logger.error(f"Tool execution failed: {tool_name} - {e}")
        return {
            "error": str(e),
            "summary": f"Tool execution failed: {str(e)}",
        }


def format_tool_result_for_model(tool_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format tool result for sending back to the model.

    Removes large/verbose data, keeps essential information.

    Args:
        tool_name: Name of tool
        result: Raw tool result

    Returns:
        Formatted result for model consumption
    """
    # Create clean result without excessive data
    if "error" in result:
        return {"error": result["error"]}

    if tool_name == "get_market_data":
        return {
            "symbol": result.get("symbol"),
            "current_price": result.get("current_price"),
            "change_percent": result.get("change_percent"),
            "volume": result.get("volume"),
        }

    elif tool_name == "analyze_technicals":
        return {
            "symbol": result.get("symbol"),
            "current_price": result.get("current_price"),
            "rsi": result.get("rsi"),
            "macd": result.get("macd"),
            "moving_averages": result.get("moving_averages"),
            "trend": result.get("trend"),
            "signals": result.get("signals"),
        }

    elif tool_name == "check_sentiment":
        return {
            "symbol": result.get("symbol"),
            "sentiment": result.get("sentiment"),
            "score": result.get("score"),
        }

    return result

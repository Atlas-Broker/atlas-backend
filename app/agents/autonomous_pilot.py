"""Autonomous paper trading pilot - PPAR loop (Perceive, Plan, Act, Reflect)."""

import google.generativeai as genai
from app.agents.tools import get_tool_definitions, execute_tool, format_tool_result_for_model
from app.agents.prompts import AUTONOMOUS_PILOT_PROMPT
from app.services.portfolio import get_portfolio_state
from app.services.order_execution import execute_paper_trade
from app.services.reflection import generate_reflection
from app.db.mongodb.queries import save_agent_run
from app.db.supabase.client import get_session_maker
from app.db.supabase.queries import save_equity_snapshot
from app.config import settings
import uuid
from datetime import datetime
from loguru import logger
from typing import Dict, Any, List


# Configure Gemini
genai.configure(api_key=settings.GOOGLE_AI_API_KEY)


async def run_autonomous_pilot() -> Dict[str, Any]:
    """
    Run autonomous paper trading pilot loop.

    Implements PPAR (Perceive → Plan → Act → Reflect):
    1. Perceive: Load portfolio state, fetch market data
    2. Plan: Agent analyzes each symbol and decides (buy/sell/hold)
    3. Act: Execute paper trades automatically
    4. Reflect: Compute outcomes, generate lessons learned

    Returns:
        Trace dictionary with run results
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    trace = {
        "run_id": run_id,
        "user_id": "AUTONOMOUS_PILOT",
        "timestamp": start_time,
        "input": "Autonomous pilot scheduled run",
        "mode": "autonomous",
        "tools_called": [],
        "reasoning": {},
        "decisions": [],
        "status": "RUNNING",
    }

    logger.info(f"Starting autonomous pilot run: {run_id}")

    try:
        # 1. PERCEIVE
        logger.info("PERCEIVE: Loading portfolio state and market data")

        portfolio = await get_portfolio_state("pilot")

        # Watchlist (TODO: Make configurable)
        watchlist = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL"]

        # 2. PLAN
        logger.info(f"PLAN: Analyzing {len(watchlist)} symbols")

        decisions = []

        for symbol in watchlist:
            decision = await analyze_symbol_for_autonomous(
                symbol=symbol,
                portfolio=portfolio,
                run_id=run_id,
                trace=trace,
            )
            decisions.append(decision)
            trace["decisions"].append(decision)

        # 3. ACT
        logger.info("ACT: Executing trades")

        for decision in decisions:
            if decision["action"] in ["BUY", "SELL"] and decision.get("quantity"):
                try:
                    trade_result = await execute_paper_trade(
                        account_id="pilot",
                        symbol=decision["symbol"],
                        action=decision["action"],
                        quantity=decision["quantity"],
                        agent_run_id=run_id,
                        confidence=decision.get("confidence"),
                        reasoning=decision.get("reasoning"),
                    )
                    decision["trade_result"] = trade_result
                    logger.info(
                        f"Executed: {decision['action']} {decision['quantity']} {decision['symbol']}"
                    )
                except Exception as e:
                    logger.error(f"Trade execution failed: {e}")
                    decision["trade_error"] = str(e)

        # 4. REFLECT
        logger.info("REFLECT: Analyzing outcomes")

        new_portfolio = await get_portfolio_state("pilot")

        reflection = await generate_reflection(
            old_portfolio=portfolio,
            new_portfolio=new_portfolio,
            decisions=decisions,
        )

        trace["reflection"] = reflection

        # Save equity snapshot
        session_maker = get_session_maker()
        async with session_maker() as session:
            await save_equity_snapshot(
                session,
                {
                    "account_id": uuid.UUID(new_portfolio["account_id"]),
                    "equity": new_portfolio["total_equity"],
                    "cash": new_portfolio["cash"],
                    "positions_value": new_portfolio["positions_value"],
                    "timestamp": datetime.utcnow(),
                },
            )

        trace["status"] = "COMPLETE"
        trace["ended_at"] = datetime.utcnow().isoformat()
        trace["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        logger.info(
            f"Pilot run complete: {reflection['trades_executed']} trades, "
            f"${reflection['total_pnl']:+.2f} P&L"
        )

    except Exception as e:
        logger.error(f"Pilot run error: {e}", exc_info=True)
        trace["status"] = "ERROR"
        trace["error"] = str(e)
        raise

    finally:
        # Always save trace
        await save_agent_run(trace)

    return trace


async def analyze_symbol_for_autonomous(
    symbol: str,
    portfolio: Dict[str, Any],
    run_id: str,
    trace: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze a single symbol and make trading decision.

    Args:
        symbol: Stock ticker
        portfolio: Current portfolio state
        run_id: Pilot run ID
        trace: Trace dictionary to append tool calls

    Returns:
        Decision dictionary:
        {
            "symbol": "NVDA",
            "action": "BUY" | "SELL" | "HOLD",
            "quantity": 10,
            "reasoning": "...",
            "confidence": 0.75
        }
    """
    try:
        # Initialize model
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            tools=get_tool_definitions(),
            system_instruction=AUTONOMOUS_PILOT_PROMPT,
        )

        # Build context
        existing_position = next(
            (p for p in portfolio["positions"] if p["symbol"] == symbol), None
        )

        context = f"""Analyze {symbol} for trading decision.

Current Portfolio:
- Cash: ${portfolio['cash']:.2f}
- Total Equity: ${portfolio['total_equity']:.2f}
- Positions: {len(portfolio['positions'])}/{settings.PAPER_MAX_POSITIONS}

{symbol} Position: {'YES - ' + str(existing_position['quantity']) + ' shares @ $' + str(existing_position['avg_entry_price']) if existing_position else 'NO'}

Maximum position size: ${settings.PAPER_MAX_POSITION_SIZE}

Analyze the symbol and decide: BUY, SELL, or HOLD. Be decisive but conservative."""

        chat = model.start_chat()
        response = chat.send_message(context)

        accumulated_text = ""

        # Process response (handle tool calls)
        while True:
            accumulated_text += response.text if response.text else ""

            # Check for function calls
            if response.parts:
                tool_called = False
                for part in response.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        tool_called = True

                        # Execute tool
                        tool_result = await execute_tool(fc.name, dict(fc.args))

                        # Record in trace
                        trace["tools_called"].append(
                            {
                                "tool": fc.name,
                                "symbol": dict(fc.args).get("symbol"),
                                "params": dict(fc.args),
                                "result": tool_result,
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )

                        # Send result back
                        formatted_result = format_tool_result_for_model(fc.name, tool_result)
                        response = chat.send_message(
                            {
                                "function_response": {
                                    "name": fc.name,
                                    "response": formatted_result,
                                }
                            }
                        )
                        break

                if not tool_called:
                    break
            else:
                break

        # Parse decision from text
        decision = parse_autonomous_decision(symbol, accumulated_text, existing_position)

        logger.info(f"{symbol}: {decision['action']} - {decision['reasoning'][:100]}")

        return decision

    except Exception as e:
        logger.error(f"Analysis failed for {symbol}: {e}")
        return {
            "symbol": symbol,
            "action": "HOLD",
            "reasoning": f"Analysis error: {str(e)}",
            "confidence": 0.0,
        }


def parse_autonomous_decision(
    symbol: str, text: str, existing_position: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Parse trading decision from agent text.

    Args:
        symbol: Stock ticker
        text: Agent's analysis text
        existing_position: Current position if exists

    Returns:
        Decision dictionary
    """
    import re

    text_upper = text.upper()

    # Determine action
    if "HOLD" in text_upper or "WAIT" in text_upper:
        action = "HOLD"
    elif existing_position and ("SELL" in text_upper or "EXIT" in text_upper):
        action = "SELL"
    elif not existing_position and "BUY" in text_upper:
        action = "BUY"
    else:
        action = "HOLD"

    # Extract confidence
    confidence = 0.5
    conf_match = re.search(r"confidence[:\s]+([0-9.]+)", text, re.IGNORECASE)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
            if confidence > 1:
                confidence = confidence / 100
        except:
            pass

    # Determine quantity
    quantity = None
    if action == "BUY":
        # Calculate quantity based on position size limit
        qty_match = re.search(r"quantity[:\s]+(\d+)", text, re.IGNORECASE)
        if qty_match:
            quantity = int(qty_match.group(1))
        else:
            # Default to $5000 position
            quantity = 10

    elif action == "SELL" and existing_position:
        # Sell entire position by default
        quantity = existing_position["quantity"]

    # Extract reasoning (first 200 chars)
    reasoning = text[:200].replace("\n", " ").strip()

    return {
        "symbol": symbol,
        "action": action,
        "quantity": quantity,
        "reasoning": reasoning,
        "confidence": confidence,
    }

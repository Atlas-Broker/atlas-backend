"""Streaming agent orchestrator with Gemini."""

import google.generativeai as genai
from app.agents.tools import get_tool_definitions, execute_tool, format_tool_result_for_model
from app.agents.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from app.db.mongodb.queries import save_agent_run, update_agent_run
from app.config import settings
from app.services.order_execution import propose_trade
from typing import Dict, Any, AsyncGenerator
import uuid
from datetime import datetime
from loguru import logger
import json
import re


# Configure Gemini
genai.configure(api_key=settings.GOOGLE_AI_API_KEY)


async def run_orchestrator_streaming(
    user_id: str, intent: str
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Run orchestrator agent with streaming updates.

    This is the CORE streaming implementation - sends real-time events
    as the agent thinks, calls tools, and makes decisions.

    Args:
        user_id: User ID making the request
        intent: User's trading intent/question

    Yields:
        Event dictionaries with 'type' and 'data' keys:
        - type: 'status', data: { status: 'ANALYZING' }
        - type: 'thinking', data: { thought: '...' }
        - type: 'tool_call', data: { tool: 'get_market_data', params: {...} }
        - type: 'tool_result', data: { tool: '...', summary: '...' }
        - type: 'proposal', data: { action: 'BUY', symbol: '...', ... }
        - type: 'complete', data: { trace_id: '...', order_id: '...' }
        - type: 'error', data: { error: '...' }
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    # Initialize trace
    trace = {
        "run_id": run_id,
        "user_id": user_id,
        "timestamp": start_time,
        "input": intent,
        "mode": "copilot",
        "tools_called": [],
        "reasoning": {},
        "proposal": None,
        "status": "ANALYZING",
    }

    yield {"type": "status", "data": {"status": "ANALYZING", "run_id": run_id}}

    try:
        # Initialize Gemini model with tools
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            tools=get_tool_definitions(),
            system_instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        )

        # Start chat session
        chat = model.start_chat()

        # Send initial message with streaming
        response = chat.send_message(intent, stream=True)

        accumulated_text = ""
        tool_calls_made = []

        # Process streaming chunks
        for chunk in response:
            # Handle text (thinking)
            if chunk.text:
                accumulated_text += chunk.text
                yield {"type": "thinking", "data": {"thought": chunk.text}}

            # Handle function calls (tool execution)
            if chunk.parts:
                for part in chunk.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call

                        yield {
                            "type": "tool_call",
                            "data": {"tool": fc.name, "params": dict(fc.args)},
                        }

                        # Execute tool
                        tool_start = datetime.utcnow()
                        tool_result = await execute_tool(fc.name, dict(fc.args))
                        tool_duration = (datetime.utcnow() - tool_start).total_seconds() * 1000

                        # Store in trace
                        tool_call_record = {
                            "tool": fc.name,
                            "symbol": dict(fc.args).get("symbol"),
                            "params": dict(fc.args),
                            "result": tool_result,
                            "timestamp": datetime.utcnow().isoformat(),
                            "cache_hit": tool_result.get("cached", False),
                            "duration_ms": int(tool_duration),
                        }
                        trace["tools_called"].append(tool_call_record)
                        tool_calls_made.append((fc.name, tool_result))

                        yield {
                            "type": "tool_result",
                            "data": {
                                "tool": fc.name,
                                "summary": tool_result.get("summary", "Executed"),
                            },
                        }

                        # Send result back to model
                        formatted_result = format_tool_result_for_model(fc.name, tool_result)
                        response = chat.send_message(
                            {
                                "function_response": {
                                    "name": fc.name,
                                    "response": formatted_result,
                                }
                            },
                            stream=True,
                        )

                        # Continue processing new chunks
                        for new_chunk in response:
                            if new_chunk.text:
                                accumulated_text += new_chunk.text
                                yield {"type": "thinking", "data": {"thought": new_chunk.text}}

        # Store reasoning
        trace["reasoning"]["raw_thoughts"] = accumulated_text

        # Parse final proposal from accumulated text
        yield {"type": "status", "data": {"status": "PROPOSING"}}

        proposal = await parse_proposal_from_text(accumulated_text, tool_calls_made)

        if not proposal:
            # Ask model explicitly for recommendation
            response = chat.send_message(
                "Based on your analysis, provide a clear trading recommendation with: Action (BUY/SELL/HOLD), Symbol, Quantity, Entry Price, Stop Loss, Target Price, Confidence (0-1), and Rationale.",
                stream=True,
            )

            recommendation_text = ""
            for chunk in response:
                if chunk.text:
                    recommendation_text += chunk.text
                    yield {"type": "thinking", "data": {"thought": chunk.text}}

            accumulated_text += "\n" + recommendation_text
            proposal = await parse_proposal_from_text(
                accumulated_text + recommendation_text, tool_calls_made
            )

        if not proposal or proposal["action"] == "HOLD":
            # No trade recommended
            trace["proposal"] = proposal or {"action": "HOLD", "reasoning": "No clear setup"}
            trace["status"] = "COMPLETE"
            await save_agent_run(trace)

            yield {
                "type": "proposal",
                "data": proposal or {"action": "HOLD", "reasoning": "No clear trading setup"},
            }
            yield {"type": "complete", "data": {"trace_id": run_id, "order_id": None}}
            return

        # Create proposed order
        try:
            order_proposal = await propose_trade(
                user_id=user_id,
                symbol=proposal["symbol"],
                action=proposal["action"],
                quantity=proposal["quantity"],
                agent_run_id=run_id,
                confidence=proposal.get("confidence", 0.5),
                reasoning=proposal.get("rationale", ""),
            )

            proposal["order_id"] = order_proposal["order_id"]
            proposal["estimated_price"] = order_proposal["estimated_price"]
            proposal["estimated_cost"] = order_proposal["estimated_cost"]

        except Exception as e:
            logger.error(f"Failed to create order proposal: {e}")
            proposal["order_error"] = str(e)

        trace["proposal"] = proposal
        trace["status"] = "COMPLETE"
        trace["ended_at"] = datetime.utcnow().isoformat()
        trace["duration_ms"] = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Save complete trace
        await save_agent_run(trace)

        yield {"type": "proposal", "data": proposal}
        yield {
            "type": "complete",
            "data": {"trace_id": run_id, "order_id": proposal.get("order_id")},
        }

    except Exception as e:
        logger.error(f"Orchestrator error: {e}", exc_info=True)
        trace["status"] = "ERROR"
        trace["error"] = str(e)
        await save_agent_run(trace)

        yield {"type": "error", "data": {"error": str(e)}}


async def parse_proposal_from_text(
    text: str, tool_calls: list
) -> Dict[str, Any]:
    """
    Parse trade proposal from agent's text output.

    Args:
        text: Accumulated agent text
        tool_calls: List of (tool_name, result) tuples

    Returns:
        Proposal dictionary or None
    """
    # Extract symbol from tool calls if available
    symbol = None
    entry_price = None

    for tool_name, result in tool_calls:
        if tool_name == "get_market_data" and not result.get("error"):
            symbol = result.get("symbol")
            entry_price = result.get("current_price")
            break

    # Look for action keywords
    text_upper = text.upper()

    if "HOLD" in text_upper or "WAIT" in text_upper or "NO TRADE" in text_upper:
        return {"action": "HOLD", "reasoning": "Conditions not favorable"}

    action = None
    if "BUY" in text_upper and "DON'T BUY" not in text_upper and "NOT BUY" not in text_upper:
        action = "BUY"
    elif "SELL" in text_upper and "DON'T SELL" not in text_upper:
        action = "SELL"

    if not action or not symbol:
        return None

    # Try to extract numerical values
    confidence = 0.5  # Default

    # Look for confidence
    conf_match = re.search(r"confidence[:\s]+([0-9.]+)", text, re.IGNORECASE)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
            if confidence > 1:
                confidence = confidence / 100  # Convert percentage
        except:
            pass

    # Look for quantity
    quantity = 10  # Default
    qty_match = re.search(r"quantity[:\s]+(\d+)", text, re.IGNORECASE)
    if qty_match:
        quantity = int(qty_match.group(1))

    # Look for stop loss
    stop_loss = None
    stop_match = re.search(r"stop\s*loss[:\s]+\$?([0-9.]+)", text, re.IGNORECASE)
    if stop_match:
        stop_loss = float(stop_match.group(1))

    # Look for target
    target = None
    target_match = re.search(r"target[:\s]+\$?([0-9.]+)", text, re.IGNORECASE)
    if target_match:
        target = float(target_match.group(1))

    # Extract rationale (last paragraph usually)
    rationale_match = re.search(r"rationale[:\s]+(.+?)(?:\n\n|$)", text, re.IGNORECASE | re.DOTALL)
    rationale = rationale_match.group(1).strip() if rationale_match else text[-200:]

    return {
        "action": action,
        "symbol": symbol,
        "quantity": quantity,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "target_price": target,
        "confidence": confidence,
        "rationale": rationale[:500],  # Limit length
    }

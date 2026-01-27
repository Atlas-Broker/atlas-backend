"""Autonomous paper trading pilot - PPAR loop with Multi-Agent System."""

from app.agents.coordinator import MultiAgentCoordinator
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


async def run_autonomous_pilot() -> Dict[str, Any]:
    """
    Run autonomous paper trading pilot with Multi-Agent System.

    Implements PPAR (Perceive → Plan → Act → Reflect):
    1. Perceive: Portfolio Manager loads state
    2. Plan: Market Analyst, Risk Manager, Execution Agent collaborate
    3. Act: Execute approved trades
    4. Reflect: Analyze outcomes and learn

    Uses 4 specialized agents:
    - Market Analyst: Technical analysis and market data
    - Risk Manager: Position sizing and risk evaluation
    - Portfolio Manager: Portfolio state and constraints
    - Execution Agent: Final trading decisions

    Returns:
        Trace dictionary with run results
    """
    run_id = str(uuid.uuid4())
    start_time = datetime.utcnow()

    trace = {
        "run_id": run_id,
        "user_id": "AUTONOMOUS_PILOT",
        "timestamp": start_time,
        "input": "Multi-Agent autonomous pilot run",
        "mode": "autonomous_multi_agent",
        "tools_called": [],
        "reasoning": {},
        "decisions": [],
        "status": "RUNNING",
        "agent_system": "multi_agent_v1",
    }

    logger.info("=" * 80)
    logger.info(f"🚀 AUTONOMOUS PILOT RUN: {run_id}")
    logger.info("=" * 80)

    try:
        # Watchlist (TODO: Make configurable via database)
        watchlist = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"]
        
        logger.info(f"📋 Watchlist: {', '.join(watchlist)}")

        # Initialize Multi-Agent Coordinator
        logger.info("\n🤖 Initializing Multi-Agent System...")
        coordinator = MultiAgentCoordinator(account_id="pilot")

        # PERCEIVE + PLAN: Run multi-agent trading cycle
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: PERCEIVE & PLAN (Multi-Agent Coordination)")
        logger.info("=" * 80 + "\n")
        
        decisions = await coordinator.run_trading_cycle(
            watchlist=watchlist,
            trace=trace,
        )
        
        trace["decisions"] = decisions
        trace["agent_communication_log"] = coordinator.get_communication_log()

        # ACT: Execute approved trades
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: ACT (Trade Execution)")
        logger.info("=" * 80 + "\n")

        trades_executed = 0
        
        for decision in decisions:
            if decision["action"] in ["BUY", "SELL"] and decision.get("quantity"):
                try:
                    logger.info(
                        f"💰 Executing: {decision['action']} {decision['quantity']} "
                        f"{decision['symbol']}"
                    )
                    
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
                    trades_executed += 1
                    
                    logger.info(
                        f"✅ Trade executed: {decision['action']} "
                        f"{decision['quantity']} {decision['symbol']}"
                    )
                except Exception as e:
                    logger.error(f"❌ Trade execution failed: {e}")
                    decision["trade_error"] = str(e)
            else:
                logger.info(
                    f"⏸️  Skipping: {decision['symbol']} - {decision['action']}"
                )

        logger.info(f"\n📊 Trades executed: {trades_executed}")

        # REFLECT: Analyze outcomes
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: REFLECT (Performance Analysis)")
        logger.info("=" * 80 + "\n")

        # Reload portfolio to see changes
        new_portfolio = await coordinator.portfolio_manager.load_portfolio_state()

        # Generate reflection (comparing before/after)
        # Get old portfolio state from the first load
        old_portfolio_context = coordinator.communication_hub.get_message_history(
            agent_name="PortfolioManager", limit=1
        )
        old_portfolio = (
            old_portfolio_context[0].content.get("portfolio_state", new_portfolio)
            if old_portfolio_context
            else new_portfolio
        )
        
        reflection = await generate_reflection(
            old_portfolio=old_portfolio,
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

        logger.info("\n" + "=" * 80)
        logger.info("✅ PILOT RUN COMPLETE")
        logger.info("=" * 80)
        logger.info(f"📈 Trades executed: {reflection['trades_executed']}")
        logger.info(f"💵 P&L: ${reflection['total_pnl']:+.2f}")
        logger.info(f"💰 Total equity: ${new_portfolio['total_equity']:.2f}")
        logger.info(f"⏱️  Duration: {trace['duration_ms']}ms")
        logger.info("=" * 80 + "\n")

    except Exception as e:
        logger.error(f"Pilot run error: {e}", exc_info=True)
        trace["status"] = "ERROR"
        trace["error"] = str(e)
        raise

    finally:
        # Always save trace
        await save_agent_run(trace)

    return trace

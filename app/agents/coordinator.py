"""Multi-Agent Coordinator - Orchestrates all specialized agents."""

from app.agents.agent_communication import AgentCommunicationHub
from app.agents.market_analyst_agent import MarketAnalystAgent
from app.agents.risk_manager_agent import RiskManagerAgent
from app.agents.portfolio_manager_agent import PortfolioManagerAgent
from app.agents.execution_agent import ExecutionAgent
from typing import Dict, Any, List
from loguru import logger
from datetime import datetime
import uuid


class MultiAgentCoordinator:
    """
    Coordinates multiple specialized agents for autonomous trading.
    
    Agent Flow:
    1. Portfolio Manager loads current state
    2. Market Analyst analyzes each symbol
    3. Risk Manager evaluates each trade
    4. Execution Agent makes final decisions
    5. All agents communicate through shared hub
    """
    
    def __init__(self, account_id: str = "pilot"):
        """
        Initialize the multi-agent coordinator.
        
        Args:
            account_id: Trading account ID
        """
        self.account_id = account_id
        
        # Create communication hub
        self.communication_hub = AgentCommunicationHub()
        
        # Initialize specialized agents
        self.portfolio_manager = PortfolioManagerAgent(
            self.communication_hub, account_id
        )
        self.market_analyst = MarketAnalystAgent(self.communication_hub)
        self.risk_manager = RiskManagerAgent(self.communication_hub)
        self.execution_agent = ExecutionAgent(self.communication_hub)
        
        logger.info("🤖 Multi-Agent System initialized with 4 specialized agents")
        
    async def run_trading_cycle(
        self, watchlist: List[str], trace: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Run a complete trading cycle with all agents.
        
        Args:
            watchlist: List of symbols to analyze
            trace: Trace dictionary for logging
            
        Returns:
            List of trading decisions
        """
        run_id = trace.get("run_id", str(uuid.uuid4()))
        
        logger.info(f"🚀 [Coordinator] Starting trading cycle for {len(watchlist)} symbols")
        logger.info(f"📋 Watchlist: {', '.join(watchlist)}")
        
        # Clear previous context
        self.communication_hub.clear()
        
        decisions = []
        
        # Step 1: Load Portfolio State
        logger.info("=" * 60)
        logger.info("STEP 1: Portfolio Manager - Loading current state")
        logger.info("=" * 60)
        
        portfolio_state = await self.portfolio_manager.load_portfolio_state()
        
        # Step 2: Analyze each symbol in the watchlist
        logger.info("=" * 60)
        logger.info(f"STEP 2: Market Analyst - Analyzing {len(watchlist)} symbols")
        logger.info("=" * 60)
        
        for symbol in watchlist:
            logger.info(f"\n{'─' * 60}")
            logger.info(f"Processing: {symbol}")
            logger.info(f"{'─' * 60}\n")
            
            try:
                # Market Analysis
                market_analysis = await self.market_analyst.analyze_symbol(
                    symbol, trace
                )
                
                if "error" in market_analysis:
                    logger.error(f"Market analysis failed for {symbol}")
                    decisions.append({
                        "symbol": symbol,
                        "action": "HOLD",
                        "reasoning": f"Analysis error: {market_analysis['error']}",
                        "confidence": 0.0,
                    })
                    continue
                    
                # Get existing position info
                existing_position = self.portfolio_manager.get_position_info(symbol)
                
                # Determine initial action (BUY if no position, SELL if have position)
                potential_action = "SELL" if existing_position.get("exists", False) else "BUY"
                
                # Risk Evaluation
                logger.info(f"\n{'─' * 60}")
                logger.info(f"STEP 3: Risk Manager - Evaluating {potential_action} {symbol}")
                logger.info(f"{'─' * 60}\n")
                
                risk_evaluation = await self.risk_manager.evaluate_trade(
                    symbol=symbol,
                    action=potential_action,
                    market_analysis=market_analysis,
                    portfolio_state=portfolio_state,
                )
                
                # Portfolio Constraints Check
                logger.info(f"\n{'─' * 60}")
                logger.info(f"STEP 4: Portfolio Manager - Checking constraints")
                logger.info(f"{'─' * 60}\n")
                
                quantity = risk_evaluation.get("recommended_quantity", 10)
                portfolio_constraints = self.portfolio_manager.check_trade_constraints(
                    symbol=symbol,
                    action=potential_action,
                    quantity=quantity,
                )
                
                # Final Decision
                logger.info(f"\n{'─' * 60}")
                logger.info(f"STEP 5: Execution Agent - Making final decision")
                logger.info(f"{'─' * 60}\n")
                
                decision = await self.execution_agent.make_decision(
                    symbol=symbol,
                    market_analysis=market_analysis,
                    risk_evaluation=risk_evaluation,
                    portfolio_constraints=portfolio_constraints,
                    existing_position=existing_position,
                )
                
                # Add symbol to decision
                decision["symbol"] = symbol
                decisions.append(decision)
                
                logger.info(f"\n✅ Decision for {symbol}: {decision['action']}")
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}", exc_info=True)
                decisions.append({
                    "symbol": symbol,
                    "action": "HOLD",
                    "reasoning": f"Processing error: {str(e)}",
                    "confidence": 0.0,
                })
                
        logger.info("=" * 60)
        logger.info(f"Trading cycle complete: {len(decisions)} decisions made")
        logger.info("=" * 60)
        
        # Summary
        buy_count = sum(1 for d in decisions if d["action"] == "BUY")
        sell_count = sum(1 for d in decisions if d["action"] == "SELL")
        hold_count = sum(1 for d in decisions if d["action"] == "HOLD")
        
        logger.info(f"📊 Summary: {buy_count} BUY, {sell_count} SELL, {hold_count} HOLD")
        
        return decisions
        
    def get_communication_log(self) -> List[Dict[str, Any]]:
        """
        Get agent communication log for debugging.
        
        Returns:
            List of messages between agents
        """
        messages = self.communication_hub.get_message_history(limit=50)
        return [
            {
                "from": msg.from_agent,
                "to": msg.to_agent or "ALL",
                "type": msg.message_type.value,
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]

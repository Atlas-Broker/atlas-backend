"""Portfolio Manager Agent - Manages portfolio state and constraints."""

from app.agents.agent_communication import AgentCommunicationHub
from app.services.portfolio import get_portfolio_state
from app.config import settings
from typing import Dict, Any
from loguru import logger
from datetime import datetime


class PortfolioManagerAgent:
    """
    Specialist agent for portfolio management.
    
    Responsibilities:
    - Track current positions and cash
    - Enforce position limits and constraints
    - Monitor portfolio diversification
    - Calculate portfolio-level metrics
    - Provide portfolio context to other agents
    """
    
    def __init__(self, communication_hub: AgentCommunicationHub, account_id: str = "pilot"):
        """
        Initialize Portfolio Manager Agent.
        
        Args:
            communication_hub: Communication hub for inter-agent messaging
            account_id: Trading account ID
        """
        self.name = "PortfolioManager"
        self.communication_hub = communication_hub
        self.communication_hub.register_agent(self.name, self)
        self.account_id = account_id
        self.current_state: Dict[str, Any] = {}
        
    async def load_portfolio_state(self) -> Dict[str, Any]:
        """
        Load current portfolio state from database.
        
        Returns:
            Portfolio state dictionary
        """
        logger.info(f"💼 [PortfolioManager] Loading portfolio state")
        
        try:
            state = await get_portfolio_state(self.account_id)
            self.current_state = state
            
            # Broadcast portfolio state to all agents
            self.communication_hub.broadcast(self.name, {
                "portfolio_state": state,
                "timestamp": datetime.utcnow().isoformat(),
            })
            
            logger.info(
                f"💼 [PortfolioManager] Portfolio loaded: "
                f"${state['total_equity']:.2f} equity, "
                f"{len(state['positions'])} positions"
            )
            
            return state
            
        except Exception as e:
            logger.error(f"Portfolio load error: {e}")
            raise
            
    def check_trade_constraints(
        self, symbol: str, action: str, quantity: int
    ) -> Dict[str, Any]:
        """
        Check if a trade meets portfolio constraints.
        
        Args:
            symbol: Stock ticker
            action: BUY or SELL
            quantity: Number of shares
            
        Returns:
            Constraint check result with allowed/rejected status
        """
        logger.info(
            f"📋 [PortfolioManager] Checking constraints for "
            f"{action} {quantity} {symbol}"
        )
        
        violations = []
        
        # Get current position
        existing_position = next(
            (p for p in self.current_state["positions"] if p["symbol"] == symbol),
            None,
        )
        
        if action == "BUY":
            # Check: Don't already have position (for swing trading)
            if existing_position:
                violations.append(
                    f"Already have position in {symbol} "
                    f"({existing_position['quantity']} shares)"
                )
                
            # Check: Max positions limit
            if len(self.current_state["positions"]) >= settings.PAPER_MAX_POSITIONS:
                violations.append(
                    f"Maximum positions reached "
                    f"({settings.PAPER_MAX_POSITIONS})"
                )
                
            # Check: Sufficient cash (estimate)
            # Note: Real price check happens during execution
            estimated_cost = quantity * 100  # Placeholder
            if self.current_state["cash"] < estimated_cost:
                violations.append(
                    f"Insufficient cash (have: ${self.current_state['cash']:.2f})"
                )
                
        elif action == "SELL":
            # Check: Have position to sell
            if not existing_position:
                violations.append(f"No existing position in {symbol} to sell")
            elif existing_position["quantity"] < quantity:
                violations.append(
                    f"Insufficient shares to sell "
                    f"(have: {existing_position['quantity']}, want: {quantity})"
                )
                
        allowed = len(violations) == 0
        
        result = {
            "allowed": allowed,
            "violations": violations,
            "current_positions": len(self.current_state["positions"]),
            "cash_available": self.current_state["cash"],
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if not allowed:
            logger.warning(
                f"❌ [PortfolioManager] Trade rejected: {', '.join(violations)}"
            )
        else:
            logger.info(f"✅ [PortfolioManager] Trade constraints satisfied")
            
        return result
        
    def get_position_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get information about a specific position.
        
        Args:
            symbol: Stock ticker
            
        Returns:
            Position info or None if no position exists
        """
        position = next(
            (p for p in self.current_state["positions"] if p["symbol"] == symbol),
            None,
        )
        
        return position or {"symbol": symbol, "quantity": 0, "exists": False}
        
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get portfolio summary for decision-making.
        
        Returns:
            Portfolio summary dictionary
        """
        return {
            "total_equity": self.current_state.get("total_equity", 0),
            "cash": self.current_state.get("cash", 0),
            "positions_count": len(self.current_state.get("positions", [])),
            "positions_value": self.current_state.get("positions_value", 0),
            "utilization": (
                self.current_state.get("positions_value", 0)
                / self.current_state.get("total_equity", 1)
                if self.current_state.get("total_equity", 0) > 0
                else 0
            ),
        }

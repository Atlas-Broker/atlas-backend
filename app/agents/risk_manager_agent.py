"""Risk Manager Agent - Evaluates risk and determines position sizing."""

import google.generativeai as genai
from app.agents.agent_communication import AgentCommunicationHub
from app.config import settings
from typing import Dict, Any
from loguru import logger
from datetime import datetime


class RiskManagerAgent:
    """
    Specialist agent for risk management and position sizing.
    
    Responsibilities:
    - Evaluate risk/reward ratios
    - Determine appropriate position sizes
    - Set stop loss and take profit levels
    - Assess portfolio-level risk
    - Reject high-risk trades
    """
    
    def __init__(self, communication_hub: AgentCommunicationHub):
        """
        Initialize Risk Manager Agent.
        
        Args:
            communication_hub: Communication hub for inter-agent messaging
        """
        self.name = "RiskManager"
        self.communication_hub = communication_hub
        self.communication_hub.register_agent(self.name, self)
        
        # Configure Gemini for risk analysis
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=self._get_system_prompt(),
        )
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for risk manager."""
        return """You are a Risk Manager Agent specializing in portfolio risk management.

Your role:
- Evaluate risk/reward for every trade
- Calculate appropriate position sizes
- Set stop losses and profit targets
- Ensure portfolio diversification
- Reject trades that exceed risk tolerance

Risk Management Principles:
- Maximum 2% risk per trade
- Minimum 2:1 reward/risk ratio
- Position size based on volatility
- Never exceed position limits
- Maintain portfolio-level risk < 10%

Be conservative. Preservation of capital is your primary concern."""
        
    async def evaluate_trade(
        self,
        symbol: str,
        action: str,
        market_analysis: Dict[str, Any],
        portfolio_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate trade risk and determine position sizing.
        
        Args:
            symbol: Stock ticker
            action: BUY or SELL
            market_analysis: Analysis from Market Analyst Agent
            portfolio_state: Current portfolio state from Portfolio Manager
            
        Returns:
            Risk evaluation with position size, stop loss, take profit
        """
        logger.info(f"⚖️ [RiskManager] Evaluating {action} {symbol}")
        
        current_price = market_analysis.get("market_data", {}).get("current_price")
        technical_indicators = market_analysis.get("technical_indicators", {})
        
        # Build context for Gemini
        context = f"""Evaluate risk for this trade:

Symbol: {symbol}
Action: {action}
Current Price: ${current_price}

Technical Analysis:
- RSI: {technical_indicators.get('rsi', 'N/A')}
- Trend: {technical_indicators.get('trend', 'N/A')}
- Volatility Signals: {technical_indicators.get('signals', [])}

Portfolio State:
- Cash Available: ${portfolio_state['cash']:.2f}
- Total Equity: ${portfolio_state['total_equity']:.2f}
- Current Positions: {len(portfolio_state['positions'])}/{settings.PAPER_MAX_POSITIONS}
- Max Position Size: ${settings.PAPER_MAX_POSITION_SIZE}

Market Analysis Confidence: {market_analysis.get('confidence', 0.5):.2f}

Provide:
1. Risk Assessment (LOW/MEDIUM/HIGH)
2. Recommended Position Size (in dollars)
3. Stop Loss Price
4. Take Profit Target
5. Risk/Reward Ratio
6. Approval Status (APPROVED/REJECTED)
7. Reasoning

Use conservative position sizing. Reject if risk is too high or setup is unclear."""

        chat = self.model.start_chat()
        response = chat.send_message(context)
        
        evaluation_text = response.text
        
        # Parse the evaluation
        evaluation = self._parse_evaluation(
            evaluation_text, current_price, portfolio_state
        )
        
        # Broadcast risk evaluation
        self.communication_hub.broadcast(self.name, {
            "symbol": symbol,
            "action": action,
            "evaluation": evaluation,
        })
        
        approval = evaluation["approval_status"]
        logger.info(
            f"{'✅' if approval == 'APPROVED' else '❌'} [RiskManager] "
            f"{symbol} {action}: {approval}"
        )
        
        return evaluation
        
    def _parse_evaluation(
        self, text: str, current_price: float, portfolio_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse risk evaluation from Gemini response.
        
        Args:
            text: Response text
            current_price: Current stock price
            portfolio_state: Portfolio state
            
        Returns:
            Parsed evaluation dictionary
        """
        import re
        
        text_upper = text.upper()
        
        # Extract approval status
        if "APPROVED" in text_upper and "REJECTED" not in text_upper:
            approval = "APPROVED"
        else:
            approval = "REJECTED"
            
        # Extract risk level
        if "HIGH RISK" in text_upper or "HIGH" in text_upper:
            risk_level = "HIGH"
        elif "LOW RISK" in text_upper or "LOW" in text_upper:
            risk_level = "LOW"
        else:
            risk_level = "MEDIUM"
            
        # Extract position size (in dollars)
        position_match = re.search(
            r"position size[:\s]+\$?([0-9,]+)", text, re.IGNORECASE
        )
        if position_match:
            position_size = float(position_match.group(1).replace(",", ""))
        else:
            # Default to 5% of portfolio or max position size, whichever is smaller
            position_size = min(
                portfolio_state["total_equity"] * 0.05,
                settings.PAPER_MAX_POSITION_SIZE,
            )
            
        # Calculate quantity
        quantity = int(position_size / current_price) if current_price else 0
        
        # Extract stop loss
        stop_match = re.search(
            r"stop loss[:\s]+\$?([0-9.]+)", text, re.IGNORECASE
        )
        if stop_match:
            stop_loss = float(stop_match.group(1))
        else:
            # Default: 5% below entry
            stop_loss = current_price * 0.95
            
        # Extract take profit
        target_match = re.search(
            r"take profit[:\s]+\$?([0-9.]+)", text, re.IGNORECASE
        )
        if target_match:
            take_profit = float(target_match.group(1))
        else:
            # Default: 10% above entry (2:1 ratio)
            take_profit = current_price * 1.10
            
        # Calculate risk/reward
        risk = current_price - stop_loss
        reward = take_profit - current_price
        risk_reward_ratio = reward / risk if risk > 0 else 0
        
        return {
            "approval_status": approval,
            "risk_level": risk_level,
            "position_size_dollars": position_size,
            "recommended_quantity": quantity,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward_ratio": risk_reward_ratio,
            "reasoning": text[:300],
            "timestamp": datetime.utcnow().isoformat(),
        }

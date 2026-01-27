"""Execution Agent - Makes final trading decisions and executes trades."""

import google.generativeai as genai
from app.agents.agent_communication import AgentCommunicationHub
from app.config import settings
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime


class ExecutionAgent:
    """
    Final decision-maker and trade executor.
    
    Responsibilities:
    - Review all agent inputs
    - Make final BUY/SELL/HOLD decision
    - Consider all factors (market, risk, portfolio)
    - Provide clear reasoning for decisions
    - Coordinate trade execution
    """
    
    def __init__(self, communication_hub: AgentCommunicationHub):
        """
        Initialize Execution Agent.
        
        Args:
            communication_hub: Communication hub for inter-agent messaging
        """
        self.name = "ExecutionAgent"
        self.communication_hub = communication_hub
        self.communication_hub.register_agent(self.name, self)
        
        # Configure Gemini for decision-making
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=self._get_system_prompt(),
        )
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for execution agent."""
        return """You are an Execution Agent - the final decision-maker for trades.

Your role:
- Review inputs from Market Analyst, Risk Manager, and Portfolio Manager
- Synthesize all information into a clear decision
- Make the final call: BUY, SELL, or HOLD
- Provide transparent reasoning

Decision Framework:
1. Market conditions must be favorable (from Market Analyst)
2. Risk must be acceptable (from Risk Manager)
3. Portfolio constraints must be satisfied (from Portfolio Manager)
4. Overall confidence must be sufficient

Be decisive but conservative. When in doubt, choose HOLD.
Every decision must be explainable and justified."""
        
    async def make_decision(
        self,
        symbol: str,
        market_analysis: Dict[str, Any],
        risk_evaluation: Dict[str, Any],
        portfolio_constraints: Dict[str, Any],
        existing_position: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make final trading decision based on all agent inputs.
        
        Args:
            symbol: Stock ticker
            market_analysis: Analysis from Market Analyst Agent
            risk_evaluation: Evaluation from Risk Manager Agent
            portfolio_constraints: Constraints from Portfolio Manager Agent
            existing_position: Existing position info if any
            
        Returns:
            Final decision with action, quantity, and reasoning
        """
        logger.info(f"🎯 [ExecutionAgent] Making decision for {symbol}")
        
        # Build comprehensive context for Gemini
        context = f"""Make final trading decision for {symbol}.

MARKET ANALYST INPUT:
- Analysis Confidence: {market_analysis.get('confidence', 0):.2f}
- Current Price: ${market_analysis.get('market_data', {}).get('current_price', 0)}
- Trend: {market_analysis.get('technical_indicators', {}).get('trend', 'N/A')}
- Technical Signals: {market_analysis.get('technical_indicators', {}).get('signals', [])}
- Analysis Summary: {market_analysis.get('analysis', 'N/A')[:200]}

RISK MANAGER INPUT:
- Approval Status: {risk_evaluation.get('approval_status', 'UNKNOWN')}
- Risk Level: {risk_evaluation.get('risk_level', 'N/A')}
- Recommended Quantity: {risk_evaluation.get('recommended_quantity', 0)} shares
- Stop Loss: ${risk_evaluation.get('stop_loss', 0):.2f}
- Take Profit: ${risk_evaluation.get('take_profit', 0):.2f}
- Risk/Reward Ratio: {risk_evaluation.get('risk_reward_ratio', 0):.2f}:1
- Risk Reasoning: {risk_evaluation.get('reasoning', 'N/A')[:200]}

PORTFOLIO MANAGER INPUT:
- Constraints Satisfied: {'YES' if portfolio_constraints.get('allowed', False) else 'NO'}
- Violations: {portfolio_constraints.get('violations', [])}
- Cash Available: ${portfolio_constraints.get('cash_available', 0):.2f}
- Current Positions: {portfolio_constraints.get('current_positions', 0)}

EXISTING POSITION:
{f"YES - {existing_position['quantity']} shares @ ${existing_position['avg_entry_price']:.2f}" if existing_position and existing_position.get('exists', False) else "NO"}

DECISION REQUIRED:
Based on ALL the above information, make your final decision.

Provide:
1. **Action**: BUY, SELL, or HOLD
2. **Quantity**: Number of shares (if BUY/SELL)
3. **Confidence**: 0.0 to 1.0
4. **Reasoning**: Clear explanation of your decision
5. **Key Factors**: Top 3 factors that influenced your decision

Remember:
- All three agents must agree for BUY
- Be conservative - HOLD is often the right choice
- Consider the full picture, not just one factor"""

        chat = self.model.start_chat()
        response = chat.send_message(context)
        
        decision_text = response.text
        
        # Parse the decision
        decision = self._parse_decision(
            decision_text,
            risk_evaluation,
            existing_position,
        )
        
        # Broadcast final decision
        self.communication_hub.broadcast(self.name, {
            "symbol": symbol,
            "decision": decision,
        })
        
        action = decision["action"]
        logger.info(
            f"{'💰' if action == 'BUY' else '📤' if action == 'SELL' else '⏸️'} "
            f"[ExecutionAgent] {symbol}: {action} "
            f"{'(' + str(decision.get('quantity', 0)) + ' shares)' if action != 'HOLD' else ''}"
        )
        
        return decision
        
    def _parse_decision(
        self,
        text: str,
        risk_evaluation: Dict[str, Any],
        existing_position: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Parse decision from Gemini response.
        
        Args:
            text: Response text
            risk_evaluation: Risk evaluation for defaults
            existing_position: Existing position if any
            
        Returns:
            Parsed decision dictionary
        """
        import re
        
        text_upper = text.upper()
        
        # Determine action
        if "HOLD" in text_upper:
            action = "HOLD"
        elif existing_position and existing_position.get("exists", False):
            # Have position - look for SELL signal
            if "SELL" in text_upper or "EXIT" in text_upper:
                action = "SELL"
            else:
                action = "HOLD"
        else:
            # No position - look for BUY signal
            if "BUY" in text_upper and "DON'T BUY" not in text_upper:
                action = "BUY"
            else:
                action = "HOLD"
                
        # Extract quantity
        quantity = None
        if action == "BUY":
            # Use Risk Manager's recommendation
            quantity = risk_evaluation.get("recommended_quantity", 10)
        elif action == "SELL" and existing_position:
            # Sell entire position
            quantity = existing_position.get("quantity", 0)
            
        # Extract confidence
        conf_match = re.search(
            r"confidence[:\s]+([0-9.]+)", text, re.IGNORECASE
        )
        if conf_match:
            try:
                confidence = float(conf_match.group(1))
                if confidence > 1:
                    confidence = confidence / 100
            except:
                confidence = 0.5
        else:
            confidence = 0.5
            
        # Extract key factors
        factors = []
        if "KEY FACTORS" in text_upper or "FACTORS" in text_upper:
            # Try to extract bullet points or numbered list
            factor_matches = re.findall(
                r"[-•\d.]+\s*([^\n]{10,100})", text[text.upper().find("FACTOR"):]
            )
            factors = factor_matches[:3] if factor_matches else []
            
        return {
            "action": action,
            "quantity": quantity,
            "confidence": confidence,
            "reasoning": text[:400],
            "key_factors": factors,
            "timestamp": datetime.utcnow().isoformat(),
        }

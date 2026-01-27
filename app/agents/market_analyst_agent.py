"""Market Analyst Agent - Analyzes market data and technical indicators."""

import google.generativeai as genai
from app.agents.tools import execute_tool
from app.agents.agent_communication import AgentCommunicationHub
from app.config import settings
from typing import Dict, Any
from loguru import logger
from datetime import datetime


class MarketAnalystAgent:
    """
    Specialist agent for market analysis.
    
    Responsibilities:
    - Fetch and analyze market data
    - Compute technical indicators (RSI, MACD, Moving Averages)
    - Identify trends and patterns
    - Provide market insights to other agents
    """
    
    def __init__(self, communication_hub: AgentCommunicationHub):
        """
        Initialize Market Analyst Agent.
        
        Args:
            communication_hub: Communication hub for inter-agent messaging
        """
        self.name = "MarketAnalyst"
        self.communication_hub = communication_hub
        self.communication_hub.register_agent(self.name, self)
        
        # Configure Gemini for market analysis
        genai.configure(api_key=settings.GOOGLE_AI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=self._get_system_prompt(),
        )
        
    def _get_system_prompt(self) -> str:
        """Get system prompt for market analyst."""
        return """You are a Market Analyst Agent specializing in technical analysis.

Your role:
- Analyze market data and price movements
- Compute and interpret technical indicators
- Identify trends, support/resistance levels
- Assess market momentum and volatility
- Provide objective, data-driven insights

Focus on:
- Price action and volume analysis
- RSI overbought/oversold conditions
- MACD crossovers and divergences
- Moving average relationships
- Trend strength and direction

Be precise, objective, and base all conclusions on the data provided."""
        
    async def analyze_symbol(
        self, symbol: str, trace: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive market analysis for a symbol.
        
        Args:
            symbol: Stock ticker to analyze
            trace: Trace dictionary for logging
            
        Returns:
            Analysis results with technical insights
        """
        logger.info(f"🔬 [MarketAnalyst] Analyzing {symbol}")
        
        analysis_start = datetime.utcnow()
        
        # Step 1: Fetch market data
        market_data = await execute_tool("get_market_data", {"symbol": symbol})
        trace["tools_called"].append({
            "agent": self.name,
            "tool": "get_market_data",
            "symbol": symbol,
            "result": market_data,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        if "error" in market_data:
            return {
                "symbol": symbol,
                "status": "error",
                "error": market_data["error"],
            }
            
        # Step 2: Analyze technicals
        technicals = await execute_tool(
            "analyze_technicals", {"symbol": symbol, "period": "1mo"}
        )
        trace["tools_called"].append({
            "agent": self.name,
            "tool": "analyze_technicals",
            "symbol": symbol,
            "result": technicals,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Step 3: Get sentiment (optional)
        sentiment = await execute_tool("check_sentiment", {"symbol": symbol})
        trace["tools_called"].append({
            "agent": self.name,
            "tool": "check_sentiment",
            "symbol": symbol,
            "result": sentiment,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        # Step 4: Synthesize analysis with Gemini
        context = f"""Analyze {symbol} based on the following data:

Market Data:
- Current Price: ${market_data.get('current_price', 'N/A')}
- Change: {market_data.get('change_percent', 'N/A')}%
- Volume: {market_data.get('volume', 'N/A')}

Technical Indicators:
- RSI: {technicals.get('rsi', 'N/A')}
- MACD: {technicals.get('macd', {})}
- Moving Averages: {technicals.get('moving_averages', {})}
- Trend: {technicals.get('trend', 'N/A')}
- Signals: {technicals.get('signals', [])}

Sentiment: {sentiment.get('sentiment', 'neutral')}

Provide a concise technical analysis covering:
1. Trend direction and strength
2. Key support/resistance levels
3. Momentum indicators interpretation
4. Overall technical outlook (bullish/bearish/neutral)
5. Confidence level (0.0 to 1.0)

Be objective and data-driven."""

        chat = self.model.start_chat()
        response = chat.send_message(context)
        
        analysis_text = response.text
        
        # Parse confidence from analysis
        confidence = self._extract_confidence(analysis_text)
        
        result = {
            "symbol": symbol,
            "market_data": market_data,
            "technical_indicators": technicals,
            "sentiment": sentiment,
            "analysis": analysis_text,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat(),
            "duration_ms": int((datetime.utcnow() - analysis_start).total_seconds() * 1000),
        }
        
        # Broadcast findings to other agents
        self.communication_hub.broadcast(self.name, {
            "symbol": symbol,
            "analysis": result,
        })
        
        logger.info(
            f"✅ [MarketAnalyst] {symbol} analysis complete "
            f"(confidence: {confidence:.2f})"
        )
        
        return result
        
    def _extract_confidence(self, text: str) -> float:
        """
        Extract confidence score from analysis text.
        
        Args:
            text: Analysis text
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        import re
        
        # Look for confidence pattern
        match = re.search(
            r"confidence[:\s]+([0-9.]+)", text, re.IGNORECASE
        )
        
        if match:
            try:
                confidence = float(match.group(1))
                if confidence > 1:
                    confidence = confidence / 100
                return max(0.0, min(1.0, confidence))
            except:
                pass
                
        # Default to medium confidence
        return 0.5

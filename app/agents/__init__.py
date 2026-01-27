"""
Multi-Agent Trading System.

Specialized agents that collaborate for autonomous trading:
- MarketAnalystAgent: Market data and technical analysis
- RiskManagerAgent: Risk evaluation and position sizing
- PortfolioManagerAgent: Portfolio state and constraints
- ExecutionAgent: Final trading decisions
- MultiAgentCoordinator: Orchestrates all agents

These agents communicate through AgentCommunicationHub
for transparent, distributed decision-making.
"""

from app.agents.coordinator import MultiAgentCoordinator
from app.agents.market_analyst_agent import MarketAnalystAgent
from app.agents.risk_manager_agent import RiskManagerAgent
from app.agents.portfolio_manager_agent import PortfolioManagerAgent
from app.agents.execution_agent import ExecutionAgent
from app.agents.agent_communication import AgentCommunicationHub, AgentMessage, MessageType

__all__ = [
    "MultiAgentCoordinator",
    "MarketAnalystAgent",
    "RiskManagerAgent",
    "PortfolioManagerAgent",
    "ExecutionAgent",
    "AgentCommunicationHub",
    "AgentMessage",
    "MessageType",
]

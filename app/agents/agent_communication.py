"""Agent-to-agent communication system."""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from loguru import logger


class MessageType(str, Enum):
    """Types of messages agents can send."""
    
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    QUERY = "query"
    RESULT = "result"


class AgentMessage(BaseModel):
    """Message passed between agents."""
    
    from_agent: str
    to_agent: Optional[str] = None  # None for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    message_id: str


class AgentCommunicationHub:
    """
    Central communication hub for multi-agent system.
    
    Allows agents to:
    - Send messages to specific agents
    - Broadcast information to all agents
    - Query other agents for information
    - Share findings and recommendations
    """
    
    def __init__(self):
        """Initialize the communication hub."""
        self.agents: Dict[str, Any] = {}
        self.message_history: List[AgentMessage] = []
        self.shared_context: Dict[str, Any] = {}
        
    def register_agent(self, agent_name: str, agent_instance: Any):
        """
        Register an agent in the communication hub.
        
        Args:
            agent_name: Unique name for the agent
            agent_instance: The agent instance
        """
        self.agents[agent_name] = agent_instance
        logger.info(f"Agent registered: {agent_name}")
        
    def send_message(self, message: AgentMessage):
        """
        Send a message between agents.
        
        Args:
            message: The message to send
        """
        self.message_history.append(message)
        
        if message.message_type == MessageType.BROADCAST:
            logger.info(
                f"📢 BROADCAST from {message.from_agent}: "
                f"{list(message.content.keys())}"
            )
        else:
            logger.info(
                f"📨 {message.from_agent} → {message.to_agent}: "
                f"{message.message_type.value}"
            )
            
    def broadcast(self, from_agent: str, content: Dict[str, Any]) -> str:
        """
        Broadcast information to all agents.
        
        Args:
            from_agent: Agent sending the broadcast
            content: Information to broadcast
            
        Returns:
            Message ID
        """
        import uuid
        message_id = str(uuid.uuid4())
        
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=None,
            message_type=MessageType.BROADCAST,
            content=content,
            timestamp=datetime.utcnow(),
            message_id=message_id,
        )
        
        self.send_message(message)
        
        # Store in shared context
        self.shared_context[from_agent] = content
        
        return message_id
        
    def query_agent(
        self, from_agent: str, to_agent: str, query: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Query another agent for information.
        
        Args:
            from_agent: Agent making the query
            to_agent: Agent to query
            query: Query parameters
            
        Returns:
            Response from the queried agent, or None if not available
        """
        import uuid
        message_id = str(uuid.uuid4())
        
        message = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.QUERY,
            content=query,
            timestamp=datetime.utcnow(),
            message_id=message_id,
        )
        
        self.send_message(message)
        
        # For now, return shared context from target agent
        return self.shared_context.get(to_agent)
        
    def get_shared_context(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get shared context from the communication hub.
        
        Args:
            agent_name: Specific agent's context, or all if None
            
        Returns:
            Shared context dictionary
        """
        if agent_name:
            return self.shared_context.get(agent_name, {})
        return self.shared_context.copy()
        
    def update_shared_context(self, agent_name: str, updates: Dict[str, Any]):
        """
        Update shared context with new information.
        
        Args:
            agent_name: Agent providing the update
            updates: Dictionary of updates to merge
        """
        if agent_name not in self.shared_context:
            self.shared_context[agent_name] = {}
            
        self.shared_context[agent_name].update(updates)
        logger.debug(f"Context updated by {agent_name}: {list(updates.keys())}")
        
    def get_message_history(
        self, agent_name: Optional[str] = None, limit: int = 10
    ) -> List[AgentMessage]:
        """
        Get message history for debugging/logging.
        
        Args:
            agent_name: Filter by specific agent, or None for all
            limit: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        if agent_name:
            messages = [
                m
                for m in self.message_history
                if m.from_agent == agent_name or m.to_agent == agent_name
            ]
        else:
            messages = self.message_history
            
        return messages[-limit:]
        
    def clear(self):
        """Clear all communication history and shared context."""
        self.message_history.clear()
        self.shared_context.clear()
        logger.debug("Communication hub cleared")

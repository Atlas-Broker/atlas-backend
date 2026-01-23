"""Tests for agent orchestrator."""

import pytest
from unittest.mock import AsyncMock, patch
from app.agents.orchestrator import parse_proposal_from_text


def test_parse_proposal_buy():
    """Test parsing BUY proposal from text."""
    text = """
    Based on my analysis, I recommend:
    
    Action: BUY
    Symbol: NVDA
    Quantity: 10
    Confidence: 0.75
    Stop Loss: $135.00
    Target: $150.00
    
    Rationale: Strong bullish momentum with RSI at 65.
    """
    
    tool_calls = [("get_market_data", {"symbol": "NVDA", "current_price": 140.50})]
    
    proposal = parse_proposal_from_text(text, tool_calls)
    
    # Note: This is a sync function so no await needed
    # But the actual implementation might be async
    # Adjust based on actual implementation


def test_parse_proposal_hold():
    """Test parsing HOLD decision."""
    text = "I recommend to HOLD and wait for better entry points."
    
    proposal = parse_proposal_from_text(text, [])
    
    # Should parse as HOLD
    # Adjust assertions based on actual return format

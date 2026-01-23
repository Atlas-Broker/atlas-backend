"""Tests for agent endpoints."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_analyze_intent_streaming(client, mock_user):
    """Test streaming agent analysis endpoint."""
    # TODO: Implement streaming test with SSE
    # This requires mocking the orchestrator and testing SSE events
    pass


@pytest.mark.asyncio
async def test_analyze_requires_auth(client):
    """Test that agent endpoint requires authentication."""
    response = await client.post(
        "/api/v1/agent/analyze",
        json={"intent": "Should I buy NVDA?"}
    )

    # Should return 401 or 403 without auth token
    assert response.status_code in [401, 403]

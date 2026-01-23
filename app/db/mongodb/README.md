# MongoDB Database Layer

## Overview

This module handles MongoDB operations for agent traces and market data caching using Motor (async driver).

## Collections

**Thoughts Storage** - Agent black box:

- `agent_runs` - Complete agent execution traces with reasoning, tool calls, proposals
- `market_data_cache` - Market data snapshots with raw Yahoo Finance responses

## Key Principle: Reproducibility

Every agent decision stores:
1. **What the agent saw** - Raw market data snapshot from Yahoo Finance
2. **How it reasoned** - Tool calls, thinking process, confidence scores
3. **What it decided** - Trade proposals with full rationale

This allows reconstructing the agent's decision-making process at any point in time.

## Usage

```python
from app.db.mongodb.queries import save_agent_run, get_agent_run

# Save trace
run_id = await save_agent_run({
    "run_id": "abc-123",
    "user_id": "user-456",
    "input": "Should I buy NVDA?",
    "tools_called": [...],
    "proposal": {...}
})

# Retrieve trace
trace = await get_agent_run("abc-123")
```

## Indexes

- `run_id` - Unique index for fast lookups
- `timestamp` - Descending index for recent queries
- `expires_at` - TTL index for cache expiration

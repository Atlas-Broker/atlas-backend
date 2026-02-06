# Backend: AI Agent Competition System

## Overview

Multi-agent trading competition system where 4 Google Gemini models compete autonomously in live trading.

## Architecture

### Competition Coordinator
**File:** `app/agents/competition_coordinator.py`

Orchestrates daily trading competition:
- Manages 4 competing agents (Gemini 3 Flash, 3 Pro, 2.5 Flash, 2.5 Pro)
- Each agent starts with $30,000 USD
- Runs autonomous trading daily at 10am EST
- Updates leaderboard and performance metrics

### Agent Components

Each competing agent uses the full multi-agent system:
- **Market Analyst Agent** - Analyzes market conditions
- **Risk Manager Agent** - Evaluates portfolio risk
- **Portfolio Manager Agent** - Makes allocation decisions
- **Execution Agent** - Executes trades

### Key Features

1. **Independent Trading**
   - Each agent trades with its own Gemini model
   - Separate cash and position tracking
   - Isolated reasoning and decision-making

2. **Explainable AI**
   - All reasoning stored in `agent_reasoning` table
   - Links decisions to specific trades
   - Three types: market_analysis, risk_assessment, decision

3. **Performance Tracking**
   - Daily snapshots in `agent_daily_performance`
   - Cumulative and daily returns
   - Sharpe ratio, max drawdown, win rate

4. **Public Access**
   - All competition endpoints are public (no auth)
   - Real-time leaderboard
   - Historical performance charts
   - Portfolio transparency

## API Endpoints

### Public Endpoints (No Auth)

**Base URL:** `/api/v1/competition`

#### Get Leaderboard
```
GET /leaderboard
```
Returns current rankings sorted by equity.

#### Get Performance Data
```
GET /performance?days=30
```
Returns daily equity/returns for all agents (for charting).

#### Get All Competitors
```
GET /competitors
```
Returns full details on all 4 competing agents.

#### Get Agent Portfolio
```
GET /portfolio/{competitor_id}
```
Returns current positions for a specific agent.

#### Get Agent Trades
```
GET /trades/{competitor_id}?limit=50
```
Returns trade history for a specific agent.

#### Get Agent Reasoning
```
GET /reasoning/{competitor_id}?reasoning_type=decision&limit=20
```
Returns reasoning records for explainable AI.

**Reasoning Types:**
- `market_analysis` - Market insights and trends
- `risk_assessment` - Risk evaluation
- `decision` - Trade decision rationale

## Scheduler

**File:** `app/scheduler/scheduler.py`

Competition runs automatically:
- **Schedule:** Daily at 10am EST, Mon-Fri
- **Job ID:** `agent_competition`
- **Watchlist:** Top 10 NASDAQ stocks (AAPL, MSFT, GOOGL, AMZN, NVDA, TSLA, META, AMD, NFLX, INTC)

## Testing

### Manual Trigger (Dev Only)
```bash
curl -X POST http://localhost:8000/api/v1/jobs/run-competition-dev
```

**Note:** Only works in `ENVIRONMENT=development` mode.

### Check Leaderboard
```bash
curl http://localhost:8000/api/v1/competition/leaderboard
```

### Get Performance Chart Data
```bash
curl http://localhost:8000/api/v1/competition/performance?days=7
```

## Database Integration

Queries all competition tables via `app/db/supabase/queries.py`:
- `get_all_competitors()` - Get active agents
- `get_daily_performance()` - Get time-series data
- `get_agent_positions()` - Get current holdings
- `get_agent_trades()` - Get trade history
- `get_agent_reasoning()` - Get decision explanations
- `get_current_leaderboard()` - Get today's rankings

## Deployment Notes

1. **Environment Variable**
   - `ENVIRONMENT=production` disables dev endpoints
   - Scheduler runs automatically on startup

2. **Supabase RLS**
   - All competition tables have public read access
   - Service role required for writes

3. **MongoDB**
   - Agent reasoning metadata stored in JSONB
   - Market analysis cached for performance

## Next Steps

After frontend integration:
1. Monitor agent performance in production
2. Add more sophisticated metrics (Sortino, Calmar ratios)
3. Implement portfolio rebalancing logic
4. Add risk-adjusted position sizing

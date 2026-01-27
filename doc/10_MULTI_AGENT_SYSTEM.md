# Multi-Agent Trading System

## Overview

Atlas uses a **Multi-Agent System** with 4 specialized AI agents that collaborate to make trading decisions autonomously. Each agent has specific responsibilities and communicates through a central hub.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Multi-Agent Coordinator                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │     Agent Communication Hub                     │    │
│  │  (Message passing & shared context)             │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Market     │  │     Risk     │  │  Portfolio   │ │
│  │   Analyst    │→ │   Manager    │→ │   Manager    │ │
│  │              │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↓                  ↓                  ↓         │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Execution Agent                        │  │
│  │      (Final decision-maker)                      │  │
│  └──────────────────────────────────────────────────┘  │
│                         ↓                               │
└─────────────────────────┼───────────────────────────────┘
                          ↓
                  ┌───────────────┐
                  │ Trade Executor │
                  │  (Supabase)    │
                  └───────────────┘
```

---

## Specialized Agents

### 1. Market Analyst Agent 🔬

**Role**: Technical analysis and market data expert

**Responsibilities**:
- Fetch current market data (price, volume)
- Compute technical indicators (RSI, MACD, Moving Averages)
- Identify trends and momentum
- Assess sentiment
- Provide objective market insights

**Tools Used**:
- `get_market_data(symbol)`
- `analyze_technicals(symbol, period)`
- `check_sentiment(symbol)`

**Output**:
```python
{
    "symbol": "NVDA",
    "market_data": {...},
    "technical_indicators": {
        "rsi": 65.3,
        "macd": {...},
        "trend": "bullish",
        "signals": ["RSI neutral", "MACD positive"]
    },
    "analysis": "NVDA showing bullish momentum...",
    "confidence": 0.75
}
```

---

### 2. Risk Manager Agent ⚖️

**Role**: Risk evaluation and position sizing specialist

**Responsibilities**:
- Evaluate risk/reward ratios
- Calculate appropriate position sizes
- Set stop loss and take profit levels
- Reject high-risk trades
- Ensure portfolio-level risk < 10%

**Risk Management Principles**:
- Maximum 2% risk per trade
- Minimum 2:1 reward/risk ratio
- Position size based on volatility
- Conservative defaults

**Output**:
```python
{
    "approval_status": "APPROVED",
    "risk_level": "MEDIUM",
    "recommended_quantity": 10,
    "stop_loss": 138.50,
    "take_profit": 152.00,
    "risk_reward_ratio": 2.3,
    "reasoning": "Risk acceptable with 2.3:1 ratio..."
}
```

---

### 3. Portfolio Manager Agent 💼

**Role**: Portfolio state and constraints manager

**Responsibilities**:
- Load current portfolio state
- Track cash and positions
- Enforce position limits (max 10 positions)
- Check portfolio constraints
- Prevent over-trading
- Monitor diversification

**Constraints Checked**:
- Maximum 10 concurrent positions
- Maximum $10,000 per position
- Sufficient cash available
- No duplicate positions (for swing trading)

**Output**:
```python
{
    "allowed": True,
    "violations": [],
    "current_positions": 5,
    "cash_available": 50000.00
}
```

---

### 4. Execution Agent 🎯

**Role**: Final decision-maker and trade coordinator

**Responsibilities**:
- Review all agent inputs
- Synthesize information
- Make final BUY/SELL/HOLD decision
- Provide clear reasoning
- Only approve when all agents agree

**Decision Framework**:
1. Market conditions must be favorable (Market Analyst)
2. Risk must be acceptable (Risk Manager)
3. Portfolio constraints must be satisfied (Portfolio Manager)
4. Overall confidence must be sufficient

**Output**:
```python
{
    "action": "BUY",
    "quantity": 10,
    "confidence": 0.78,
    "reasoning": "All agents agree: bullish trend, acceptable risk...",
    "key_factors": [
        "Strong technical setup",
        "2.3:1 risk/reward",
        "Portfolio capacity available"
    ]
}
```

---

## Agent Communication

### Communication Hub

All agents communicate through `AgentCommunicationHub`:

**Features**:
- Broadcast messages to all agents
- Direct agent-to-agent queries
- Shared context storage
- Message history logging

**Message Types**:
- `REQUEST` - Agent requests information
- `RESPONSE` - Response to a request
- `BROADCAST` - Share findings with all agents
- `QUERY` - Query specific agent
- `RESULT` - Return query result

**Example Communication**:
```python
# Market Analyst broadcasts findings
hub.broadcast("MarketAnalyst", {
    "symbol": "NVDA",
    "analysis": {...}
})

# Execution Agent queries Risk Manager
risk_eval = hub.query_agent(
    "ExecutionAgent", 
    "RiskManager", 
    {"symbol": "NVDA"}
)
```

---

## Trading Cycle Flow

### Step-by-Step Process

```
1. PERCEIVE
   ├─ Portfolio Manager loads current state
   ├─ Broadcasts portfolio to all agents
   └─ Sets context for decision-making

2. ANALYZE (For each symbol in watchlist)
   ├─ Market Analyst fetches data
   ├─ Computes technical indicators
   ├─ Broadcasts market analysis
   └─ Shares confidence level

3. EVALUATE RISK
   ├─ Risk Manager receives market analysis
   ├─ Calculates position size
   ├─ Sets stop loss / take profit
   ├─ Approves or rejects on risk basis
   └─ Broadcasts risk evaluation

4. CHECK CONSTRAINTS
   ├─ Portfolio Manager checks position limits
   ├─ Verifies cash availability
   ├─ Identifies constraint violations
   └─ Returns allowed/rejected status

5. DECIDE
   ├─ Execution Agent reviews all inputs
   ├─ Synthesizes information
   ├─ Makes final decision: BUY/SELL/HOLD
   └─ Broadcasts decision with reasoning

6. ACT
   ├─ Execute approved trades
   ├─ Update positions in Supabase
   └─ Log all actions

7. REFLECT
   ├─ Compare before/after portfolio state
   ├─ Calculate P&L
   ├─ Generate lessons learned
   └─ Save equity snapshot
```

---

## Advantages of Multi-Agent System

### 1. **Separation of Concerns**
Each agent focuses on its specialty:
- Cleaner code
- Easier to test
- Modular and maintainable

### 2. **Checks and Balances**
Multiple agents must agree:
- Reduces single-point failures
- More conservative decisions
- Built-in safety mechanisms

### 3. **Transparency**
All agent communications logged:
- Full audit trail
- Explainable decisions
- Debugging made easy

### 4. **Scalability**
Easy to add new agents:
- Add sentiment analyzer
- Add news parser
- Add technical pattern detector

### 5. **Specialization**
Each agent uses optimized prompts:
- More accurate analysis
- Better risk management
- Higher quality decisions

---

## Usage

### Running Autonomous Pilot

```python
from app.agents.autonomous_pilot import run_autonomous_pilot

# Run complete trading cycle
trace = await run_autonomous_pilot()

print(f"Trades executed: {trace['reflection']['trades_executed']}")
print(f"P&L: ${trace['reflection']['total_pnl']:+.2f}")
```

### Manual Multi-Agent Coordination

```python
from app.agents.coordinator import MultiAgentCoordinator

# Initialize coordinator
coordinator = MultiAgentCoordinator(account_id="pilot")

# Run trading cycle
watchlist = ["NVDA", "TSLA", "AAPL"]
decisions = await coordinator.run_trading_cycle(
    watchlist=watchlist,
    trace={}
)

# Get communication log
comm_log = coordinator.get_communication_log()
```

---

## Configuration

### Watchlist

Currently hardcoded in `autonomous_pilot.py`:
```python
watchlist = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"]
```

**TODO**: Make configurable via database

### Risk Parameters

Set in `.env`:
```bash
PAPER_MAX_POSITIONS=10          # Max concurrent positions
PAPER_MAX_POSITION_SIZE=10000   # Max dollars per position
```

### Agent Models

All agents use:
- Model: `gemini-2.0-flash-exp`
- Temperature: Default (controlled by Gemini)
- Function calling: Enabled for tools

---

## Observability

### Logging

All agent activities logged with emojis:
- 🔬 Market Analyst analyzing
- ⚖️ Risk Manager evaluating
- 💼 Portfolio Manager loading state
- 🎯 Execution Agent deciding
- 💰 Trade execution

### MongoDB Traces

Every pilot run saved with:
- All agent communications
- Tool calls with timestamps
- Final decisions
- Trade results
- Agent communication log

**View trace**:
```bash
GET /api/v1/traces/{run_id}
```

---

## Testing

### Run Pilot Manually

```bash
# Via script
python scripts/run_pilot.py

# Via API
curl -X POST http://localhost:8000/api/v1/jobs/run-pilot \
  -H "Authorization: Bearer $TOKEN"
```

### View Localhost Agent Activity

```bash
# Start server
uvicorn app.main:app --reload

# Watch logs in real-time
# You'll see all 4 agents collaborating!
```

---

## Future Enhancements

### Planned Agents

1. **Sentiment Agent** - Parse news and social media
2. **Pattern Recognition Agent** - Identify chart patterns
3. **Fundamental Analysis Agent** - Analyze earnings, P/E ratios
4. **Macro Agent** - Consider market-wide conditions

### Planned Features

1. **Agent Voting System** - Weighted consensus mechanism
2. **Agent Learning** - Improve from past decisions
3. **Dynamic Watchlists** - Agents suggest new symbols
4. **Real-time Adaptation** - Adjust strategy based on market conditions

---

## Troubleshooting

### Agent Not Responding

Check:
1. Gemini API key valid
2. Network connectivity
3. Rate limits not exceeded

### Unexpected Decisions

Review:
1. Agent communication log
2. Market data at decision time
3. Risk evaluation reasoning
4. Portfolio constraints

### Trades Not Executing

Verify:
1. Portfolio Manager constraints satisfied
2. Sufficient cash available
3. Risk Manager approved
4. Execution Agent decided BUY/SELL (not HOLD)

---

## Summary

The Multi-Agent System provides:
- ✅ **Specialized expertise** from 4 AI agents
- ✅ **Transparent collaboration** via communication hub
- ✅ **Conservative decision-making** with multiple checks
- ✅ **Complete auditability** of every decision
- ✅ **Production-ready** autonomous trading

**Each agent is an expert. Together, they make Atlas intelligent.**

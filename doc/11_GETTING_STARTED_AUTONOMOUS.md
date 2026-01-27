# Getting Started with Autonomous Trading

## Quick Start Guide for Running the Multi-Agent System Locally

This guide will help you get the autonomous multi-agent trading system running on your local machine at `localhost:8000`.

---

## Prerequisites

Before starting, ensure you have:

- ✅ Python 3.11+
- ✅ MongoDB Atlas account (or local MongoDB)
- ✅ Supabase account
- ✅ Google AI API key (for Gemini)

---

## Step 1: Clone and Setup Environment

```bash
# Navigate to backend
cd atlas-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Step 2: Configure Environment Variables

Create a `.env` file in the `atlas-backend` directory:

```bash
# Copy example
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `.env` with your credentials:

```bash
# Database - Supabase (PostgreSQL)
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Database - MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=atlas_production

# AI - Google Gemini
GOOGLE_AI_API_KEY=AIzaSy...your_key_here

# Paper Trading Settings
PAPER_STARTING_CASH=100000
PAPER_MAX_POSITIONS=10
PAPER_MAX_POSITION_SIZE=10000

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=INFO

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

---

## Step 3: Setup Databases

### Supabase (PostgreSQL)

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy contents of `migrations/supabase/001_paper_trading.sql`
4. Execute the SQL script
5. Verify tables created: `paper_accounts`, `paper_orders`, `paper_positions`, `equity_snapshots`

### MongoDB

MongoDB collections are created automatically on first run. No manual setup needed!

---

## Step 4: Run the Server

Start the FastAPI server:

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or run directly
python -m uvicorn app.main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
🤖 Multi-Agent System initialized with 4 specialized agents
```

---

## Step 5: Verify Server is Running

Open your browser and visit:

- **API Docs (Swagger)**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

You should see the API documentation and be able to interact with endpoints.

---

## Step 6: Run Autonomous Pilot Manually

### Option A: Via API (Recommended for testing)

```bash
# Trigger autonomous pilot run
curl -X POST http://localhost:8000/api/v1/jobs/run-pilot \
  -H "Content-Type: application/json"
```

### Option B: Via Python Script

```bash
python scripts/run_pilot.py
```

---

## Step 7: Watch Agents in Action! 🤖

When you trigger the pilot, you'll see **detailed logs** of all 4 agents collaborating:

```
🚀 AUTONOMOUS PILOT RUN: abc-123-def-456
📋 Watchlist: NVDA, TSLA, AAPL, MSFT, GOOGL, AMZN, META

🤖 Initializing Multi-Agent System...
============================================================
PHASE 1: PERCEIVE & PLAN (Multi-Agent Coordination)
============================================================

💼 [PortfolioManager] Loading portfolio state
💼 [PortfolioManager] Portfolio loaded: $100000.00 equity, 0 positions

────────────────────────────────────────────────────────────
Processing: NVDA
────────────────────────────────────────────────────────────

🔬 [MarketAnalyst] Analyzing NVDA
🔧 Executing tool: get_market_data with params: {'symbol': 'NVDA'}
🔧 Executing tool: analyze_technicals with params: {'symbol': 'NVDA'}
✅ [MarketAnalyst] NVDA analysis complete (confidence: 0.75)

⚖️ [RiskManager] Evaluating BUY NVDA
✅ [RiskManager] NVDA BUY: APPROVED

📋 [PortfolioManager] Checking constraints for BUY 10 NVDA
✅ [PortfolioManager] Trade constraints satisfied

🎯 [ExecutionAgent] Making decision for NVDA
💰 [ExecutionAgent] NVDA: BUY (10 shares)

────────────────────────────────────────────────────────────
PHASE 2: ACT (Trade Execution)
────────────────────────────────────────────────────────────

💰 Executing: BUY 10 NVDA
✅ Trade executed: BUY 10 NVDA

────────────────────────────────────────────────────────────
PHASE 3: REFLECT (Performance Analysis)
────────────────────────────────────────────────────────────

============================================================
✅ PILOT RUN COMPLETE
============================================================
📈 Trades executed: 1
💵 P&L: $0.00
💰 Total equity: $98500.00
⏱️  Duration: 15420ms
============================================================
```

---

## Step 8: View Results

### Via API

**Get recent traces**:
```bash
curl http://localhost:8000/api/v1/traces?mode=autonomous&limit=5
```

**Get specific trace**:
```bash
curl http://localhost:8000/api/v1/traces/{run_id}
```

**View portfolio**:
```bash
curl http://localhost:8000/api/v1/portfolio/summary
```

**View positions**:
```bash
curl http://localhost:8000/api/v1/portfolio/positions
```

### Via Swagger UI

1. Go to http://localhost:8000/docs
2. Try the endpoints interactively
3. View request/response schemas

### Via MongoDB

Connect to your MongoDB cluster and query:

```javascript
// View latest agent run
db.agent_runs.findOne({}, {sort: {timestamp: -1}})

// View all autonomous runs
db.agent_runs.find({mode: "autonomous_multi_agent"})

// See agent communication log
db.agent_runs.findOne({run_id: "your-run-id"}).agent_communication_log
```

---

## What's Happening Behind the Scenes?

When you run the autonomous pilot:

1. **Portfolio Manager** loads current cash and positions
2. **Market Analyst** analyzes each symbol in watchlist:
   - Fetches real market data from Yahoo Finance
   - Computes RSI, MACD, Moving Averages
   - Uses Gemini AI to synthesize analysis
   
3. **Risk Manager** evaluates each trade:
   - Calculates position size (max $10,000)
   - Sets stop loss and take profit
   - Approves or rejects based on risk/reward
   
4. **Execution Agent** makes final decision:
   - Reviews all agent inputs
   - Decides BUY, SELL, or HOLD
   - Provides transparent reasoning
   
5. **Trade Executor** submits approved trades:
   - Creates orders in Supabase
   - Updates positions and cash
   - Logs everything to MongoDB

6. **Reflection** analyzes performance:
   - Compares before/after portfolio
   - Calculates P&L
   - Saves equity snapshot

---

## Scheduled Autonomous Trading

The pilot can run automatically on a schedule:

**Default Schedule** (in `app/scheduler/scheduler.py`):
- 9:00 AM EST (market open)
- 3:00 PM EST (before market close)
- Monday - Friday only

**To enable scheduled runs**:

The scheduler starts automatically with the server. Trades will execute at scheduled times without manual intervention!

**To disable scheduled runs**:

Comment out the scheduler initialization in `app/main.py`:

```python
# start_scheduler()  # Disable scheduled pilot
```

---

## Customization

### Change Watchlist

Edit `app/agents/autonomous_pilot.py`:

```python
# Current watchlist
watchlist = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"]

# Add your symbols
watchlist = ["YOUR_SYMBOL_1", "YOUR_SYMBOL_2", ...]
```

**TODO**: Make watchlist configurable via database/API

### Adjust Risk Parameters

Edit `.env`:

```bash
# Maximum concurrent positions
PAPER_MAX_POSITIONS=10

# Maximum dollars per position
PAPER_MAX_POSITION_SIZE=10000

# Starting cash
PAPER_STARTING_CASH=100000
```

### Modify Agent Prompts

Edit agent system prompts in:
- `app/agents/market_analyst_agent.py` - Market analysis prompt
- `app/agents/risk_manager_agent.py` - Risk management prompt
- `app/agents/execution_agent.py` - Final decision prompt

---

## Troubleshooting

### Server won't start

**Check**:
- Python version 3.11+
- All dependencies installed
- `.env` file exists with correct values
- MongoDB and Supabase accessible

### No trades executing

**Check**:
- Portfolio has sufficient cash
- Watchlist symbols are valid US stocks
- Google AI API key is valid
- Not exceeding max positions (10)

### Agent errors in logs

**Check**:
- Google AI API rate limits
- Network connectivity
- Yahoo Finance API availability
- Gemini API key validity

### MongoDB connection errors

**Check**:
- MongoDB URI correct
- IP whitelist includes your IP
- Database name matches

### Supabase errors

**Check**:
- Migration ran successfully
- Service role key is correct
- Database URL format correct

---

## Next Steps

Once you have the system running locally:

1. ✅ **Experiment** - Modify watchlist and observe decisions
2. ✅ **Review Logs** - Study agent reasoning and communication
3. ✅ **Check MongoDB** - Examine full traces and tool calls
4. ✅ **Tune Parameters** - Adjust risk settings
5. ✅ **Deploy to EC2** - Follow production deployment guide

---

## Production Deployment (EC2)

See `doc/12_EC2_DEPLOYMENT.md` for complete EC2 deployment instructions.

**Quick Overview**:
1. Launch EC2 instance (t3.medium recommended)
2. Install Python 3.11+ and dependencies
3. Configure environment variables
4. Setup systemd service
5. Configure nginx reverse proxy
6. Enable HTTPS with Let's Encrypt
7. Monitor with CloudWatch

---

## Monitoring & Observability

### Logs

All agent activity logged to:
- Console (in development)
- `logs/` directory (in production)

**Tail logs**:
```bash
tail -f logs/atlas.log
```

### MongoDB Traces

Every decision fully logged:
```bash
# View trace details
curl http://localhost:8000/api/v1/traces/{run_id}
```

### Supabase Database

Check tables directly:
- `paper_orders` - All orders
- `paper_positions` - Current positions
- `equity_snapshots` - Equity over time

---

## Support & Resources

- **Full Documentation**: See `doc/` folder
- **Multi-Agent System Details**: `doc/10_MULTI_AGENT_SYSTEM.md`
- **API Reference**: http://localhost:8000/docs
- **Project Summary**: `doc/03_PROJECT_SUMMARY.md`

---

## Success Criteria ✅

You'll know everything is working when:

1. ✅ Server starts without errors
2. ✅ Swagger docs accessible at `/docs`
3. ✅ Pilot runs successfully
4. ✅ See all 4 agents logging their work
5. ✅ Trades appear in Supabase
6. ✅ Traces saved to MongoDB
7. ✅ Portfolio state updates correctly

---

**You're now running a sophisticated multi-agent autonomous trading system! 🚀**

The agents are analyzing markets, evaluating risks, and making trades—all autonomously and transparently.

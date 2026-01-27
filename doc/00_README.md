# Atlas Backend - Intelligence API

**Agentic AI Swing Trading Backend with Real-Time Streaming**

---

## 🎯 Overview

Atlas Backend is the Intelligence API powering Atlas - an agentic AI swing trading platform. This FastAPI backend provides:

- **🤖 Streaming Agent Copilot** - Real-time trade analysis with human-in-the-loop approval
- **🚀 Autonomous Paper Trader** - Scheduled agent that trades autonomously
- **📊 Dual Storage Architecture** - PostgreSQL for facts, MongoDB for agent thoughts
- **🔄 Real-Time Streaming** - Server-Sent Events (SSE) for live agent reasoning
- **📈 Complete Observability** - Full black box flight recorder for every decision

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js Frontend                        │
│                  (User Interface + Charts)                   │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP + SSE Streaming
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   Agent     │  │   Market     │  │    Portfolio     │  │
│  │Orchestrator │  │Data Service  │  │   Management     │  │
│  │(Streaming)  │  │(Yahoo $$)    │  │  (Paper Trade)   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
│          │                │                    │             │
│          ▼                ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Gemini 2.0 Flash (Function Calling)        │  │
│  └──────────────────────────────────────────────────────┘  │
└───────┬──────────────────────────────────┬─────────────────┘
        │                                  │
        ▼                                  ▼
┌───────────────────┐            ┌──────────────────┐
│  Supabase (SQL)   │            │  MongoDB         │
│  - Orders         │            │  - Agent Traces  │
│  - Positions      │            │  - Market Cache  │
│  - Equity Curve   │            │  - Reasoning     │
└───────────────────┘            └──────────────────┘
```

### Two Operating Modes

**Lane A - Trader Copilot** (Human-in-the-Loop)
```
User Intent → Agent Analysis (streaming) → Trade Proposal → Human Approval → Execution
```

**Lane B - Autonomous Pilot** (Scheduled)
```
Cron Trigger → Perceive → Plan → Act → Reflect → Equity Snapshot
```

---

## 📚 Documentation

- **[SETUP_GUIDE.md](./knowledge/SETUP_GUIDE.md)** - Complete step-by-step setup instructions
- **[PROJECT_SUMMARY.md](./knowledge/PROJECT_SUMMARY.md)** - Comprehensive overview of what was built
- **[API Docs (Swagger)](http://localhost:8000/docs)** - Interactive API documentation (when server is running)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional, for local MongoDB)
- Supabase account
- MongoDB Atlas account (or local MongoDB)
- Google AI API key (Gemini)
- Clerk account (for authentication)

### 1. Clone and Setup

```bash
git clone <your-repo>
cd atlas-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `DATABASE_URL` - PostgreSQL connection string
- `MONGODB_URI` - MongoDB connection string
- `GOOGLE_AI_API_KEY` - Google AI (Gemini) API key
- `CLERK_SECRET_KEY` - Clerk authentication secret

### 3. Database Setup

**Supabase (PostgreSQL):**
```bash
# Run migration in Supabase SQL Editor
# Copy contents of migrations/supabase/001_paper_trading.sql
```

**MongoDB:**
```bash
# Indexes are created automatically on startup
# Or use Docker Compose for local MongoDB
docker-compose up mongodb -d
```

### 4. Run the Server

**Development:**
```bash
uvicorn app.main:app --reload
```

**Production:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Docker Compose (recommended for local dev):**
```bash
docker-compose up
```

The API will be available at: `http://localhost:8000`

### 5. Test the API

Open your browser to:
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### 🤖 Agent Copilot

**`POST /api/v1/agent/analyze`** - Stream agent analysis (SSE)

```javascript
// Frontend example
const eventSource = new EventSource('/api/v1/agent/analyze', {
  headers: { 'Authorization': `Bearer ${token}` }
});

eventSource.addEventListener('thinking', (e) => {
  const data = JSON.parse(e.data);
  console.log('Agent thinking:', data.thought);
});

eventSource.addEventListener('proposal', (e) => {
  const proposal = JSON.parse(e.data);
  console.log('Trade proposal:', proposal);
});
```

### 📋 Orders

- `POST /api/v1/orders/{order_id}/approve` - Approve proposed trade
- `POST /api/v1/orders/{order_id}/reject` - Reject proposed trade
- `GET /api/v1/orders` - List orders (with filters)

### 💼 Portfolio

- `GET /api/v1/portfolio/summary` - Current holdings and P&L
- `GET /api/v1/portfolio/equity-curve` - Historical equity data
- `GET /api/v1/portfolio/positions` - Current positions

### 📊 Trades

- `GET /api/v1/trades/recent` - Recent filled orders

### 🔍 Traces

- `GET /api/v1/traces/{run_id}` - Full MongoDB trace
- `GET /api/v1/traces` - List recent agent runs

### ⚙️ Jobs (Admin)

- `POST /api/v1/jobs/run-pilot` - Manually trigger pilot
- `GET /api/v1/jobs/pilot-status` - Check pilot status

---

## 🎭 Streaming Agent Flow

The streaming agent is the **centerpiece** of this backend:

```
User: "Should I buy NVDA?"
  ↓
[ANALYZING] Agent starts reasoning
  ↓ SSE: event=status, data={"status":"ANALYZING"}
  ↓
[THINKING] "Let me check NVDA's current price..."
  ↓ SSE: event=thinking, data={"thought":"..."}
  ↓
[TOOL CALL] get_market_data(symbol="NVDA")
  ↓ SSE: event=tool_call, data={"tool":"get_market_data"}
  ↓
[TOOL RESULT] NVDA: $140.50 (+2.34%)
  ↓ SSE: event=tool_result, data={"summary":"NVDA: $140.50"}
  ↓
[THINKING] "RSI is at 65, bullish trend..."
  ↓
[PROPOSING] Generate trade recommendation
  ↓ SSE: event=status, data={"status":"PROPOSING"}
  ↓
[PROPOSAL] BUY 10 NVDA @ $140.50
  ↓ SSE: event=proposal, data={"action":"BUY",...}
  ↓
[COMPLETE] Trace saved to MongoDB
  ↓ SSE: event=complete, data={"trace_id":"abc-123"}
```

Frontend receives **live updates** at each step!

---

## 🤖 Autonomous Pilot

The pilot runs on a cron schedule (default: 9am and 3pm EST weekdays):

**PPAR Loop:**

1. **Perceive** - Load portfolio, fetch market data for watchlist
2. **Plan** - Agent analyzes each symbol, decides BUY/SELL/HOLD
3. **Act** - Execute trades automatically (no approval needed)
4. **Reflect** - Compute P&L, generate lessons learned

Manual trigger:
```bash
python scripts/run_pilot.py
```

Or via API:
```bash
curl -X POST http://localhost:8000/api/v1/jobs/run-pilot \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📦 Data Storage

### Supabase (PostgreSQL) - **FACTS**

Transactional data:
- Paper accounts (cash, equity)
- Orders (PROPOSED → APPROVED → FILLED)
- Positions (current holdings)
- Equity snapshots (time series)

### MongoDB - **THOUGHTS**

Agent traces (black box):
- Complete reasoning chains
- Tool calls with raw Yahoo Finance responses
- Market data snapshots (what agent saw)
- Proposals and decisions

**Why?** Enables reproducing agent decisions at any point in time.

---

## 🔐 Authentication

Uses **Clerk JWT** tokens:

```python
@router.get("/protected")
async def protected_route(user: User = Depends(verify_clerk_token)):
    return {"user_id": user.id}
```

Frontend sends:
```
Authorization: Bearer <clerk-jwt-token>
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app

# Seed test data
python scripts/seed_db.py
```

---

## 📊 Observability

Every agent run is fully logged:

**View in MongoDB:**
```javascript
db.agent_runs.findOne({run_id: "abc-123"})
```

**View via API:**
```bash
GET /api/v1/traces/abc-123
```

Contains:
- ✅ All tool calls with timestamps
- ✅ Raw market data snapshots
- ✅ Agent reasoning text
- ✅ Confidence scores
- ✅ Final proposal

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t atlas-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env atlas-backend
```

### Docker Compose (Full Stack)

```bash
docker-compose up
```

Includes:
- FastAPI backend
- MongoDB (local)

---

## ☁️ Production Deployment

### Recommended: AWS App Runner

1. **Build and push Docker image:**
```bash
docker build -t atlas-backend .
docker tag atlas-backend:latest <your-ecr-repo>:latest
docker push <your-ecr-repo>:latest
```

2. **Create App Runner service:**
   - Source: ECR
   - Enable auto-deployment
   - Set environment variables via Secrets Manager

3. **Configure:**
   - Port: 8000
   - Health check: `/health`
   - Auto-scaling: 1-10 instances

**Why App Runner?**
- ✅ Native streaming support (critical!)
- ✅ Auto-scaling
- ✅ HTTPS out of the box
- ✅ Simpler than ECS/EKS

### Alternative: EC2 + Docker

```bash
# On EC2 instance
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🛠️ Development

### Code Formatting

```bash
# Format code
black app/

# Lint
ruff check app/

# Type check
mypy app/
```

### Project Structure

```
atlas-backend/
├── app/
│   ├── agents/          # Agent logic (orchestrator, tools, prompts)
│   ├── api/             # FastAPI routes
│   ├── db/              # Database clients (Supabase, MongoDB, S3)
│   ├── middleware/      # Auth, logging, error handling
│   ├── schemas/         # Pydantic models
│   ├── scheduler/       # APScheduler jobs
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── migrations/          # SQL migrations
├── scripts/             # Utility scripts
├── tests/               # Test suite
└── requirements.txt     # Dependencies
```

---

## 🎯 Success Criteria

When everything works:

1. ✅ Start server: `uvicorn app.main:app --reload`
2. ✅ Swagger docs: `http://localhost:8000/docs`
3. ✅ Call streaming agent: `POST /api/v1/agent/analyze`
4. ✅ See real-time SSE events in browser/Postman
5. ✅ Approve trade: `POST /api/v1/orders/{id}/approve`
6. ✅ Check portfolio: `GET /api/v1/portfolio/summary`
7. ✅ View equity curve: `GET /api/v1/portfolio/equity-curve`
8. ✅ Trigger pilot: `POST /api/v1/jobs/run-pilot`
9. ✅ View traces: `GET /api/v1/traces/{run_id}`
10. ✅ Run in Docker: `docker-compose up`

---

## 🔧 Troubleshooting

### Streaming not working

- Check CORS configuration allows streaming
- Verify `X-Accel-Buffering: no` header is set
- Test with curl or Postman (supports SSE)

### Database connection errors

- Verify environment variables are set
- Check Supabase connection string format
- Ensure MongoDB is accessible

### Gemini API errors

- Verify `GOOGLE_AI_API_KEY` is valid
- Check API quota limits
- Review function calling format

---

## 📚 Learn More

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini Function Calling](https://ai.google.dev/docs/function_calling)
- [Server-Sent Events (SSE)](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Supabase Docs](https://supabase.com/docs)
- [MongoDB Motor](https://motor.readthedocs.io/)

---

## 🤝 Contributing

This is a thesis project, but contributions welcome!

---

## 📄 License

MIT

---

## 👨‍💻 Author

Built as part of Atlas - Agentic AI Swing Trading Platform

**This backend is the brain of Atlas - intelligent, observable, and bulletproof.**

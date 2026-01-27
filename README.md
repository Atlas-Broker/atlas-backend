# Atlas Backend

**AI-Powered Autonomous Trading API**

FastAPI backend with multi-agent autonomous trading system powered by Google Gemini 2.0 Flash.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 🌟 Features

### Multi-Agent Autonomous Trading
- **4 Specialized AI Agents**: Market Analyst, Risk Manager, Portfolio Manager, Execution Agent
- **Agent Communication Hub**: Transparent inter-agent messaging
- **PPAR Loop**: Perceive → Plan → Act → Reflect autonomous cycle
- **Full Observability**: Every decision traced and logged to MongoDB

### Real-Time Streaming Copilot
- **Server-Sent Events (SSE)**: Stream agent thinking in real-time
- **Human-in-the-Loop**: AI proposes, human approves
- **Interactive Analysis**: Ask questions, get detailed market insights

### Production-Ready Architecture
- **Dual Database**: Supabase (facts) + MongoDB (thoughts)
- **Market Data**: Yahoo Finance integration with caching
- **Scheduled Jobs**: Autonomous pilot runs 9am & 3pm EST (weekdays)
- **Paper Trading**: Safe testing environment before live trading

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Supabase account
- MongoDB Atlas account
- Google AI API key (Gemini 2.0 Flash)

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd atlas-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your credentials
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - MONGODB_URI
# - GOOGLE_API_KEY
```

### Database Setup

```bash
# 1. Run Supabase migration
# Go to: https://app.supabase.com/project/YOUR_PROJECT/sql
# Copy: ../atlas-database/migrations/supabase/001_unified_schema.sql
# Execute in SQL Editor

# 2. Setup MongoDB indexes
cd ../atlas-database
python scripts/run_mongodb_setup.py
```

### Run the Server

```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Server runs at: **http://localhost:8000**

API documentation: **http://localhost:8000/docs**

---

## 🤖 Autonomous Pilot

### Trigger Manually

```bash
# Development endpoint (no authentication)
curl -X POST http://localhost:8000/api/v1/jobs/run-pilot-dev

# Production endpoint (requires authentication)
curl -X POST http://localhost:8000/api/v1/jobs/run-pilot \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Scheduled Runs

Automatic runs at:
- **9:00 AM EST** (market open)
- **3:00 PM EST** (before close)
- **Monday - Friday** only

### What It Does

1. **Perceive**: Analyzes watchlist symbols using market data
2. **Plan**: Risk manager evaluates trades, portfolio manager checks constraints
3. **Act**: Execution agent makes final decision, creates orders in database
4. **Reflect**: Analyzes performance, updates equity snapshots

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────┐
│        Multi-Agent Coordinator           │
└─────────────┬───────────────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ▼         ▼         ▼         ▼
┌────────┐ ┌─────┐ ┌──────────┐ ┌───────────┐
│ Market │ │Risk │ │Portfolio │ │ Execution │
│Analyst │ │ Mgr │ │ Manager  │ │   Agent   │
└────────┘ └─────┘ └──────────┘ └───────────┘
    │         │         │             │
    └─────────┴─────────┴─────────────┘
              │
    ┌─────────▼─────────┐
    │ Communication Hub  │
    └───────────────────┘
```

### Database Architecture

**Supabase (PostgreSQL)** - Facts:
- `profiles` - User profiles (Clerk + system accounts)
- `accounts` - Trading accounts (paper/live)
- `orders` - Complete order history
- `positions` - Current holdings
- `equity_snapshots` - Portfolio value time series

**MongoDB** - Thoughts:
- `agent_runs` - Complete AI execution traces
- `market_data_cache` - Cached Yahoo Finance data

---

## 📡 API Endpoints

### Health & Status

```bash
GET  /health              # Health check
GET  /api/v1/status       # System status
```

### Agent Operations

```bash
POST /api/v1/agent/analyze           # Stream analysis (SSE)
POST /api/v1/jobs/run-pilot          # Trigger pilot (auth required)
POST /api/v1/jobs/run-pilot-dev      # Trigger pilot (dev only)
GET  /api/v1/jobs/status             # Job status
```

### Portfolio & Trading

```bash
GET  /api/v1/portfolio/summary       # Portfolio overview
GET  /api/v1/positions               # Current positions
GET  /api/v1/orders                  # Order history
POST /api/v1/orders                  # Create order
PUT  /api/v1/orders/{id}/approve     # Approve order
GET  /api/v1/trades/recent           # Recent trades
```

### Traces & Observability

```bash
GET  /api/v1/traces                  # List agent runs
GET  /api/v1/traces/{run_id}         # Get specific trace
```

See full API docs: **http://localhost:8000/docs**

---

## 🧪 Development

### Project Structure

```
atlas-backend/
├── app/
│   ├── agents/              # Multi-agent system
│   │   ├── coordinator.py           # Orchestrates all agents
│   │   ├── market_analyst_agent.py  # Market analysis
│   │   ├── risk_manager_agent.py    # Risk assessment
│   │   ├── portfolio_manager_agent.py
│   │   ├── execution_agent.py       # Final decisions
│   │   ├── agent_communication.py   # Inter-agent messaging
│   │   └── autonomous_pilot.py      # Scheduled autonomous runs
│   │
│   ├── api/v1/              # API routes
│   │   ├── agent.py         # Agent endpoints
│   │   ├── jobs.py          # Job management
│   │   ├── portfolio.py     # Portfolio endpoints
│   │   └── traces.py        # Trace endpoints
│   │
│   ├── db/                  # Database clients
│   │   ├── supabase/        # PostgreSQL
│   │   └── mongodb/         # MongoDB
│   │
│   ├── services/            # Business logic
│   │   ├── market_data.py   # Yahoo Finance
│   │   ├── portfolio.py     # Portfolio management
│   │   └── order_execution.py
│   │
│   ├── scheduler/           # APScheduler jobs
│   └── main.py              # FastAPI app
│
├── doc/                     # Documentation
├── scripts/                 # Utility scripts
└── requirements.txt         # Python dependencies
```

### Environment Variables

See `env.example` for all required variables:

```bash
# Server
ENVIRONMENT=development
PORT=8000

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxx

# MongoDB
MONGODB_URI=mongodb+srv://xxx
MONGODB_DB_NAME=atlas-mongodb

# Google AI
GOOGLE_API_KEY=AIzaxxx

# Clerk (optional for auth)
CLERK_SECRET_KEY=sk_xxx
```

### Testing

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_agents/test_coordinator.py

# With coverage
pytest --cov=app tests/
```

---

## 📊 Monitoring & Logs

### Structured Logging

All logs use structured format with Loguru:

```python
from loguru import logger

logger.info("Order created", order_id=order.id, symbol=order.symbol)
logger.error("Order failed", order_id=order.id, error=str(e))
```

### Trace Every Decision

Every agent run is logged to MongoDB:

```javascript
{
  "run_id": "abc-123",
  "mode": "autonomous_multi_agent",
  "timestamp": "2026-01-27T14:30:00Z",
  "tools_called": [...],
  "agent_communication_log": [...],
  "decisions": [...],
  "status": "COMPLETE"
}
```

View traces: `GET /api/v1/traces`

---

## 🚢 Deployment

### Docker

```bash
# Build image
docker build -t atlas-backend .

# Run container
docker run -p 8000:8000 --env-file .env atlas-backend
```

### Docker Compose

```bash
docker-compose up -d
```

### AWS EC2

```bash
# 1. Launch EC2 instance (t3.small or larger)
# 2. SSH into instance
# 3. Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip

# 4. Clone repo
git clone <your-repo>
cd atlas-backend

# 5. Install requirements
pip3 install -r requirements.txt

# 6. Setup systemd service
sudo cp deployment/atlas-backend.service /etc/systemd/system/
sudo systemctl enable atlas-backend
sudo systemctl start atlas-backend
```

---

## 📚 Documentation

Complete documentation in `doc/` folder:

- **[00_README.md](./doc/00_README.md)** - Overview
- **[01_INDEX.md](./doc/01_INDEX.md)** - Documentation index
- **[10_MULTI_AGENT_SYSTEM.md](./doc/10_MULTI_AGENT_SYSTEM.md)** - Multi-agent architecture ⭐
- **[11_GETTING_STARTED_AUTONOMOUS.md](./doc/11_GETTING_STARTED_AUTONOMOUS.md)** - Quick start ⭐
- **[12_TROUBLESHOOTING.md](./doc/12_TROUBLESHOOTING.md)** - Common issues

### External Documentation

- **Database schemas**: See `../atlas-database/doc/`
- **API reference**: http://localhost:8000/docs
- **Frontend integration**: See `../atlas-frontend/`

---

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/amazing-feature`
2. Make changes and test thoroughly
3. Update documentation
4. Commit: `git commit -m "Add amazing feature"`
5. Push: `git push origin feature/amazing-feature`
6. Open Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 🔗 Related Repositories

- **[atlas-database](../atlas-database)** - Centralized database schemas & migrations
- **[atlas-frontend](../atlas-frontend)** - Next.js frontend application

---

## 💬 Support

- **Documentation**: See `doc/` folder
- **Issues**: Open a GitHub issue
- **Discussions**: GitHub Discussions

---

**Built with ❤️ for autonomous trading**

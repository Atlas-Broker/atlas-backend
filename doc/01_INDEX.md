# 📚 Atlas Backend - Documentation Index

**FastAPI Python Backend with Multi-Agent AI System**

---

## 📖 Documentation Structure

### **01. [INDEX.md](./01_INDEX.md)** 📍
Navigation hub for all backend documentation.

### **02. [SETUP.md](./02_SETUP.md)** ⚙️
Complete setup instructions:
- Virtual environment setup
- Dependencies installation
- Environment configuration
- Running the server

### **03. [STRUCTURE.md](./03_STRUCTURE.md)** 🏗️
Project file structure and organization.

### **04. [MONGODB.md](./04_MONGODB.md)** 🍃
MongoDB collections for AI traces:
- `agent_traces` - Complete PPAR loop traces
- `market_data_cache` - Cached market data
- `agent_runs` - Autonomous pilot logs

### **05. [SUPABASE.md](./05_SUPABASE.md)** 📊
Supabase database layer:
- Query operations
- Model usage
- Connection management

### **06. [MULTI_AGENT_SYSTEM.md](./06_MULTI_AGENT_SYSTEM.md)** 🤖
Multi-agent architecture:
- 4 specialized AI agents
- Agent communication hub
- PPAR trading cycle
- Coordinator pattern

### **07. [GETTING_STARTED.md](./07_GETTING_STARTED.md)** 🚀
Quick start guide:
- Run autonomous trading locally
- Watch agents in action
- Development workflow

### **08. [AGENT_COMPETITION.md](./08_AGENT_COMPETITION.md)** 🏆
AI Agent Competition system:
- Competition coordinator
- Public API endpoints
- Scheduler integration
- Testing guide

### **09. [TROUBLESHOOTING.md](./09_TROUBLESHOOTING.md)** 🔧
Common issues and solutions.

---

## 🎯 Quick Navigation

| I want to... | Document |
|--------------|----------|
| **Set up from scratch** | [02_SETUP.md](./02_SETUP.md) |
| **Run autonomous trading** | [07_GETTING_STARTED.md](./07_GETTING_STARTED.md) |
| **Understand multi-agent system** | [06_MULTI_AGENT_SYSTEM.md](./06_MULTI_AGENT_SYSTEM.md) |
| **View competition system** | [08_AGENT_COMPETITION.md](./08_AGENT_COMPETITION.md) |
| **Fix issues** | [09_TROUBLESHOOTING.md](./09_TROUBLESHOOTING.md) |
| **View file structure** | [03_STRUCTURE.md](./03_STRUCTURE.md) |

---

## 📁 Project Structure

```
atlas-backend/
├── doc/                              # Documentation (you are here)
│   ├── 01_INDEX.md                  # This file
│   ├── 02_SETUP.md                  # Setup guide
│   ├── 03_STRUCTURE.md              # File structure
│   ├── 04_MONGODB.md                # MongoDB guide
│   ├── 05_SUPABASE.md               # Supabase guide
│   ├── 06_MULTI_AGENT_SYSTEM.md     # Multi-agent architecture
│   ├── 07_GETTING_STARTED.md        # Quick start
│   ├── 08_AGENT_COMPETITION.md      # Competition system
│   └── 09_TROUBLESHOOTING.md        # Troubleshooting
├── app/
│   ├── agents/                       # Multi-agent system
│   │   ├── market_analyst_agent.py
│   │   ├── risk_manager_agent.py
│   │   ├── portfolio_manager_agent.py
│   │   ├── execution_agent.py
│   │   ├── coordinator_agent.py
│   │   ├── communication_hub.py
│   │   ├── autonomous_pilot.py
│   │   └── competition_coordinator.py
│   ├── api/v1/                       # REST API endpoints
│   │   ├── agent.py
│   │   ├── orders.py
│   │   ├── portfolio.py
│   │   ├── trades.py
│   │   ├── traces.py
│   │   ├── jobs.py
│   │   └── competition.py           # Public competition API
│   ├── services/                     # Business logic
│   ├── db/                           # Database layers
│   │   ├── supabase/
│   │   └── mongodb/
│   ├── middleware/                   # Auth & middleware
│   └── scheduler/                    # APScheduler jobs
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env
# Edit .env with your credentials

# 3. Start server
uvicorn app.main:app --reload

# 4. Visit API docs
http://localhost:8000/docs
```

**Full guide:** [02_SETUP.md](./02_SETUP.md)

---

## 🤖 Multi-Agent System (Core Feature)

Atlas uses **6 specialized AI agents** that collaborate for autonomous trading:

1. **Market Analyst** 🔬 - Technical analysis and market sentiment
2. **Risk Manager** ⚖️ - Portfolio risk and position sizing
3. **Portfolio Manager** 💼 - Asset allocation and rebalancing
4. **Execution Agent** 🎯 - Final trading decisions
5. **Coordinator** 🎭 - Orchestration and conflict resolution
6. **Communication Hub** 📡 - Inter-agent messaging

**Deep dive:** [06_MULTI_AGENT_SYSTEM.md](./06_MULTI_AGENT_SYSTEM.md)

---

## 🏆 AI Agent Competition

4 Gemini models compete autonomously:
- Daily trading at 10am EST (Mon-Fri)
- Public API endpoints (no auth required)
- Full explainable AI transparency

**Details:** [08_AGENT_COMPETITION.md](./08_AGENT_COMPETITION.md)

---

## 📚 Related Documentation

- **Organization Docs:** [.github/doc/](../../.github/doc/) - System architecture, org-level guides
- **Database Docs:** [atlas-database/doc/](../../atlas-database/doc/) - Schema reference
- **Frontend Docs:** [atlas-frontend/doc/](../../atlas-frontend/doc/) - UI components

---

## 🎉 Key Features

✅ Multi-Agent AI System - 6 specialized agents  
✅ AI Trading Competition - 4 Gemini models competing  
✅ Autonomous Trading - Scheduled daily execution  
✅ Public APIs - Competition data accessible to all  
✅ Explainable AI - Full reasoning transparency  
✅ Production Ready - Robust error handling

---

**Ready to watch AI agents trade? Let's go! 🚀**

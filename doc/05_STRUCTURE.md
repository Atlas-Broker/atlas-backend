# 📁 Atlas Backend - Project Structure

```
atlas-backend/
├── 📄 README.md                 # Main documentation and API reference
├── 📄 .env.example              # Environment variables template
├── 📄 .gitignore                # Git ignore rules
├── 📄 requirements.txt          # Python dependencies
├── 📄 pyproject.toml            # Project config (Black, Ruff, MyPy)
├── 📄 Dockerfile                # Production Docker image
├── 📄 docker-compose.yml        # Local development environment
│
├── 📚 knowledge/                # Documentation files
│   ├── README.md                # Knowledge base index
│   ├── SETUP_GUIDE.md           # Step-by-step setup instructions
│   └── PROJECT_SUMMARY.md       # Complete overview and architecture
│
├── 🐍 app/                      # Main application code
│   ├── main.py                  # FastAPI entry point
│   ├── config.py                # Environment configuration
│   ├── dependencies.py          # Shared dependencies
│   │
│   ├── agents/                  # 🤖 Agent logic
│   │   ├── orchestrator.py      # Streaming agent (CRITICAL!)
│   │   ├── autonomous_pilot.py  # PPAR loop
│   │   ├── tools.py             # Tool definitions
│   │   └── prompts.py           # System prompts
│   │
│   ├── api/v1/                  # 📡 API endpoints
│   │   ├── router.py            # Main v1 router
│   │   ├── agent.py             # Streaming analysis
│   │   ├── orders.py            # Order management
│   │   ├── portfolio.py         # Portfolio & equity curve
│   │   ├── trades.py            # Trade history
│   │   ├── traces.py            # Agent traces
│   │   └── jobs.py              # Admin jobs
│   │
│   ├── services/                # 💼 Business logic
│   │   ├── market_data.py       # Yahoo Finance + caching
│   │   ├── indicators.py        # Technical analysis
│   │   ├── portfolio.py         # Portfolio accounting
│   │   ├── order_execution.py   # Trade execution
│   │   └── reflection.py        # Post-trade analysis
│   │
│   ├── db/                      # 🗄️ Database layer
│   │   ├── supabase/            # PostgreSQL
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   ├── client.py        # Async connection
│   │   │   ├── queries.py       # Reusable queries
│   │   │   └── README.md        # Supabase docs
│   │   ├── mongodb/             # MongoDB
│   │   │   ├── models.py        # Pydantic models
│   │   │   ├── client.py        # Motor client
│   │   │   ├── queries.py       # Trace operations
│   │   │   └── README.md        # MongoDB docs
│   │   └── s3/                  # S3 (future)
│   │       ├── client.py        # S3 client
│   │       └── README.md        # S3 docs
│   │
│   ├── middleware/              # 🛡️ Middleware
│   │   ├── auth.py              # Clerk JWT verification
│   │   ├── logging.py           # Request logging
│   │   └── error_handling.py    # Error handlers
│   │
│   ├── scheduler/               # ⏰ Background jobs
│   │   ├── scheduler.py         # APScheduler setup
│   │   └── jobs.py              # Job definitions
│   │
│   ├── schemas/                 # 📋 Pydantic schemas
│   │   ├── agent.py             # Agent models
│   │   ├── orders.py            # Order models
│   │   ├── portfolio.py         # Portfolio models
│   │   └── traces.py            # Trace models
│   │
│   └── utils/                   # 🔧 Utilities
│       ├── logging.py           # Loguru setup
│       ├── streaming.py         # SSE helpers
│       └── validators.py        # Input validation
│
├── 🗃️ migrations/               # Database migrations
│   └── supabase/
│       ├── 001_paper_trading.sql # Schema definition
│       └── README.md            # Migration docs
│
├── 📜 scripts/                  # Utility scripts
│   ├── seed_db.py               # Seed test data
│   └── run_pilot.py             # Manual pilot trigger
│
└── 🧪 tests/                    # Test suite
    ├── conftest.py              # Pytest fixtures
    ├── test_api/
    ├── test_agents/
    └── test_services/
```

## 📊 Statistics

- **Total Files**: ~80 files
- **Lines of Code**: ~6,000 LOC
- **API Endpoints**: 12 endpoints
- **Database Tables**: 4 tables (Supabase)
- **MongoDB Collections**: 2 collections
- **Agent Tools**: 3 tools

## 🎯 Key Directories

| Directory | Purpose |
|-----------|---------|
| `app/agents/` | Agent orchestration and autonomous pilot |
| `app/api/v1/` | RESTful API endpoints with streaming |
| `app/services/` | Business logic (market data, portfolio, etc.) |
| `app/db/` | Database clients and models |
| `knowledge/` | Documentation and guides |
| `migrations/` | Database schema definitions |
| `scripts/` | Utility scripts for seeding and testing |

## 🚀 Getting Started

1. Read **[README.md](./README.md)** for overview
2. Follow **[knowledge/SETUP_GUIDE.md](./knowledge/SETUP_GUIDE.md)** for setup
3. Review **[knowledge/PROJECT_SUMMARY.md](./knowledge/PROJECT_SUMMARY.md)** for architecture

## 🔗 Quick Links

- **Main README**: [README.md](./README.md)
- **Setup Guide**: [knowledge/SETUP_GUIDE.md](./knowledge/SETUP_GUIDE.md)
- **Project Summary**: [knowledge/PROJECT_SUMMARY.md](./knowledge/PROJECT_SUMMARY.md)
- **API Docs**: http://localhost:8000/docs (when server running)

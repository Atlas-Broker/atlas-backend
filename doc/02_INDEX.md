# 📚 Atlas Backend - Documentation Index

**Last Updated**: January 27, 2026  
**Version**: 2.0 - Multi-Agent System

Welcome to Atlas Backend documentation! This folder contains all technical documentation, guides, and references.

---

## 📖 Documentation Structure

### **Getting Started**

1. **[01_README.md](./01_README.md)** 📘
   - Main project README
   - Overview and architecture
   - Quick start guide
   
2. **[03_SETUP_GUIDE.md](./03_SETUP_GUIDE.md)** ⚙️
   - Complete setup instructions
   - Database configuration
   - Environment setup
   
3. **[12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)** 🚀
   - Quick start for autonomous trading
   - Run multi-agent system locally
   - Watch agents in action

---

### **Architecture & Design**

4. **[04_PROJECT_SUMMARY.md](./04_PROJECT_SUMMARY.md)** 📋
   - High-level project overview
   - What was built
   - Features and capabilities
   
5. **[06_STRUCTURE.md](./06_STRUCTURE.md)** 🏗️
   - Project file structure
   - Directory organization
   
6. **[11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md)** 🤖
   - **Multi-agent architecture**
   - 4 specialized AI agents
   - Agent communication
   - Trading cycle workflow

---

### **Configuration & Setup**

7. **[05_ENV_TEMPLATE.md](./05_ENV_TEMPLATE.md)** 🔐
   - Environment variables guide
   - Configuration options
   - API keys and credentials

---

### **Database Documentation**

8. **[07_SUPABASE_MIGRATIONS.md](./07_SUPABASE_MIGRATIONS.md)** 🗄️
   - Supabase SQL migrations
   - Schema overview
   
9. **[08_MONGODB.md](./08_MONGODB.md)** 🍃
   - MongoDB collections
   - Agent trace storage
   
10. **[09_SUPABASE_DB.md](./09_SUPABASE_DB.md)** 📊
    - Supabase database layer
    - Query operations
    
11. **[10_S3_STORAGE.md](./10_S3_STORAGE.md)** ☁️
    - S3 storage (future)
    - Artifact storage
    
12. **[13_TROUBLESHOOTING.md](./13_TROUBLESHOOTING.md)** 🔧
    - Common issues and solutions
    - Debugging guide

---

## 🎯 Quick Reference

### **I want to...**

| Goal | Document |
|------|----------|
| Get project overview | [01_README.md](./01_README.md) |
| Set up from scratch | [03_SETUP_GUIDE.md](./03_SETUP_GUIDE.md) |
| **Run autonomous trading** | [12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md) ⭐ |
| **Understand multi-agent system** | [11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md) ⭐ |
| Configure environment | [05_ENV_TEMPLATE.md](./05_ENV_TEMPLATE.md) |
| Setup database | [07_SUPABASE_MIGRATIONS.md](./07_SUPABASE_MIGRATIONS.md) |
| View project structure | [06_STRUCTURE.md](./06_STRUCTURE.md) |
| Troubleshooting | [13_TROUBLESHOOTING.md](./13_TROUBLESHOOTING.md) |

---

## 🔥 Most Important Docs

### **For New Users:**
1. **[01_README.md](./01_README.md)** - Start here!
2. **[03_SETUP_GUIDE.md](./03_SETUP_GUIDE.md)** - Setup instructions
3. **[12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)** - Run autonomous trading

### **For Understanding Multi-Agent System:**
1. **[11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md)** - Complete architecture guide ⭐
2. **[12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)** - See it in action

### **For Development:**
1. **[04_PROJECT_SUMMARY.md](./04_PROJECT_SUMMARY.md)** - What's been built
2. **[06_STRUCTURE.md](./06_STRUCTURE.md)** - File organization
3. **[08_MONGODB.md](./08_MONGODB.md)** - Agent traces

---

## 🤖 Multi-Agent System (NEW!)

Atlas now uses **4 specialized AI agents** that collaborate for autonomous trading:

1. **Market Analyst** 🔬 - Market data and technical analysis
2. **Risk Manager** ⚖️ - Risk evaluation and position sizing
3. **Portfolio Manager** 💼 - Portfolio state and constraints
4. **Execution Agent** 🎯 - Final trading decisions

**See**: [11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Start server
uvicorn app.main:app --reload

# 4. Visit
# http://localhost:8000/docs
```

**Full guide**: [12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)

---

## 📁 Project Structure

```
atlas-backend/
├── doc/                    # 📚 You are here
│   ├── 01_README.md       # Main README
│   ├── 02_INDEX.md        # This file
│   ├── 03-10_*.md         # Setup & database docs
│   ├── 11_MULTI_AGENT_SYSTEM.md        # Multi-agent guide
│   ├── 12_GETTING_STARTED_AUTONOMOUS.md # Quick start
│   └── 13_TROUBLESHOOTING.md           # Troubleshooting
├── app/
│   ├── agents/            # 🤖 Multi-agent system
│   ├── api/               # 📡 REST endpoints
│   ├── services/          # 💼 Business logic
│   └── db/                # 🗄️ Database layers
├── migrations/            # SQL migrations
├── scripts/               # Utility scripts
└── tests/                 # Test suite
```

---

## 🎓 Learning Path

### **Day 1: Setup**
1. Read [01_README.md](./01_README.md)
2. Follow [03_SETUP_GUIDE.md](./03_SETUP_GUIDE.md)
3. Get server running

### **Day 2: Multi-Agent System**
1. Read [11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md)
2. Follow [12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)
3. Run autonomous pilot
4. Watch agents collaborate!

### **Day 3: Customization**
1. Modify watchlist
2. Adjust risk parameters
3. Tune agent prompts
4. Review MongoDB traces

---

## 📞 Need Help?

- **Multi-agent system?** → [11_MULTI_AGENT_SYSTEM.md](./11_MULTI_AGENT_SYSTEM.md)
- **Setup issues?** → [03_SETUP_GUIDE.md](./03_SETUP_GUIDE.md) or [13_TROUBLESHOOTING.md](./13_TROUBLESHOOTING.md)
- **Quick start?** → [12_GETTING_STARTED_AUTONOMOUS.md](./12_GETTING_STARTED_AUTONOMOUS.md)
- **API reference?** → http://localhost:8000/docs

---

## 🎉 Key Features

✅ **Multi-Agent System** - 4 specialized AI agents  
✅ **Agent Communication Hub** - Transparent collaboration  
✅ **Enhanced Logging** - Beautiful emoji-based logs  
✅ **Complete Observability** - Full agent communication traces  
✅ **Production Ready** - Robust error handling  
✅ **Comprehensive Docs** - 13 detailed guides

---

**Ready to watch AI agents trade autonomously? Let's go! 🚀**

# 📚 Atlas Backend - Documentation Index

**Last Updated**: January 27, 2026  
**Version**: 2.0 - Multi-Agent System

Welcome to Atlas Backend documentation! This folder contains all technical documentation, guides, and references.

---

## 📖 Documentation Structure

### **Getting Started**

1. **[00_README.md](./00_README.md)** 📘
   - Main project README
   - Overview and architecture
   - Quick start guide
   
2. **[02_SETUP_GUIDE.md](./02_SETUP_GUIDE.md)** ⚙️
   - Complete setup instructions
   - Database configuration
   - Environment setup
   
3. **[11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)** 🚀 **NEW!**
   - Quick start for autonomous trading
   - Run multi-agent system locally
   - Watch agents in action

---

### **Architecture & Design**

4. **[03_PROJECT_SUMMARY.md](./03_PROJECT_SUMMARY.md)** 📋
   - High-level project overview
   - What was built
   - Features and capabilities
   
5. **[05_STRUCTURE.md](./05_STRUCTURE.md)** 🏗️
   - Project file structure
   - Directory organization
   
6. **[10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md)** 🤖 **NEW!**
   - **Multi-agent architecture**
   - 4 specialized AI agents
   - Agent communication
   - Trading cycle workflow

---

### **Configuration & Setup**

7. **[04_ENV_TEMPLATE.md](./04_ENV_TEMPLATE.md)** 🔐
   - Environment variables guide
   - Configuration options
   - API keys and credentials

---

### **Database Documentation**

8. **[06_SUPABASE_MIGRATIONS.md](./06_SUPABASE_MIGRATIONS.md)** 🗄️
   - Supabase SQL migrations
   - Schema overview
   
9. **[07_MONGODB.md](./07_MONGODB.md)** 🍃
   - MongoDB collections
   - Agent trace storage
   
10. **[08_SUPABASE_DB.md](./08_SUPABASE_DB.md)** 📊
    - Supabase database layer
    - Query operations
    
11. **[09_S3_STORAGE.md](./09_S3_STORAGE.md)** ☁️
    - S3 storage (future)
    - Artifact storage

---

## 🎯 Quick Reference

### **I want to...**

| Goal | Document |
|------|----------|
| Get project overview | [00_README.md](./00_README.md) |
| Set up from scratch | [02_SETUP_GUIDE.md](./02_SETUP_GUIDE.md) |
| **Run autonomous trading** | [11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md) ⭐ |
| **Understand multi-agent system** | [10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md) ⭐ |
| Configure environment | [04_ENV_TEMPLATE.md](./04_ENV_TEMPLATE.md) |
| Setup database | [06_SUPABASE_MIGRATIONS.md](./06_SUPABASE_MIGRATIONS.md) |
| View project structure | [05_STRUCTURE.md](./05_STRUCTURE.md) |

---

## 🔥 Most Important Docs

### **For New Users:**
1. **[00_README.md](./00_README.md)** - Start here!
2. **[02_SETUP_GUIDE.md](./02_SETUP_GUIDE.md)** - Setup instructions
3. **[11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)** - Run autonomous trading

### **For Understanding Multi-Agent System:**
1. **[10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md)** - Complete architecture guide ⭐
2. **[11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)** - See it in action

### **For Development:**
1. **[03_PROJECT_SUMMARY.md](./03_PROJECT_SUMMARY.md)** - What's been built
2. **[05_STRUCTURE.md](./05_STRUCTURE.md)** - File organization
3. **[07_MONGODB.md](./07_MONGODB.md)** - Agent traces

---

## 🤖 Multi-Agent System (NEW!)

Atlas now uses **4 specialized AI agents** that collaborate for autonomous trading:

1. **Market Analyst** 🔬 - Market data and technical analysis
2. **Risk Manager** ⚖️ - Risk evaluation and position sizing
3. **Portfolio Manager** 💼 - Portfolio state and constraints
4. **Execution Agent** 🎯 - Final trading decisions

**See**: [10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md)

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

**Full guide**: [11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)

---

## 📁 Project Structure

```
atlas-backend/
├── doc/                    # 📚 You are here
│   ├── 00_README.md       # Main README
│   ├── 01_INDEX.md        # This file
│   ├── 02-09_*.md         # Setup & database docs
│   ├── 10_MULTI_AGENT_SYSTEM.md        # 🆕 Multi-agent guide
│   └── 11_GETTING_STARTED_AUTONOMOUS.md # 🆕 Quick start
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
1. Read [00_README.md](./00_README.md)
2. Follow [02_SETUP_GUIDE.md](./02_SETUP_GUIDE.md)
3. Get server running

### **Day 2: Multi-Agent System**
1. Read [10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md)
2. Follow [11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)
3. Run autonomous pilot
4. Watch agents collaborate!

### **Day 3: Customization**
1. Modify watchlist
2. Adjust risk parameters
3. Tune agent prompts
4. Review MongoDB traces

---

## 📞 Need Help?

- **Multi-agent system?** → [10_MULTI_AGENT_SYSTEM.md](./10_MULTI_AGENT_SYSTEM.md)
- **Setup issues?** → [02_SETUP_GUIDE.md](./02_SETUP_GUIDE.md)
- **Quick start?** → [11_GETTING_STARTED_AUTONOMOUS.md](./11_GETTING_STARTED_AUTONOMOUS.md)
- **API reference?** → http://localhost:8000/docs

---

## 🎉 What's New in v2.0

✅ **Multi-Agent System** - 4 specialized AI agents  
✅ **Agent Communication Hub** - Transparent collaboration  
✅ **Enhanced Logging** - Beautiful emoji-based logs  
✅ **Complete Observability** - Full agent communication traces  
✅ **Production Ready** - Robust error handling  
✅ **Comprehensive Docs** - 2 new detailed guides  

See [REFURBISHMENT_SUMMARY.md](../REFURBISHMENT_SUMMARY.md) for complete changelog.

---

**Ready to watch AI agents trade autonomously? Let's go! 🚀**

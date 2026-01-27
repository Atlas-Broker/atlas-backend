# Troubleshooting Guide

## Common Issues and Solutions

---

## 1. Motor/PyMongo Import Error ✅ FIXED

**Error**:
```
ImportError: cannot import name '_QUERY_OPTIONS' from 'pymongo.cursor'
```

**Cause**: Incompatible versions of `motor` and `pymongo`.

**Solution**:
```bash
# Uninstall old versions
pip uninstall pymongo motor -y

# Install compatible versions
pip install "pymongo>=4.5,<5.0" motor==3.5.2
```

**Fixed in requirements.txt**:
```
pymongo>=4.5,<5.0
motor==3.5.2
```

---

## 2. Server Won't Start

**Symptoms**:
- Server crashes on startup
- Import errors
- Module not found errors

**Solutions**:

### Check Python Version
```bash
python --version  # Should be 3.11+
```

### Reinstall Dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

### Check .env File
```bash
# Ensure .env exists
ls .env  # or dir .env on Windows

# Verify all required variables are set
cat .env  # or type .env on Windows
```

### Verify Database Connections
```bash
# Test MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('your_mongodb_uri').server_info())"

# Test Supabase connection
# (Check in Supabase dashboard)
```

---

## 3. Google AI API Errors

**Error**:
```
google.api_core.exceptions.PermissionDenied: 403
```

**Solutions**:

1. **Verify API Key**:
   ```bash
   # Check .env
   GOOGLE_AI_API_KEY=AIzaSy...
   ```

2. **Check API Quota**:
   - Visit: https://aistudio.google.com/apikey
   - Verify quota limits
   - Check billing status

3. **Enable API**:
   - Go to Google AI Studio
   - Enable Gemini API
   - Wait a few minutes for activation

---

## 4. No Trades Executing

**Symptoms**:
- Agent runs but no trades execute
- All decisions are HOLD
- Risk Manager rejecting all trades

**Check**:

1. **Portfolio State**:
   ```bash
   curl http://localhost:8000/api/v1/portfolio/summary
   ```
   - Verify sufficient cash
   - Check position count

2. **Watchlist Symbols**:
   - Ensure symbols are valid US stocks
   - Check Yahoo Finance availability

3. **Risk Parameters** (in .env):
   ```bash
   PAPER_MAX_POSITIONS=10
   PAPER_MAX_POSITION_SIZE=10000
   ```

4. **Market Hours**:
   - Yahoo Finance data best during market hours
   - Some symbols may have no data after-hours

---

## 5. MongoDB Connection Errors

**Error**:
```
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions**:

1. **Check MongoDB URI**:
   ```bash
   # In .env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

2. **IP Whitelist**:
   - Go to MongoDB Atlas
   - Network Access
   - Add your IP address (or 0.0.0.0/0 for testing)

3. **Database Name**:
   ```bash
   # In .env
   MONGODB_DB_NAME=atlas_production
   ```

4. **Test Connection**:
   ```bash
   python -c "from motor.motor_asyncio import AsyncIOMotorClient; client = AsyncIOMotorClient('YOUR_URI'); print('Connected!')"
   ```

---

## 6. Supabase Connection Errors

**Error**:
```
asyncpg.exceptions.InvalidPasswordError
```

**Solutions**:

1. **Check DATABASE_URL Format**:
   ```bash
   # Correct format
   DATABASE_URL=postgresql://postgres:PASSWORD@db.xxx.supabase.co:5432/postgres
   ```

2. **Verify Service Role Key**:
   ```bash
   # In .env
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   ```

3. **Run Migration**:
   - Supabase Dashboard → SQL Editor
   - Copy `migrations/supabase/001_paper_trading.sql`
   - Execute

4. **Check Project Status**:
   - Ensure Supabase project is active
   - Check billing status

---

## 7. Agent Reasoning Issues

**Symptoms**:
- Agent makes unexpected decisions
- Low confidence scores
- Constant HOLD decisions

**Debug**:

1. **View Agent Logs**:
   - Check console output
   - Look for agent emojis (🔬 ⚖️ 💼 🎯)

2. **Check MongoDB Traces**:
   ```bash
   curl http://localhost:8000/api/v1/traces/{run_id}
   ```
   - Review `agent_communication_log`
   - Check tool call results
   - Verify market data quality

3. **Adjust Agent Prompts**:
   - Edit `market_analyst_agent.py`
   - Edit `risk_manager_agent.py`
   - Edit `execution_agent.py`

4. **Check Market Data**:
   ```bash
   # Test Yahoo Finance
   python -c "import yfinance as yf; print(yf.Ticker('NVDA').info)"
   ```

---

## 8. High Memory/CPU Usage

**Solutions**:

1. **Reduce Watchlist Size**:
   ```python
   # In autonomous_pilot.py
   watchlist = ["NVDA", "AAPL"]  # Start small
   ```

2. **Increase Cache TTL**:
   - Market data cached for 15 minutes
   - Reduces API calls

3. **Disable Scheduler** (for testing):
   ```python
   # In app/main.py
   # start_scheduler()  # Comment out
   ```

4. **Monitor Resources**:
   ```bash
   # Check process
   ps aux | grep uvicorn  # Linux/Mac
   tasklist | findstr python  # Windows
   ```

---

## 9. Scheduled Jobs Not Running

**Symptoms**:
- Pilot doesn't run automatically
- No scheduled trades

**Check**:

1. **Scheduler Enabled**:
   ```python
   # In app/main.py
   start_scheduler()  # Should be uncommented
   ```

2. **Schedule Configuration**:
   ```python
   # In app/scheduler/scheduler.py
   # Check trigger times
   ```

3. **Logs**:
   - Look for "Starting autonomous pilot"
   - Check for errors in logs

4. **Timezone**:
   - Scheduler uses UTC
   - Adjust for your timezone

---

## 10. CORS Errors (Frontend)

**Error**:
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solution**:

Add frontend URL to CORS_ORIGINS in `.env`:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://your-frontend.com
```

---

## 11. Streaming Not Working

**Symptoms**:
- No real-time updates
- Events not received

**Solutions**:

1. **Check SSE Headers**:
   - Server sends `text/event-stream`
   - Client uses `EventSource` API

2. **Test with curl**:
   ```bash
   curl -N http://localhost:8000/api/v1/agent/analyze \
     -H "Content-Type: application/json" \
     -d '{"intent": "Should I buy NVDA?"}'
   ```

3. **Check Nginx** (production):
   ```nginx
   proxy_set_header X-Accel-Buffering no;
   proxy_buffering off;
   ```

---

## 12. Package Installation Fails

**Error**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:

1. **Upgrade pip**:
   ```bash
   python -m pip install --upgrade pip
   ```

2. **Clear cache**:
   ```bash
   pip cache purge
   ```

3. **Install from requirements**:
   ```bash
   pip install -r requirements.txt --no-cache-dir
   ```

4. **Check Python version**:
   ```bash
   python --version  # Must be 3.11+
   ```

---

## Quick Diagnostics

Run this to check your setup:

```bash
# 1. Check Python version
python --version

# 2. Check packages
pip list | grep -E "(motor|pymongo|fastapi|google)"

# 3. Test server
curl http://localhost:8000/health

# 4. Check databases
# MongoDB
python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('Motor OK')"

# 5. Check .env
cat .env | grep -v "^#" | grep "="
```

---

## Getting Help

If you're still stuck:

1. **Check Logs**:
   - Console output
   - `logs/` directory (production)

2. **View Documentation**:
   - `doc/10_MULTI_AGENT_SYSTEM.md`
   - `doc/11_GETTING_STARTED_AUTONOMOUS.md`

3. **Test Endpoints**:
   - http://localhost:8000/docs
   - Interactive API testing

4. **Review Traces**:
   ```bash
   curl http://localhost:8000/api/v1/traces
   ```

---

## Preventive Measures

### Before Each Run

- ✅ Check .env file exists and is complete
- ✅ Verify MongoDB and Supabase are accessible
- ✅ Ensure sufficient portfolio cash
- ✅ Validate watchlist symbols

### Production Deployment

- ✅ Use environment variables (not .env file)
- ✅ Enable logging to files
- ✅ Setup monitoring (CloudWatch, DataDog)
- ✅ Configure health checks
- ✅ Setup alerts for errors

---

## Success Checklist

Your setup is correct when:

- ✅ Server starts without errors
- ✅ `/health` endpoint returns 200
- ✅ `/docs` loads Swagger UI
- ✅ Pilot runs successfully
- ✅ All 4 agents log activity
- ✅ Trades appear in Supabase
- ✅ Traces saved to MongoDB

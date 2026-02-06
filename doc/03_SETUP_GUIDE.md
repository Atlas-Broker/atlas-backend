# Atlas Backend Setup Guide

Complete step-by-step setup instructions for the Atlas Intelligence API.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.11 or higher installed
- [ ] Git installed
- [ ] A Supabase account (free tier is fine)
- [ ] A MongoDB Atlas account (free tier is fine) OR Docker for local MongoDB
- [ ] A Google Cloud account with AI API enabled
- [ ] A Clerk account for authentication
- [ ] A code editor (VS Code recommended)

---

## 🛠️ Step-by-Step Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd atlas-backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Set Up Supabase (PostgreSQL)

#### Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Choose organization and region
4. Set a database password (save this!)
5. Wait for project to initialize (~2 minutes)

#### Run Database Migration

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `migrations/supabase/001_paper_trading.sql`
4. Paste and click **Run**
5. Verify tables were created (check **Table Editor**)

#### Get Connection Details

1. Go to **Settings** → **Database**
2. Copy **Connection String** (URI format)
3. Replace `[YOUR-PASSWORD]` with your database password
4. Add `+asyncpg` before `://` (e.g., `postgresql+asyncpg://...`)
5. Save this for `.env` file

#### Get API Keys

1. Go to **Settings** → **API**
2. Copy **service_role** key (starts with `eyJ...`)
3. Copy **URL** (https://xxx.supabase.co)
4. Save both for `.env` file

### 5. Set Up MongoDB

#### Option A: MongoDB Atlas (Cloud - Recommended)

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster (M0 tier)
3. Create database user:
   - Username: `atlas_user`
   - Password: (generate strong password)
4. Whitelist IP: `0.0.0.0/0` (for development)
5. Click **Connect** → **Connect your application**
6. Copy connection string
7. Replace `<password>` with your database password
8. Save for `.env` file

#### Option B: Local MongoDB (Docker)

```bash
# Start MongoDB container
docker-compose up mongodb -d

# Connection string for .env:
MONGODB_URI=mongodb://admin:password@localhost:27017/atlas_development?authSource=admin
```

### 6. Set Up Google AI (Gemini)

1. Go to [ai.google.dev](https://ai.google.dev)
2. Click **Get API Key**
3. Create or select a Google Cloud project
4. Click **Create API Key**
5. Copy the key (starts with `AIza...`)
6. Save for `.env` file

### 7. Set Up Clerk (Authentication)

1. Go to [clerk.com](https://clerk.com)
2. Create account and organization
3. Create new application
4. Choose authentication methods (Email, Google, etc.)
5. Go to **API Keys**
6. Copy **Secret Key** (starts with `sk_live_...` or `sk_test_...`)
7. Copy **Publishable Key** (starts with `pk_live_...` or `pk_test_...`)
8. Save both for `.env` file

### 8. Configure Environment Variables

Copy the example env file:
```bash
cp .env.example .env
```

Edit `.env` and fill in all values:

```bash
# Update these with your actual values:
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DATABASE_URL=postgresql+asyncpg://postgres:password@...

MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/atlas_production
MONGODB_DB_NAME=atlas_production

GOOGLE_AI_API_KEY=AIzaSy...

CLERK_SECRET_KEY=sk_live_...
CLERK_PUBLISHABLE_KEY=pk_live_...
```

**Important:** Never commit `.env` to git!

### 9. Verify Setup

Run the health check script:

```bash
python -c "from app.config import settings; print('✅ Config loaded successfully')"
```

If no errors, configuration is correct!

### 10. Seed Test Data (Optional)

```bash
python scripts/seed_db.py
```

This creates:
- Pilot account in Supabase
- Sample orders
- Test agent runs in MongoDB

---

## 🚀 Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --log-level debug
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker Compose (Recommended)

```bash
docker-compose up
```

This starts:
- FastAPI backend on port 8000
- MongoDB on port 27017

---

## ✅ Verification Steps

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "environment": "development",
  "streaming_enabled": true
}
```

### 2. Check Swagger Docs

Open browser to: http://localhost:8000/docs

You should see interactive API documentation.

### 3. Test Streaming (Optional)

Use Postman or curl:

```bash
curl -X POST http://localhost:8000/api/v1/agent/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-clerk-token>" \
  -d '{"intent": "Should I buy NVDA?"}' \
  --no-buffer
```

Should see streaming SSE events!

### 4. Run Manual Pilot (Optional)

```bash
python scripts/run_pilot.py
```

Should execute autonomous trading loop.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'app'"

**Solution:** Make sure you're in the project root and virtual environment is activated.

```bash
# Activate venv first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Then run from project root
uvicorn app.main:app --reload
```

### "Connection refused" for MongoDB

**Solution:** 

- Check MongoDB is running: `docker ps` (if using Docker)
- Verify connection string in `.env`
- For Atlas: Check IP whitelist

### "Invalid Google AI API key"

**Solution:**

- Verify key in Google AI Studio
- Check key is not expired
- Ensure Gemini API is enabled in your project

### "Supabase connection failed"

**Solution:**

- Verify connection string format: `postgresql+asyncpg://...`
- Check database password is correct
- Ensure database is not paused (Supabase free tier)

### Streaming not working

**Solution:**

- Check CORS settings in `.env`
- Verify client supports SSE (EventSource API)
- Test with Postman which has native SSE support

---

## 📚 Next Steps

1. **Frontend Integration**: Connect your Next.js frontend
2. **Authentication**: Set up Clerk in your frontend
3. **Customization**: 
   - Modify watchlist in `autonomous_pilot.py`
   - Adjust system prompts in `agents/prompts.py`
   - Configure trading parameters in `.env`
4. **Deployment**: See README.md for AWS App Runner deployment

---

## 🆘 Getting Help

If you encounter issues:

1. Check logs: `tail -f logs/*.log` (if in production)
2. Enable debug logging: Set `LOG_LEVEL=DEBUG` in `.env`
3. Verify all environment variables are set
4. Check database connections
5. Review Supabase logs and MongoDB logs

---

## ✨ You're Ready!

Your Atlas Backend should now be running successfully. Time to build something amazing! 🚀

# Environment Variables Template

Copy this content to create your `.env` file in the project root.

```bash
# Environment
ENVIRONMENT=development

# Server
HOST=0.0.0.0
PORT=8000

# CORS (Next.js frontend)
ALLOWED_ORIGINS=http://localhost:3000

# Clerk Authentication
CLERK_SECRET_KEY=your_clerk_secret_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here

# Supabase (PostgreSQL)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
DATABASE_URL=postgresql+asyncpg://postgres:your_password@db.your-project.supabase.co:5432/postgres

# MongoDB
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/atlas_production
MONGODB_DB_NAME=atlas_production

# S3 (AWS) - Optional
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=atlas-artifacts

# Google AI (Gemini)
GOOGLE_AI_API_KEY=your_google_ai_api_key_here

# Yahoo Finance Rate Limiting
YAHOO_RATE_LIMIT_CALLS=100
YAHOO_RATE_LIMIT_PERIOD=3600

# Paper Trading Config
PAPER_STARTING_CASH=100000.00
PAPER_MAX_POSITIONS=10
PAPER_MAX_POSITION_SIZE=10000.00

# Autonomous Pilot Schedule (cron format)
PILOT_SCHEDULE_CRON=0 9,15 * * 1-5

# Logging
LOG_LEVEL=INFO
```

## 🔑 Required Variables

The following variables **must** be set for the backend to work:

### Essential
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `DATABASE_URL` - PostgreSQL connection string (must include `+asyncpg`)
- `MONGODB_URI` - MongoDB connection string
- `GOOGLE_AI_API_KEY` - Google AI (Gemini) API key
- `CLERK_SECRET_KEY` - Clerk authentication secret key

### Optional (have defaults)
- `CLERK_PUBLISHABLE_KEY` - Clerk publishable key (for frontend)
- `AWS_ACCESS_KEY_ID` - AWS access key (only if using S3)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (only if using S3)
- All other variables have sensible defaults

## 📝 Setup Instructions

1. **Create `.env` file** in project root:
   ```bash
   # Copy this template
   cp knowledge/ENV_TEMPLATE.md .env
   
   # Or create manually
   touch .env
   ```

2. **Fill in your credentials**:
   - Get Supabase keys from your Supabase dashboard
   - Get MongoDB URI from MongoDB Atlas
   - Get Google AI key from [ai.google.dev](https://ai.google.dev)
   - Get Clerk keys from [clerk.com](https://clerk.com)

3. **Verify format**:
   - `DATABASE_URL` must include `+asyncpg` (e.g., `postgresql+asyncpg://...`)
   - No quotes around values
   - No spaces around `=`

## ⚠️ Security

**NEVER commit `.env` to git!**

The `.env` file is already in `.gitignore` to prevent accidental commits.

## 🔗 Related Docs

- [SETUP_GUIDE.md](./SETUP_GUIDE.md) - Complete setup instructions
- [README.md](../README.md) - Main documentation

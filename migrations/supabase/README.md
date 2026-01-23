# Supabase Migrations

## Overview

SQL migration files for Supabase PostgreSQL database.

## Running Migrations

### Via Supabase Dashboard

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy contents of `001_paper_trading.sql`
4. Execute the SQL

### Via Supabase CLI

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link project
supabase link --project-ref YOUR_PROJECT_REF

# Run migration
supabase db push
```

## Migrations

- **001_paper_trading.sql** - Core paper trading schema (accounts, orders, positions, equity snapshots)

## Schema Design

### Tables

1. **paper_accounts** - User and pilot trading accounts
2. **paper_orders** - Orders with approval workflow (PROPOSED → APPROVED → FILLED)
3. **paper_positions** - Current holdings per account
4. **equity_snapshots** - Time series data for equity curve

### Key Features

- Automatic `updated_at` timestamps via triggers
- Cascading deletes for data integrity
- Indexes for query performance
- Enum type for order status validation

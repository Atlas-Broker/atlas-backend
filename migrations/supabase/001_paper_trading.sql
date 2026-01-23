-- Atlas Backend - Paper Trading Schema
-- Run this in your Supabase SQL editor

-- Paper trading accounts
CREATE TABLE IF NOT EXISTS paper_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT,  -- NULL for autonomous pilot
  cash_balance NUMERIC(12,2) DEFAULT 100000.00,
  starting_cash NUMERIC(12,2) DEFAULT 100000.00,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper orders
CREATE TYPE order_status AS ENUM (
  'proposed', 'approved', 'submitted', 'filled', 'rejected', 'cancelled'
);

CREATE TABLE IF NOT EXISTS paper_orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES paper_accounts(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL,  -- BUY, SELL
  quantity INTEGER NOT NULL,
  order_type TEXT DEFAULT 'market',
  status order_status DEFAULT 'proposed',
  filled_price NUMERIC(10,2),
  filled_at TIMESTAMPTZ,
  agent_run_id TEXT,  -- MongoDB link
  confidence_score NUMERIC(3,2),
  reasoning_summary TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Paper positions
CREATE TABLE IF NOT EXISTS paper_positions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES paper_accounts(id) ON DELETE CASCADE,
  symbol TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  avg_entry_price NUMERIC(10,2) NOT NULL,
  current_price NUMERIC(10,2),
  unrealized_pnl NUMERIC(10,2),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(account_id, symbol)
);

-- Equity snapshots (for equity curve)
CREATE TABLE IF NOT EXISTS equity_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES paper_accounts(id) ON DELETE CASCADE,
  equity NUMERIC(12,2) NOT NULL,
  cash NUMERIC(12,2) NOT NULL,
  positions_value NUMERIC(12,2) NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_orders_account ON paper_orders(account_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON paper_orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created ON paper_orders(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_agent_run ON paper_orders(agent_run_id);

CREATE INDEX IF NOT EXISTS idx_positions_account ON paper_positions(account_id);
CREATE INDEX IF NOT EXISTS idx_positions_symbol ON paper_positions(symbol);

CREATE INDEX IF NOT EXISTS idx_snapshots_account_time ON equity_snapshots(account_id, timestamp DESC);

-- Function to auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_paper_accounts_updated_at BEFORE UPDATE ON paper_accounts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paper_orders_updated_at BEFORE UPDATE ON paper_orders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_paper_positions_updated_at BEFORE UPDATE ON paper_positions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert autonomous pilot account
INSERT INTO paper_accounts (user_id, cash_balance, starting_cash)
VALUES (NULL, 100000.00, 100000.00)
ON CONFLICT DO NOTHING;

-- Create initial equity snapshot for pilot
INSERT INTO equity_snapshots (account_id, equity, cash, positions_value, timestamp)
SELECT id, cash_balance, cash_balance, 0, NOW()
FROM paper_accounts
WHERE user_id IS NULL
ON CONFLICT DO NOTHING;

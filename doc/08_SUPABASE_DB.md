# Supabase Database Layer

## Overview

This module handles PostgreSQL operations via Supabase using SQLAlchemy async.

## Schema

**Facts Storage** - Transactional data:

- `paper_accounts` - User and pilot trading accounts
- `paper_orders` - Trade orders with approval workflow
- `paper_positions` - Current holdings
- `equity_snapshots` - Portfolio value over time

## Usage

```python
from app.db.supabase.client import get_db
from app.db.supabase.queries import create_paper_order

async def example(session: AsyncSession = Depends(get_db)):
    order = await create_paper_order(
        session=session,
        account_id=account.id,
        symbol="NVDA",
        side="BUY",
        quantity=10,
        agent_run_id="trace-123"
    )
```

## Migrations

Run SQL migrations in `migrations/supabase/` via Supabase dashboard or CLI.

"""SQLAlchemy models for Supabase (PostgreSQL)."""

from sqlalchemy import Column, String, Numeric, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid


Base = declarative_base()


class OrderStatus(enum.Enum):
    """Paper order status enum."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class PaperAccount(Base):
    """Paper trading account."""

    __tablename__ = "paper_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)  # None for autonomous pilot
    cash_balance = Column(Numeric(12, 2), default=100000.00)
    starting_cash = Column(Numeric(12, 2), default=100000.00)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaperOrder(Base):
    """Paper trading order."""

    __tablename__ = "paper_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("paper_accounts.id"))
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    quantity = Column(Integer, nullable=False)
    order_type = Column(String, default="market")
    status = Column(Enum(OrderStatus), default=OrderStatus.PROPOSED)
    filled_price = Column(Numeric(10, 2))
    filled_at = Column(DateTime)
    agent_run_id = Column(String)  # Link to MongoDB trace
    confidence_score = Column(Numeric(3, 2))
    reasoning_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PaperPosition(Base):
    """Paper trading position (current holdings)."""

    __tablename__ = "paper_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("paper_accounts.id"))
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_entry_price = Column(Numeric(10, 2), nullable=False)
    current_price = Column(Numeric(10, 2))
    unrealized_pnl = Column(Numeric(10, 2))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EquitySnapshot(Base):
    """Historical equity snapshots for equity curve."""

    __tablename__ = "equity_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("paper_accounts.id"))
    equity = Column(Numeric(12, 2), nullable=False)
    cash = Column(Numeric(12, 2), nullable=False)
    positions_value = Column(Numeric(12, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

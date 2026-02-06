"""SQLAlchemy models for Supabase (PostgreSQL) - Unified Schema."""

from sqlalchemy import Column, String, Numeric, Integer, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from datetime import datetime
import enum
import uuid


Base = declarative_base()


# ============================================
# ENUMS (must match SQL schema exactly)
# ============================================


class UserRole(enum.Enum):
    """User role hierarchy."""
    TRADER = "trader"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    SYSTEM = "system"


class OrderSide(enum.Enum):
    """Order side types."""
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    COVER = "cover"


class OrderType(enum.Enum):
    """Order types."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderStatus(enum.Enum):
    """Order status lifecycle."""
    PROPOSED = "proposed"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"


class EnvironmentType(enum.Enum):
    """Trading environment."""
    PAPER = "paper"
    LIVE = "live"


# ============================================
# DATABASE MODELS (match unified schema)
# ============================================


class Profile(Base):
    """User profiles - supports both Clerk users and system accounts."""

    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String, unique=True, nullable=True)  # NULL for system accounts
    email = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.TRADER)
    is_active = Column(Boolean, nullable=False, default=True)
    is_system = Column(Boolean, nullable=False, default=False)  # True for autonomous pilot
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Account(Base):
    """Trading accounts - paper and live trading support."""

    __tablename__ = "accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    environment = Column(Enum(EnvironmentType), nullable=False, default=EnvironmentType.PAPER)
    cash_balance = Column(Numeric(15, 2), nullable=False, default=100000.00)
    starting_cash = Column(Numeric(15, 2), nullable=False, default=100000.00)
    total_equity = Column(Numeric(15, 2), nullable=False, default=100000.00)
    broker_account_id = Column(String, nullable=True)  # For live trading
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class TraderSettings(Base):
    """Risk and autonomy preferences per user."""

    __tablename__ = "trader_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False, unique=True)
    autonomy_level = Column(Integer, nullable=False, default=1)  # 0-3
    max_concurrent_positions = Column(Integer, nullable=False, default=5)
    max_daily_orders = Column(Integer, nullable=False, default=20)
    max_position_size_usd = Column(Numeric(12, 2), nullable=False, default=10000.00)
    allow_shorting = Column(Boolean, nullable=False, default=False)
    allow_margin = Column(Boolean, nullable=False, default=False)
    trading_hours = Column(String, nullable=False, default="regular")  # 'regular', 'extended', 'all'
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Watchlist(Base):
    """User-curated stock lists."""

    __tablename__ = "watchlists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False, default="My Watchlist")
    symbols = Column(ARRAY(String), nullable=False, default=[])
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Order(Base):
    """All orders - paper and live trading."""

    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)  # Denormalized
    symbol = Column(String, nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    order_type = Column(Enum(OrderType), nullable=False, default=OrderType.MARKET)
    limit_price = Column(Numeric(12, 2), nullable=True)
    stop_price = Column(Numeric(12, 2), nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PROPOSED)
    environment = Column(Enum(EnvironmentType), nullable=False, default=EnvironmentType.PAPER)

    # Execution details
    broker_order_id = Column(String, nullable=True)
    filled_price = Column(Numeric(12, 2), nullable=True)
    filled_quantity = Column(Integer, nullable=True)
    filled_at = Column(DateTime, nullable=True)

    # AI agent details
    agent_run_id = Column(String, nullable=True)  # Link to MongoDB agent_runs.run_id
    confidence_score = Column(Numeric(3, 2), nullable=True)
    reasoning_summary = Column(Text, nullable=True)
    agent_reasoning = Column(JSONB, nullable=True)  # Full reasoning object

    # Approval tracking
    approved_by = Column(UUID(as_uuid=True), ForeignKey("profiles.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    rejected_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Position(Base):
    """Current open positions across all accounts."""

    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)  # Denormalized
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_entry_price = Column(Numeric(12, 2), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=True)
    unrealized_pnl = Column(Numeric(12, 2), nullable=True)
    realized_pnl = Column(Numeric(12, 2), default=0.00)
    environment = Column(Enum(EnvironmentType), nullable=False, default=EnvironmentType.PAPER)
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class EquitySnapshot(Base):
    """Time series of portfolio equity for charts."""

    __tablename__ = "equity_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    cash = Column(Numeric(15, 2), nullable=False)
    positions_value = Column(Numeric(15, 2), nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class AuditLog(Base):
    """Full audit trail of all system actions."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(UUID(as_uuid=True), nullable=True)
    metadata = Column(JSONB, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================
# AGENT COMPETITION MODELS
# ============================================


class AgentCompetitor(Base):
    """AI models competing in live trading arena."""

    __tablename__ = "agent_competitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    model_id = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    initial_capital = Column(Numeric(15, 2), nullable=False, default=30000.00)
    current_equity = Column(Numeric(15, 2), nullable=False, default=30000.00)
    total_return = Column(Numeric(10, 4), default=0.0000)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    total_trades = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_trade_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentDailyPerformance(Base):
    """Daily performance snapshots for charting."""

    __tablename__ = "agent_daily_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    trading_date = Column(DateTime, nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    cash = Column(Numeric(15, 2), nullable=False)
    positions_value = Column(Numeric(15, 2), nullable=False)
    daily_return = Column(Numeric(10, 4), nullable=True)
    cumulative_return = Column(Numeric(10, 4), nullable=True)
    trades_today = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentPositionModel(Base):
    """Current holdings of each AI agent."""

    __tablename__ = "agent_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_entry_price = Column(Numeric(12, 2), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=True)
    unrealized_pnl = Column(Numeric(12, 2), nullable=True)
    cost_basis = Column(Numeric(15, 2), nullable=False)
    market_value = Column(Numeric(15, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentTrade(Base):
    """Complete trading history of all agents."""

    __tablename__ = "agent_trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    reasoning_summary = Column(Text, nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentReasoningModel(Base):
    """Detailed reasoning for explainable AI."""

    __tablename__ = "agent_reasoning"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("agent_trades.id", ondelete="CASCADE"), nullable=True)
    reasoning_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentLeaderboard(Base):
    """Daily rankings snapshot for historical comparison."""

    __tablename__ = "agent_leaderboard"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    ranking_date = Column(DateTime, nullable=False)
    rank = Column(Integer, nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    total_return = Column(Numeric(10, 4), nullable=False)
    daily_return = Column(Numeric(10, 4), nullable=True)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    total_trades = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================
# AGENT COMPETITION MODELS
# ============================================


class AgentCompetitor(Base):
    """AI models competing in live trading arena."""

    __tablename__ = "agent_competitors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    model_id = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    initial_capital = Column(Numeric(15, 2), nullable=False, default=30000.00)
    current_equity = Column(Numeric(15, 2), nullable=False, default=30000.00)
    total_return = Column(Numeric(10, 4), default=0.0000)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(10, 4), nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    total_trades = Column(Integer, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_trade_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentDailyPerformance(Base):
    """Daily performance snapshots for charting."""

    __tablename__ = "agent_daily_performance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    trading_date = Column(DateTime, nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    cash = Column(Numeric(15, 2), nullable=False)
    positions_value = Column(Numeric(15, 2), nullable=False)
    daily_return = Column(Numeric(10, 4), nullable=True)
    cumulative_return = Column(Numeric(10, 4), nullable=True)
    trades_today = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentPositionModel(Base):
    """Current holdings of each AI agent."""

    __tablename__ = "agent_positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    avg_entry_price = Column(Numeric(12, 2), nullable=False)
    current_price = Column(Numeric(12, 2), nullable=True)
    unrealized_pnl = Column(Numeric(12, 2), nullable=True)
    cost_basis = Column(Numeric(15, 2), nullable=False)
    market_value = Column(Numeric(15, 2), nullable=True)
    weight = Column(Numeric(5, 2), nullable=True)
    opened_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentTrade(Base):
    """Complete trading history of all agents."""

    __tablename__ = "agent_trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    reasoning_summary = Column(Text, nullable=True)
    confidence_score = Column(Numeric(3, 2), nullable=True)
    executed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentReasoningModel(Base):
    """Detailed reasoning for explainable AI."""

    __tablename__ = "agent_reasoning"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    trade_id = Column(UUID(as_uuid=True), ForeignKey("agent_trades.id", ondelete="CASCADE"), nullable=True)
    reasoning_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSONB, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class AgentLeaderboard(Base):
    """Daily rankings snapshot for historical comparison."""

    __tablename__ = "agent_leaderboard"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competitor_id = Column(UUID(as_uuid=True), ForeignKey("agent_competitors.id", ondelete="CASCADE"), nullable=False)
    ranking_date = Column(DateTime, nullable=False)
    rank = Column(Integer, nullable=False)
    equity = Column(Numeric(15, 2), nullable=False)
    total_return = Column(Numeric(10, 4), nullable=False)
    daily_return = Column(Numeric(10, 4), nullable=True)
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    win_rate = Column(Numeric(5, 2), nullable=True)
    total_trades = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

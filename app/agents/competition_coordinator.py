"""
Agent Competition Coordinator.

Manages 4 Gemini AI models competing in autonomous trading.
Each agent trades independently with $30,000 starting capital.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, date
from loguru import logger
import asyncio

from app.db.supabase.client import get_session
from app.db.supabase.models import (
    AgentCompetitor,
    AgentTrade,
    AgentPositionModel,
    AgentDailyPerformance,
    AgentReasoningModel,
    AgentLeaderboard,
    OrderSide,
)
from sqlalchemy import select, func
from app.services.market_data import get_stock_price
from app.agents.market_analyst_agent import MarketAnalystAgent
from app.agents.risk_manager_agent import RiskManagerAgent
from app.agents.portfolio_manager_agent import PortfolioManagerAgent
from app.agents.execution_agent import ExecutionAgent


class CompetitionAgent:
    """Single agent in the competition."""

    def __init__(self, competitor: AgentCompetitor, model_name: str):
        """
        Initialize competition agent.

        Args:
            competitor: Database competitor record
            model_name: Gemini model ID
        """
        self.competitor = competitor
        self.model_name = model_name
        self.cash = float(competitor.current_equity)
        self.positions: Dict[str, Dict[str, Any]] = {}

        # Initialize specialized agents with this model
        self.market_analyst = MarketAnalystAgent(model_name=model_name)
        self.risk_manager = RiskManagerAgent(model_name=model_name)
        self.portfolio_manager = PortfolioManagerAgent(model_name=model_name)
        self.execution_agent = ExecutionAgent(model_name=model_name)

        logger.info(f"🤖 Initialized {competitor.name} with model {model_name}")

    async def run_daily_trading(self, watchlist: List[str], session) -> Dict[str, Any]:
        """
        Execute daily trading cycle for this agent.

        Args:
            watchlist: List of stock symbols to analyze
            session: Database session

        Returns:
            Trading summary
        """
        logger.info(f"📊 {self.competitor.name} starting daily trading")

        trades_executed = []
        reasoning_records = []

        try:
            # 1. Market Analysis
            logger.info(f"🔬 {self.competitor.name}: Analyzing market")
            market_insights = await self.market_analyst.analyze_market(watchlist)

            # Store market analysis reasoning
            reasoning_records.append({
                "type": "market_analysis",
                "content": market_insights.get("analysis", "No analysis available"),
                "metadata": {"symbols": watchlist, "insights": market_insights},
            })

            # 2. Portfolio Status
            portfolio_state = {
                "cash": self.cash,
                "positions": self.positions,
                "total_equity": self.cash + sum(
                    pos.get("market_value", 0) for pos in self.positions.values()
                ),
            }

            # 3. Risk Assessment
            logger.info(f"⚖️ {self.competitor.name}: Assessing risk")
            risk_assessment = await self.risk_manager.evaluate_risk(
                portfolio_state, market_insights
            )

            reasoning_records.append({
                "type": "risk_assessment",
                "content": risk_assessment.get("assessment", "No assessment available"),
                "metadata": risk_assessment,
            })

            # 4. Generate Trading Decisions
            logger.info(f"🎯 {self.competitor.name}: Making decisions")
            decisions = await self.execution_agent.make_trading_decisions(
                market_insights, risk_assessment, portfolio_state
            )

            # 5. Execute Trades
            for decision in decisions.get("trades", []):
                try:
                    trade_result = await self._execute_trade(decision, session)
                    if trade_result:
                        trades_executed.append(trade_result)

                        # Store decision reasoning
                        reasoning_records.append({
                            "type": "decision",
                            "content": decision.get("reasoning", ""),
                            "metadata": decision,
                            "trade_id": trade_result["trade_id"],
                        })
                except Exception as e:
                    logger.error(f"❌ Trade execution failed: {e}")

            # 6. Save all reasoning to database
            await self._save_reasoning(reasoning_records, session)

            # 7. Update daily performance
            await self._update_daily_performance(session)

            logger.info(
                f"✅ {self.competitor.name} completed: {len(trades_executed)} trades"
            )

            return {
                "agent": self.competitor.name,
                "trades": len(trades_executed),
                "equity": self.cash
                + sum(pos.get("market_value", 0) for pos in self.positions.values()),
                "trade_details": trades_executed,
            }

        except Exception as e:
            logger.error(f"❌ {self.competitor.name} trading failed: {e}")
            return {"agent": self.competitor.name, "error": str(e)}

    async def _execute_trade(
        self, decision: Dict[str, Any], session
    ) -> Optional[Dict[str, Any]]:
        """Execute a single trade."""
        symbol = decision.get("symbol")
        side = decision.get("action", "").lower()  # buy/sell
        quantity = decision.get("quantity", 0)

        if not symbol or side not in ["buy", "sell"] or quantity <= 0:
            return None

        # Get current price
        price_data = await get_stock_price(symbol)
        if not price_data:
            logger.warning(f"⚠️ Could not get price for {symbol}")
            return None

        price = float(price_data.get("price", 0))
        total_amount = price * quantity

        # Check if we have enough cash for buy
        if side == "buy" and total_amount > self.cash:
            logger.warning(f"⚠️ Insufficient cash: ${self.cash:.2f} < ${total_amount:.2f}")
            return None

        # Check if we have enough shares for sell
        if side == "sell":
            current_qty = self.positions.get(symbol, {}).get("quantity", 0)
            if quantity > current_qty:
                logger.warning(f"⚠️ Insufficient shares: {current_qty} < {quantity}")
                return None

        # Execute trade
        if side == "buy":
            self.cash -= total_amount
            if symbol in self.positions:
                # Update existing position
                pos = self.positions[symbol]
                total_qty = pos["quantity"] + quantity
                total_cost = pos["cost_basis"] + total_amount
                pos["quantity"] = total_qty
                pos["avg_entry_price"] = total_cost / total_qty
                pos["cost_basis"] = total_cost
            else:
                # New position
                self.positions[symbol] = {
                    "quantity": quantity,
                    "avg_entry_price": price,
                    "cost_basis": total_amount,
                    "current_price": price,
                    "market_value": total_amount,
                }
        else:  # sell
            pos = self.positions[symbol]
            pos["quantity"] -= quantity
            self.cash += total_amount

            if pos["quantity"] == 0:
                del self.positions[symbol]

        # Save trade to database
        trade = AgentTrade(
            competitor_id=self.competitor.id,
            symbol=symbol,
            side=OrderSide.BUY if side == "buy" else OrderSide.SELL,
            quantity=quantity,
            price=price,
            total_amount=total_amount,
            reasoning_summary=decision.get("reasoning", ""),
            confidence_score=decision.get("confidence", 0.5),
        )
        session.add(trade)
        await session.commit()
        await session.refresh(trade)

        # Update competitor equity
        self.competitor.current_equity = self.cash + sum(
            pos.get("market_value", 0) for pos in self.positions.values()
        )
        self.competitor.total_trades += 1
        self.competitor.last_trade_at = datetime.utcnow()
        await session.commit()

        logger.info(f"✅ {self.competitor.name}: {side.upper()} {quantity} {symbol} @ ${price:.2f}")

        return {
            "trade_id": trade.id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "total_amount": total_amount,
        }

    async def _save_reasoning(self, reasoning_records: List[Dict], session):
        """Save all reasoning records to database."""
        for record in reasoning_records:
            reasoning = AgentReasoningModel(
                competitor_id=self.competitor.id,
                trade_id=record.get("trade_id"),
                reasoning_type=record["type"],
                content=record["content"],
                metadata=record.get("metadata"),
            )
            session.add(reasoning)

        await session.commit()

    async def _update_daily_performance(self, session):
        """Update daily performance snapshot."""
        today = date.today()

        # Calculate current equity
        total_equity = self.cash + sum(
            pos.get("market_value", 0) for pos in self.positions.values()
        )
        positions_value = total_equity - self.cash

        # Calculate returns
        cumulative_return = (
            (total_equity - float(self.competitor.initial_capital))
            / float(self.competitor.initial_capital)
        ) * 100

        # Get yesterday's equity for daily return
        result = await session.execute(
            select(AgentDailyPerformance)
            .where(AgentDailyPerformance.competitor_id == self.competitor.id)
            .order_by(AgentDailyPerformance.trading_date.desc())
            .limit(1)
        )
        yesterday = result.scalar_one_or_none()
        daily_return = None
        if yesterday:
            daily_return = ((total_equity - float(yesterday.equity)) / float(yesterday.equity)) * 100

        # Save snapshot
        snapshot = AgentDailyPerformance(
            competitor_id=self.competitor.id,
            trading_date=today,
            equity=total_equity,
            cash=self.cash,
            positions_value=positions_value,
            daily_return=daily_return,
            cumulative_return=cumulative_return,
            trades_today=self.competitor.total_trades,
        )
        session.add(snapshot)
        await session.commit()


class AgentCompetitionCoordinator:
    """Coordinates the multi-agent trading competition."""

    def __init__(self):
        """Initialize competition coordinator."""
        self.agents: List[CompetitionAgent] = []
        logger.info("🏆 Agent Competition Coordinator initialized")

    async def initialize_agents(self):
        """Load all active competitors from database."""
        async with get_session() as session:
            result = await session.execute(
                select(AgentCompetitor).where(AgentCompetitor.is_active == True)
            )
            competitors = result.scalars().all()

            for competitor in competitors:
                agent = CompetitionAgent(competitor, competitor.model_id)
                self.agents.append(agent)

            logger.info(f"✅ Loaded {len(self.agents)} competing agents")

    async def run_daily_competition(self, watchlist: List[str]):
        """
        Run daily trading competition for all agents.

        Args:
            watchlist: List of stock symbols to trade
        """
        logger.info(f"🏆 Starting daily competition with {len(self.agents)} agents")

        results = []

        # Run all agents concurrently
        async with get_session() as session:
            tasks = [
                agent.run_daily_trading(watchlist, session) for agent in self.agents
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Update leaderboard
            await self._update_leaderboard(session)

        # Log results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"❌ Agent {i} failed: {result}")
            else:
                logger.info(f"✅ {result.get('agent')}: {result.get('trades', 0)} trades")

        logger.info("🏆 Daily competition complete")

        return results

    async def _update_leaderboard(self, session):
        """Update daily leaderboard rankings."""
        today = date.today()

        # Get all competitors sorted by equity
        result = await session.execute(
            select(AgentCompetitor)
            .where(AgentCompetitor.is_active == True)
            .order_by(AgentCompetitor.current_equity.desc())
        )
        competitors = result.scalars().all()

        # Create leaderboard entries
        for rank, competitor in enumerate(competitors, start=1):
            total_return = (
                (float(competitor.current_equity) - float(competitor.initial_capital))
                / float(competitor.initial_capital)
            ) * 100

            # Get today's performance
            perf_result = await session.execute(
                select(AgentDailyPerformance)
                .where(AgentDailyPerformance.competitor_id == competitor.id)
                .where(AgentDailyPerformance.trading_date == today)
            )
            perf = perf_result.scalar_one_or_none()

            leaderboard = AgentLeaderboard(
                competitor_id=competitor.id,
                ranking_date=today,
                rank=rank,
                equity=competitor.current_equity,
                total_return=total_return,
                daily_return=perf.daily_return if perf else None,
                sharpe_ratio=competitor.sharpe_ratio,
                win_rate=competitor.win_rate,
                total_trades=competitor.total_trades,
            )
            session.add(leaderboard)

        await session.commit()
        logger.info(f"✅ Leaderboard updated for {today}")

    async def get_competition_summary(self) -> Dict[str, Any]:
        """Get current competition status."""
        async with get_session() as session:
            result = await session.execute(
                select(AgentCompetitor)
                .where(AgentCompetitor.is_active == True)
                .order_by(AgentCompetitor.current_equity.desc())
            )
            competitors = result.scalars().all()

            return {
                "total_agents": len(competitors),
                "leaders": [
                    {
                        "name": c.name,
                        "model": c.model_id,
                        "equity": float(c.current_equity),
                        "return": float(c.total_return) if c.total_return else 0.0,
                    }
                    for c in competitors[:3]
                ],
                "last_updated": datetime.utcnow().isoformat(),
            }


# Global competition coordinator instance
competition_coordinator = AgentCompetitionCoordinator()

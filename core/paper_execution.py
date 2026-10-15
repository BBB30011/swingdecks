"""
SwingDeck Paper Execution Simulator & Order State Machine
Implements realistic paper-only simulated execution:
- Order Lifecycle: CREATED -> ACCEPTED -> (FILLED | PARTIALLY_FILLED | REJECTED | CANCELLED | EXPIRED)
- Realistic Friction: Fees, Slippage, Liquidity Constraints, Price Gaps
- Hard Paper-Only Boundary: Fails closed if live mode, broker credentials, or live endpoints are present.
"""

import os
import uuid
import math
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field

from core.position import PaperPosition
from core.paper_portfolio import PaperPortfolio
from core.schemas import MarketBar

class LiveExecutionBlockedError(RuntimeError):
    """Raised whenever any live-trading path, credential, or endpoint is encountered."""
    pass

class PaperOrder(BaseModel):
    order_id: str
    run_id: str
    event_id: str
    symbol: str
    side: Literal["BUY", "SELL"]
    quantity: float
    lots: int
    order_type: Literal["MARKET", "LIMIT"] = "LIMIT"
    request_price: float
    simulated_execution_price: Optional[float] = None
    execution_timestamp: Optional[str] = None
    fees: float = 0.0
    slippage: float = 0.0
    status: Literal["CREATED", "ACCEPTED", "REJECTED", "PARTIALLY_FILLED", "FILLED", "CANCELLED", "EXPIRED"] = "CREATED"
    filled_quantity: float = 0.0
    rejection_reason: Optional[str] = None
    stop_loss: float = 0.0
    target_price: float = 0.0
    initial_risk: float = 0.0
    initial_reward: float = 0.0
    initial_rr: float = 0.0
    thesis: str = ""
    invalidation_conditions: List[str] = Field(default_factory=list)
    opened_by_decision_id: str = ""

class ExecutionFrictionConfig(BaseModel):
    fee_rate_buy: float = 0.0015   # 0.15% IDX standard buy commission
    fee_rate_sell: float = 0.0025  # 0.25% IDX standard sell commission (incl. 0.1% final tax)
    slippage_bps: float = 5.0      # 5 basis points baseline slippage
    max_bar_volume_pct: float = 0.10 # Max fill allowed is 10% of bar volume
    allow_partial_fills: bool = True
    enforce_paper_isolation: bool = True

class PaperExecutionSimulator:
    """
    Simulates order routing and execution with realistic market frictions.
    Guarantees strict paper-only isolation.
    """
    def __init__(self, config: Optional[ExecutionFrictionConfig] = None):
        self.config = config or ExecutionFrictionConfig()
        self.orders: Dict[str, PaperOrder] = {}
        self._verify_paper_isolation()

    def _verify_paper_isolation(self):
        """Hard safety check: verifies no live broker environment or credentials exist."""
        forbidden_env_keys = [
            "LIVE_TRADING_ENABLED",
            "BROKER_API_KEY",
            "BROKER_SECRET",
            "LIVE_BROKER_URL",
            "PRODUCTION_ORDER_ENDPOINT"
        ]
        for key in forbidden_env_keys:
            val = os.getenv(key, "").strip().lower()
            if val and val not in ["0", "false", "disabled", "none", ""]:
                raise LiveExecutionBlockedError(
                    f"CRITICAL SAFETY VIOLATION: Live trading credential/flag discovered in env ({key}={val}). "
                    f"Execution blocked fail-closed."
                )

    def create_order(self, 
                     run_id: str,
                     event_id: str,
                     symbol: str,
                     side: Literal["BUY", "SELL"],
                     quantity: float,
                     lots: int,
                     request_price: float,
                     stop_loss: float,
                     target_price: float,
                     order_type: Literal["MARKET", "LIMIT"] = "LIMIT",
                     thesis: str = "",
                     invalidation_conditions: Optional[List[str]] = None,
                     decision_id: str = "") -> PaperOrder:
                     
        self._verify_paper_isolation()
        
        order_key = f"{event_id}_{symbol.strip().upper()}_{request_price}_{quantity}"
        order_hash = hashlib.md5(order_key.encode("utf-8")).hexdigest()[:8].upper()
        order = PaperOrder(
            order_id=f"ORD_{order_hash}",
            run_id=run_id,
            event_id=event_id,
            symbol=symbol.strip().upper(),
            side=side,
            quantity=quantity,
            lots=lots,
            order_type=order_type,
            request_price=request_price,
            status="CREATED",
            stop_loss=stop_loss,
            target_price=target_price,
            initial_risk=(request_price - stop_loss) * quantity if stop_loss > 0 else 0.0,
            initial_reward=(target_price - request_price) * quantity if target_price > 0 else 0.0,
            initial_rr=((target_price - request_price) / (request_price - stop_loss)) if (stop_loss > 0 and request_price > stop_loss) else 0.0,
            thesis=thesis,
            invalidation_conditions=invalidation_conditions or [],
            opened_by_decision_id=decision_id
        )
        self.orders[order.order_id] = order
        return order

    def simulate_execution(self, 
                           order: PaperOrder, 
                           bar: MarketBar, 
                           portfolio: PaperPortfolio,
                           timestamp: str) -> PaperOrder:
        """
        Processes a pending paper order against an incoming market bar.
        Applies friction, slippage, liquidity limits, and portfolio cash checks.
        """
        self._verify_paper_isolation()
        
        if order.status not in ["CREATED", "ACCEPTED", "PARTIALLY_FILLED"]:
            return order

        order.status = "ACCEPTED"

        # 1. Price Matching & Gaps
        fill_price = order.request_price
        if order.side == "BUY":
            # If bar low is higher than limit request price, order cannot fill
            if order.order_type == "LIMIT" and bar.low > order.request_price:
                order.status = "EXPIRED"
                order.rejection_reason = f"PRICE_UNREACHABLE: Bar low {bar.low} > limit {order.request_price}"
                return order
            # Price gap: If bar opened above limit, fill at bar open if market, else limit
            if bar.open > order.request_price and order.order_type == "MARKET":
                fill_price = bar.open
        elif order.side == "SELL":
            # If bar high is lower than limit request price, order cannot fill
            if order.order_type == "LIMIT" and bar.high < order.request_price:
                order.status = "EXPIRED"
                order.rejection_reason = f"PRICE_UNREACHABLE: Bar high {bar.high} < limit {order.request_price}"
                return order
            if bar.open < order.request_price and order.order_type == "MARKET":
                fill_price = bar.open

        # 2. Slippage Simulation
        slippage_pct = self.config.slippage_bps / 10000.0
        if order.side == "BUY":
            effective_price = fill_price * (1.0 + slippage_pct)
        else:
            effective_price = fill_price * (1.0 - slippage_pct)
        order.slippage = abs(effective_price - fill_price) * order.quantity
        order.simulated_execution_price = round(effective_price, 2)

        # 3. Liquidity & Volume Constraint
        max_fill_shares = bar.volume * self.config.max_bar_volume_pct
        target_shares = order.quantity - order.filled_quantity
        
        if bar.volume <= 0:
            order.status = "REJECTED"
            order.rejection_reason = "ZERO_LIQUIDITY: Market bar volume is 0"
            return order

        if target_shares > max_fill_shares:
            if not self.config.allow_partial_fills or max_fill_shares <= 0:
                order.status = "REJECTED"
                order.rejection_reason = f"INSUFFICIENT_LIQUIDITY: Requested {target_shares} > max volume capacity {max_fill_shares}"
                return order
            # Partial fill
            fill_shares = max_fill_shares
            order.filled_quantity += fill_shares
            order.status = "PARTIALLY_FILLED"
        else:
            fill_shares = target_shares
            order.filled_quantity += fill_shares
            order.status = "FILLED"

        # 4. Fee Calculation
        fee_rate = self.config.fee_rate_buy if order.side == "BUY" else self.config.fee_rate_sell
        nominal_val = fill_shares * order.simulated_execution_price
        order.fees = round(nominal_val * fee_rate, 2)
        order.execution_timestamp = timestamp

        # 5. Portfolio Mutation for BUY
        if order.side == "BUY":
            total_cost_required = nominal_val + order.fees
            if portfolio.cash < total_cost_required:
                order.status = "REJECTED"
                order.rejection_reason = f"INSUFFICIENT_CASH: Required {total_cost_required} > available {portfolio.cash}"
                order.filled_quantity = 0.0
                return order

            if not portfolio.can_open_position(order.symbol):
                order.status = "REJECTED"
                order.rejection_reason = f"DUPLICATE_POSITION: {order.symbol} already OPEN or PENDING"
                order.filled_quantity = 0.0
                return order

            # Instantiate PaperPosition
            pos_key = f"{order.order_id}_{order.symbol}_{timestamp}"
            pos_hash = hashlib.md5(pos_key.encode("utf-8")).hexdigest()[:8].upper()
            pos = PaperPosition(
                position_id=f"POS_{pos_hash}",
                job_id=order.opened_by_decision_id or order.order_id,
                symbol=order.symbol,
                status="OPEN",
                entry_timestamp=timestamp,
                entry_price=order.simulated_execution_price,
                quantity=fill_shares,
                lots=int(fill_shares / 100),
                stop_loss=order.stop_loss,
                target_price=order.target_price,
                initial_risk=order.initial_risk,
                initial_reward=order.initial_reward,
                initial_rr=order.initial_rr,
                position_value=nominal_val,
                entry_cost=order.fees,
                exit_cost=0.0,
                current_price=order.simulated_execution_price,
                thesis=order.thesis,
                invalidation_conditions=order.invalidation_conditions,
                opened_by_decision_id=order.opened_by_decision_id
            )
            portfolio.open_position(pos, cost=order.fees)

        return order

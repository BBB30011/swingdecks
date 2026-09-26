from core.backtest.models import BacktestConfig, BacktestTrade, BacktestResult, BacktestIntegrityError
from core.backtest.replay import PointInTimeReplay
from core.backtest.costs import TransactionCostEngine
from core.backtest.metrics import MetricsEngine
from core.backtest.calendar import TradingCalendar, DataGapAnalyzer
from core.market_scanner import MarketScanner
from core.schemas import MarketSnapshot
import uuid
from core.backtest.models import BacktestConfig, BacktestTrade, BacktestResult, BacktestIntegrityError
from core.backtest.replay import PointInTimeReplay
from core.backtest.costs import TransactionCostEngine
from core.backtest.metrics import MetricsEngine
from core.backtest.calendar import TradingCalendar, DataGapAnalyzer
from core.market_scanner import MarketScanner
from core.schemas import MarketSnapshot
from core.decision import PortfolioContext, DecisionResult
from core.risk_engine import RiskEngine, RiskEngineConfig
from agents.agent3_committee.committee import InvestmentCommittee
import uuid
import pandas as pd
from typing import List, Dict

class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.replay = PointInTimeReplay()
        self.scanner = MarketScanner()
        self.risk_engine = RiskEngine(RiskEngineConfig({
            "risk": {"max_single_position_risk": config.risk_per_trade, "max_portfolio_risk": 0.5},
            "trade": {"lot_size": config.lot_size, "maximum_positions": config.max_positions}
        }))
        self.committee = InvestmentCommittee()
        
    def run(self, snapshots: List[MarketSnapshot], benchmark_snapshot: MarketSnapshot = None) -> BacktestResult:
        for snap in snapshots:
            self.replay.load_snapshot(snap)
        if benchmark_snapshot:
            self.replay.load_snapshot(benchmark_snapshot)
            
        all_times = set()
        for snap in snapshots:
            for b in snap.bars:
                all_times.add(b.timestamp)
        
        global_timeline = sorted(list(all_times))
        calendar = TradingCalendar(global_timeline)
        
        # Data gap flags
        data_gap_flags = {}
        for snap in snapshots:
            sym_times = [b.timestamp for b in snap.bars]
            data_gap_flags[snap.symbol] = DataGapAnalyzer.analyze(sym_times, global_timeline)
            
        capital = self.config.initial_capital
        cash = capital
        open_positions: List[BacktestTrade] = []
        closed_trades: List[BacktestTrade] = []
        equity_curve: List[float] = []
        
        signals_generated = 0
        trades_opened = 0
        trades_closed = 0
        trades_skipped = 0
        
        market_data: Dict[str, pd.DataFrame] = {}
        for snap in snapshots:
            df = pd.DataFrame([b.model_dump() for b in snap.bars])
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                market_data[snap.symbol] = df
        
        def get_price(sym: str, ts: str, price_type: str = "open"):
            target_time = pd.to_datetime(ts)
            df = market_data.get(sym)
            if df is None: return None
            if target_time in df.index:
                val = float(df.loc[target_time][price_type])
                if pd.isna(val) or val <= 0:
                    raise BacktestIntegrityError(f"Invalid price {val} for {sym} at {ts}")
                return val
            return None

        # Fixed Allocation Rule
        fixed_allocation_per_trade = self.config.initial_capital / self.config.max_positions

        for i, current_time in enumerate(global_timeline):
            still_open = []
            
            # --- A. EXECUTE EXITS ---
            for pos in open_positions:
                pos.holding_bars += 1
                
                should_exit = False
                exit_price = None
                
                curr_open = get_price(pos.symbol, current_time, "open")
                curr_high = get_price(pos.symbol, current_time, "high")
                curr_low = get_price(pos.symbol, current_time, "low")
                curr_close = get_price(pos.symbol, current_time, "close")
                
                if curr_open is None or curr_high is None or curr_low is None or curr_close is None:
                    # Missing data, hold until next available
                    pos.holding_bars -= 1 # Revert holding bar increment so we wait for data
                    still_open.append(pos)
                    continue
                    
                # Evaluate Exits
                if curr_low <= pos.stop_loss and curr_high >= pos.target_price:
                    # Same-bar ambiguity: assume STOP_FIRST
                    should_exit = True
                    exit_price = curr_open if curr_open < pos.stop_loss else pos.stop_loss
                elif curr_low <= pos.stop_loss:
                    should_exit = True
                    # Gap-through-stop logic
                    exit_price = curr_open if curr_open < pos.stop_loss else pos.stop_loss
                elif curr_high >= pos.target_price:
                    should_exit = True
                    exit_price = curr_open if curr_open > pos.target_price else pos.target_price
                elif pos.holding_bars >= self.config.holding_period_bars:
                    should_exit = True
                    exit_price = curr_close

                if should_exit:
                    eff_price, comm = TransactionCostEngine.calculate_exit(
                        exit_price, pos.quantity, self.config.commission_rate, self.config.slippage_rate
                    )
                    
                    gross_pnl = (eff_price * pos.quantity) - (pos.entry_price * pos.quantity)
                    net_pnl = gross_pnl - comm - pos.cost # subtract exit comm and entry comm
                    
                    pos.exit_timestamp = current_time
                    pos.exit_price = exit_price
                    pos.gross_pnl = gross_pnl
                    pos.net_pnl = net_pnl
                    pos.return_pct = (eff_price / pos.entry_price) - 1.0
                    pos.status = "CLOSED"
                    
                    cash += (eff_price * pos.quantity) - comm
                    closed_trades.append(pos)
                    trades_closed += 1
                else:
                    if self.config.atr_trailing_multiplier:
                        df_h = market_data[pos.symbol].loc[:pd.to_datetime(current_time)].tail(15)
                        if len(df_h) >= 14:
                            df_h['prev_close'] = df_h['close'].shift(1)
                            df_h['tr'] = df_h.apply(lambda x: max(x['high'] - x['low'], abs(x['high'] - x['prev_close']), abs(x['low'] - x['prev_close'])), axis=1)
                            atr = df_h['tr'].mean()
                            new_stop = curr_close - (atr * self.config.atr_trailing_multiplier)
                            if new_stop > pos.stop_loss:
                                pos.stop_loss = new_stop
                    still_open.append(pos)
                    
            open_positions = still_open
            
            # --- B. MARK TO MARKET EQUITY ---
            current_eq = cash
            for pos in open_positions:
                # Use current valid close, if missing, don't forward fill, use last known from entry_price ideally
                # Wait, prompt says: "Gunakan price yang tersedia. Jika current bar tidak tersedia, jangan forward fill. Gunakan last valid observable value...". 
                # Simplest: check close price. If None, we must find the last observable.
                curr_price = get_price(pos.symbol, current_time, "close")
                if curr_price is not None:
                    current_eq += (curr_price * pos.quantity)
                else:
                    # Find last observable
                    last_valid = None
                    prev_t = calendar.previous_trading_timestamp(current_time)
                    while prev_t and prev_t >= pos.entry_timestamp:
                        p = get_price(pos.symbol, prev_t, "close")
                        if p is not None:
                            last_valid = p
                            break
                        prev_t = calendar.previous_trading_timestamp(prev_t)
                    if last_valid is None: last_valid = pos.entry_price
                    current_eq += (last_valid * pos.quantity)
                    
            equity_curve.append(current_eq)
            
            # --- C. EXECUTE ENTRIES ---
            next_time = global_timeline[i+1] if i + 1 < len(global_timeline) else None
            if not next_time:
                continue
                
            open_symbols = {p.symbol for p in open_positions}
            available_slots = self.config.max_positions - len(open_positions)
            
            if available_slots <= 0:
                continue
                
            portfolio_ctx = PortfolioContext(
                capital=self.config.initial_capital,
                available_cash=cash,
                current_positions=list(open_symbols),
                total_exposure=sum([p.entry_price * p.quantity for p in open_positions]),
                total_risk=0.0,
                number_of_positions=len(open_positions),
                as_of_timestamp=current_time
            )
            
            candidates = []
            for snap in snapshots:
                if snap.symbol in open_symbols:
                    continue
                try:
                    point_snap = self.replay.get_snapshot_at(snap.symbol, current_time)
                except ValueError:
                    continue
                    
                bench_snap = None
                if benchmark_snapshot:
                    try:
                        bench_snap = self.replay.get_snapshot_at(benchmark_snapshot.symbol, current_time)
                    except ValueError:
                        pass
                
                res = self.scanner.scan(point_snap, benchmark_snapshot=bench_snap)
                if res["status"] == "READY_FOR_RESEARCH":
                    if self.config.block_bear_regime and res.get("market_regime") == "BEAR":
                        continue
                        
                    signals_generated += 1
                    if self.config.entry_mode == "CURRENT_BAR_CLOSE":
                        entry_price = get_price(snap.symbol, current_time, "close")
                        act_entry_time = current_time
                    else:
                        entry_price = get_price(snap.symbol, next_time, "open")
                        act_entry_time = next_time
                        
                    if not entry_price:
                        continue
                        
                    if self.config.atr_stop_multiplier:
                        df_history = market_data[snap.symbol].loc[:pd.to_datetime(current_time)].tail(15)
                        if len(df_history) >= 14:
                            df_history['prev_close'] = df_history['close'].shift(1)
                            df_history['tr'] = df_history.apply(lambda x: max(x['high'] - x['low'], abs(x['high'] - x['prev_close']), abs(x['low'] - x['prev_close'])), axis=1)
                            atr = df_history['tr'].mean()
                            stop_loss = entry_price - (atr * self.config.atr_stop_multiplier)
                        else:
                            stop_loss = res.get("features", {}).get("price_action", {}).get("low_20d", 0.0)
                    else:
                        stop_loss = res.get("features", {}).get("price_action", {}).get("low_20d", 0.0)
                        
                    if stop_loss <= 0.0 or entry_price <= stop_loss:
                        continue
                        
                    target_price = entry_price + 2.0 * (entry_price - stop_loss)
                    
                    quant_data = {
                        "quant_score": res["quant_score"],
                        "quant_confidence": res["quant_confidence"],
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "target_price": target_price,
                        "market_regime": res["market_regime"],
                        "price": {"current": get_price(snap.symbol, current_time, "close") or entry_price},
                        "price_action": {"low_20d": stop_loss},
                        "trigger": {
                            "trigger_type": "BREAKOUT",
                            "trigger_price": entry_price,
                            "trigger_condition": "ABOVE_RESISTANCE",
                            "timestamp": current_time
                        }
                    }
                    
                    research_data = {
                        "confidence": 85,
                        "completeness": "COMPLETE",
                        "red_team_decision": "PASS",
                        "flow_state": res.get("features", {}).get("flow", {}).get("flow_state", "UNKNOWN"),
                        "evidence_state": "GOOD"
                    }
                    
                    risk_eval = self.risk_engine.evaluate(
                        symbol=snap.symbol,
                        entry=entry_price,
                        stop=stop_loss,
                        target=target_price,
                        portfolio=portfolio_ctx,
                        quant_data=quant_data,
                        research_data=research_data
                    )
                    
                    decision = self.committee.synthesize(
                        job_id=str(uuid.uuid4()),
                        symbol=snap.symbol,
                        as_of_timestamp=current_time,
                        quant_data=quant_data,
                        research_data=research_data,
                        risk_evaluation=risk_eval
                    )
                    
                    if decision.action == "BUY" and getattr(decision.opportunity_assessment, 'entry_readiness', 'NOT_READY') == "READY":
                        candidates.append(decision)
                        
            candidates = sorted(candidates, key=lambda x: (-getattr(x.opportunity_assessment, 'opportunity_score', 0), -x.confidence, x.symbol))
            selected = candidates[:available_slots]
            
            for sig in selected:
                eff_price, comm = TransactionCostEngine.calculate_entry(sig.entry_price, sig.position_size, self.config.commission_rate, self.config.slippage_rate)
                total_cost = (eff_price * sig.position_size) + comm
                
                if cash >= total_cost and sig.position_size > 0:
                    cash -= total_cost
                    trade = BacktestTrade(
                        position_id=str(uuid.uuid4()),
                        symbol=sig.symbol,
                        signal_timestamp=current_time,
                        entry_timestamp=act_entry_time,
                        entry_price=sig.entry_price,
                        stop_loss=sig.stop_loss,
                        target_price=sig.target_price,
                        shares=float(sig.position_size),
                        quantity=float(sig.position_size),
                        cost=comm,
                        holding_bars=0,
                        status="OPEN",
                        signal=sig
                    )
                    open_positions.append(trade)
                    trades_opened += 1
                else:
                    trades_skipped += 1

        # 5. Simulation End
        unrealized_pnl = 0.0
        realized_pnl = sum([t.net_pnl for t in closed_trades if t.net_pnl is not None])
        
        for pos in open_positions:
            pos.status = "OPEN_AT_END"
            # Calc unrealized PNL
            last_price = get_price(pos.symbol, global_timeline[-1], "close")
            if last_price is None:
                last_price = pos.entry_price
            eff_price, comm = TransactionCostEngine.calculate_exit(last_price, pos.quantity, self.config.commission_rate, self.config.slippage_rate)
            u_pnl = (eff_price * pos.quantity) - (pos.entry_price * pos.quantity) - comm - pos.cost
            unrealized_pnl += u_pnl
            
        all_trades = closed_trades + open_positions
        metrics = MetricsEngine.calculate_trade_metrics(closed_trades) # Only closed trades
        max_dd = MetricsEngine.calculate_drawdown(equity_curve)
        
        final_equity = cash
        for pos in open_positions:
            last_price = get_price(pos.symbol, global_timeline[-1], "close")
            if last_price is None:
                last_price = pos.entry_price
            final_equity += (last_price * pos.quantity)
            
        total_ret = (final_equity - self.config.initial_capital) / self.config.initial_capital
        
        total_comm = sum([t.cost for t in all_trades if t.cost]) + sum([(t.gross_pnl - t.net_pnl) - t.cost if t.net_pnl is not None else 0 for t in closed_trades])
        
        turnover_notional = sum([t.entry_price * t.quantity for t in all_trades])
        avg_equity = sum(equity_curve) / len(equity_curve) if equity_curve else self.config.initial_capital
        turnover = turnover_notional / avg_equity if avg_equity > 0 else 0.0

        score_buckets = {
            "60-69": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 60 <= getattr(t.signal.opportunity_assessment, 'opportunity_score', 0) <= 69]),
            "70-79": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 70 <= getattr(t.signal.opportunity_assessment, 'opportunity_score', 0) <= 79]),
            "80-89": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 80 <= getattr(t.signal.opportunity_assessment, 'opportunity_score', 0) <= 89]),
            "90-100": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 90 <= getattr(t.signal.opportunity_assessment, 'opportunity_score', 0) <= 100]),
        }
        
        conf_buckets = {
            "0-59": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 0 <= t.signal.confidence <= 59]),
            "60-79": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 60 <= t.signal.confidence <= 79]),
            "80-89": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 80 <= t.signal.confidence <= 89]),
            "90-100": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if 90 <= t.signal.confidence <= 100]),
        }
        
        regimes = ["BULL", "BEAR", "SIDEWAYS", "HIGH_VOLATILITY", "UNKNOWN"]
        regime_breakdown = {
            r: MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'market_state', 'UNKNOWN') == r]) for r in regimes
        }
        
        timing_buckets = {
            "EARLY": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'timing_quality', 'UNKNOWN') == "EARLY"]),
            "READY": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'timing_quality', 'UNKNOWN') == "READY"]),
            "LATE": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'timing_quality', 'UNKNOWN') == "LATE"]),
            "UNKNOWN": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'timing_quality', 'UNKNOWN') not in ("EARLY", "READY", "LATE")]),
        }
        
        tier_buckets = {
            "TIER 1": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'signal_tier', 'UNKNOWN') == "TIER 1"]),
            "TIER 2": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'signal_tier', 'UNKNOWN') == "TIER 2"]),
            "TIER 3": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'signal_tier', 'UNKNOWN') == "TIER 3"]),
        }
        
        urgency_buckets = {
            "HIGH": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'alert_urgency', 'UNKNOWN') in ("HIGH", "VERY_HIGH", "CRITICAL")]),
            "MEDIUM": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'alert_urgency', 'UNKNOWN') == "MEDIUM"]),
            "LOW": MetricsEngine.calculate_bucket_stats([t for t in closed_trades if getattr(t.signal.opportunity_assessment, 'alert_urgency', 'UNKNOWN') == "LOW"]),
        }
        
        integrity_warnings = []
        if metrics["win_rate"] and metrics["win_rate"] > 0.90:
            integrity_warnings.append("UNUSUALLY_HIGH_WIN_RATE_REQUIRES_INVESTIGATION")

        return BacktestResult(
            initial_capital=self.config.initial_capital,
            final_capital=final_equity,
            total_return=total_ret,
            max_drawdown=max_dd,
            signals_generated=signals_generated,
            trades_opened=trades_opened,
            trades_closed=trades_closed,
            trades_skipped=trades_skipped,
            open_positions_at_end=len(open_positions),
            number_of_trades=trades_closed,
            winning_trades=metrics["winning_trades"],
            losing_trades=metrics["losing_trades"],
            win_rate=metrics["win_rate"],
            profit_factor=metrics["profit_factor"],
            expectancy=metrics["expectancy"],
            average_win=metrics["average_win"],
            average_loss=metrics["average_loss"],
            average_hold=metrics["average_hold"],
            turnover=turnover,
            total_cost=total_comm,
            realized_pnl=realized_pnl,
            unrealized_pnl=unrealized_pnl,
            score_buckets=score_buckets,
            confidence_buckets=conf_buckets,
            regime_breakdown=regime_breakdown,
            timing_buckets=timing_buckets,
            tier_buckets=tier_buckets,
            urgency_buckets=urgency_buckets,
            data_gap_flags=data_gap_flags,
            integrity_warnings=integrity_warnings,
            trades_history=all_trades
        )

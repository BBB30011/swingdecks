from typing import List, Dict, Any, Tuple
from core.backtest.models import BacktestTrade
from core.schemas import AttributionGroup, PerformanceAttribution

class PerformanceAttributionEngine:
    """
    Groups and analyzes backtest results based on predefined metadata fields.
    """
    
    @staticmethod
    def get_score_bucket(score: float) -> str:
        if 60 <= score < 70: return "60_69"
        if 70 <= score < 80: return "70_79"
        if 80 <= score < 90: return "80_89"
        if 90 <= score <= 100: return "90_100"
        return "UNKNOWN"
        
    @staticmethod
    def get_confidence_bucket(conf: float) -> str:
        if 0 <= conf < 60: return "0_59"
        if 60 <= conf < 70: return "60_69"
        if 70 <= conf < 80: return "70_79"
        if 80 <= conf < 90: return "80_89"
        if 90 <= conf <= 100: return "90_100"
        return "UNKNOWN"

    @staticmethod
    def check_sample_size(count: int) -> str:
        if count < 5: return "VERY_SMALL_SAMPLE"
        if count < 20: return "SMALL_SAMPLE"
        if count < 50: return "LIMITED_SAMPLE"
        return "ADEQUATE_FOR_DESCRIPTIVE_ANALYSIS"

    @classmethod
    def calc_group_metrics(cls, trades: List[BacktestTrade]) -> AttributionGroup:
        # Note: We group by the signal generated for signals, but here we just take closed trades
        # to calculate PnL metrics.
        # Actually, `trades` could contain OPEN trades? We should only analyze CLOSED trades for win/loss
        closed_trades = [t for t in trades if t.exit_timestamp is not None and t.net_pnl is not None]
        
        opened = len(trades)
        closed = len(closed_trades)
        
        status = cls.check_sample_size(closed)
        if closed == 0:
            return AttributionGroup(
                signals=opened,
                trades_opened=opened,
                trades_closed=0,
                status="INSUFFICIENT_SAMPLE"
            )
            
        wins = [t for t in closed_trades if t.net_pnl > 0]
        losses = [t for t in closed_trades if t.net_pnl <= 0]
        
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = win_count / closed if closed > 0 else None
        
        gross_pnl = sum(t.gross_pnl for t in closed_trades) if any(t.gross_pnl is not None for t in closed_trades) else 0.0
        net_pnl = sum(t.net_pnl for t in closed_trades)
        total_cost = sum(t.cost for t in closed_trades if t.cost is not None)
        
        avg_win = sum(w.net_pnl for w in wins) / win_count if win_count > 0 else 0.0
        avg_loss = sum(l.net_pnl for l in losses) / loss_count if loss_count > 0 else 0.0
        
        expectancy = None
        if win_rate is not None:
            expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
            
        profit_factor = None
        gross_loss = sum(abs(l.net_pnl) for l in losses)
        gross_win = sum(w.net_pnl for w in wins)
        if gross_loss > 0:
            profit_factor = gross_win / gross_loss
        elif gross_win > 0:
            profit_factor = 999.0 # arbitrary large number when no losses
            
        avg_hold = sum(t.holding_bars for t in closed_trades if t.holding_bars is not None) / closed if closed > 0 else None
        
        return AttributionGroup(
            signals=opened,
            trades_opened=opened,
            trades_closed=closed,
            wins=win_count,
            losses=loss_count,
            win_rate=win_rate,
            gross_pnl=gross_pnl,
            net_pnl=net_pnl,
            expectancy=expectancy,
            profit_factor=profit_factor,
            average_win=avg_win,
            average_loss=avg_loss,
            total_cost=total_cost,
            average_holding_period=avg_hold,
            status=status
        )

    @classmethod
    def attribute(cls, dataset_id: str, trades: List[BacktestTrade]) -> PerformanceAttribution:
        overall = cls.calc_group_metrics(trades)
        
        # Groupings
        by_score = {"60_69": [], "70_79": [], "80_89": [], "90_100": []}
        by_conf = {"0_59": [], "60_69": [], "70_79": [], "80_89": [], "90_100": []}
        by_quality = {"HIGH": [], "MEDIUM": [], "LOW": [], "INSUFFICIENT": [], "UNKNOWN": []}
        by_priority = {"P1": [], "P2": [], "P3": [], "P4": [], "UNKNOWN": []}
        by_market = {"BULL": [], "BEAR": [], "SIDEWAYS": [], "HIGH_VOLATILITY": [], "UNKNOWN": []}
        by_stock = {"BULL": [], "BEAR": [], "SIDEWAYS": [], "HIGH_VOLATILITY": [], "UNKNOWN": []}
        by_alignment = {"ALIGNED": [], "DIVERGED": [], "UNKNOWN": []}
        by_flow = {"ACCUMULATION": [], "DISTRIBUTION": [], "NEUTRAL": [], "UNKNOWN": []}

        for t in trades:
            s = t.signal.opportunity_assessment
            s_bucket = cls.get_score_bucket(s.opportunity_score)
            if s_bucket in by_score: by_score[s_bucket].append(t)
            
            c_bucket = cls.get_confidence_bucket(t.signal.confidence)
            if c_bucket in by_conf: by_conf[c_bucket].append(t)
            
            q = s.opportunity_class if s.opportunity_class in by_quality else "UNKNOWN"
            by_quality[q].append(t)
            
            p = getattr(s, "research_priority", "UNKNOWN")
            if p not in by_priority: p = "UNKNOWN"
            by_priority[p].append(t)
            
            mr = s.market_state if s.market_state in by_market else "UNKNOWN"
            by_market[mr].append(t)
            
            sr = s.technical_state if s.technical_state in by_stock else "UNKNOWN"
            by_stock[sr].append(t)
            
            al = getattr(s, "regime_alignment", "UNKNOWN")
            if al not in by_alignment: al = "UNKNOWN"
            by_alignment[al].append(t)
            
            fl = getattr(s, "flow_state", "UNKNOWN")
            if fl not in by_flow: fl = "UNKNOWN"
            by_flow[fl].append(t)

        warnings = []
        if overall.status in ["VERY_SMALL_SAMPLE", "SMALL_SAMPLE"]:
            warnings.append(f"Overall dataset has {overall.status}. Interpret attributes with caution.")
            
        return PerformanceAttribution(
            dataset_id=dataset_id,
            overall=overall,
            by_score={k: cls.calc_group_metrics(v) for k, v in by_score.items()},
            by_confidence={k: cls.calc_group_metrics(v) for k, v in by_conf.items()},
            by_quality={k: cls.calc_group_metrics(v) for k, v in by_quality.items()},
            by_priority={k: cls.calc_group_metrics(v) for k, v in by_priority.items()},
            by_market_regime={k: cls.calc_group_metrics(v) for k, v in by_market.items()},
            by_stock_regime={k: cls.calc_group_metrics(v) for k, v in by_stock.items()},
            by_regime_alignment={k: cls.calc_group_metrics(v) for k, v in by_alignment.items()},
            by_flow={k: cls.calc_group_metrics(v) for k, v in by_flow.items()},
            warnings=warnings
        )

import math
from typing import List, Dict
from core.backtest.models import BacktestTrade

class MetricsEngine:
    
    @staticmethod
    def calculate_drawdown(equity_curve: List[float]) -> float:
        if not equity_curve:
            return 0.0
        
        peak = equity_curve[0]
        max_dd = 0.0
        
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
                
        return max_dd

    @staticmethod
    def calculate_trade_metrics(trades: List[BacktestTrade]) -> dict:
        closed = [t for t in trades if t.status == "CLOSED" and t.net_pnl is not None]
        
        num_trades = len(closed)
        if num_trades == 0:
            return {
                "winning_trades": 0, "losing_trades": 0, "win_rate": None,
                "profit_factor": None, "expectancy": None,
                "average_win": None, "average_loss": None, "average_hold": None
            }
            
        winners = [t for t in closed if t.net_pnl > 0]
        losers = [t for t in closed if t.net_pnl <= 0]
        
        win_rate = len(winners) / num_trades
        
        gross_profit = sum(t.net_pnl for t in winners)
        gross_loss = sum(t.net_pnl for t in losers)
        
        # Profit Factor
        profit_factor = None
        if abs(gross_loss) > 0:
            profit_factor = gross_profit / abs(gross_loss)
            
        # Averages
        avg_win = gross_profit / len(winners) if winners else 0.0
        avg_loss = gross_loss / len(losers) if losers else 0.0
        
        loss_rate = 1.0 - win_rate
        expectancy = (win_rate * avg_win) - (loss_rate * abs(avg_loss))
        
        avg_hold = sum(t.holding_bars for t in closed) / num_trades if closed else 0.0
        
        return {
            "winning_trades": len(winners),
            "losing_trades": len(losers),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "expectancy": expectancy,
            "average_win": avg_win if winners else None,
            "average_loss": avg_loss if losers else None,
            "average_hold": avg_hold
        }

    @staticmethod
    def calculate_bucket_stats(trades: List[BacktestTrade]) -> dict:
        if not trades:
            return {"trades": 0, "win_rate": None, "average_return": None, "profit_factor": None, "expectancy": None}
            
        metrics = MetricsEngine.calculate_trade_metrics(trades)
        total_ret = sum(t.return_pct for t in trades if t.return_pct is not None)
        avg_ret = total_ret / len(trades) if len(trades) > 0 else None
        
        return {
            "trades": len(trades),
            "win_rate": metrics["win_rate"],
            "average_return": avg_ret,
            "profit_factor": metrics["profit_factor"],
            "expectancy": metrics["expectancy"]
        }

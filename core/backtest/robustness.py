from copy import deepcopy
from core.backtest.engine import BacktestEngine
from core.backtest.models import BacktestConfig
from core.schemas import RobustnessResult, MarketSnapshot
from typing import List

class RobustnessAnalyzer:
    def __init__(self, baseline_config: BacktestConfig):
        self.baseline_config = baseline_config

    def run_stress_test(self, snapshots: List[MarketSnapshot]) -> RobustnessResult:
        # Run Baseline
        engine_base = BacktestEngine(self.baseline_config)
        res_base = engine_base.run(snapshots)
        
        # Define Stress
        stress_config = deepcopy(self.baseline_config)
        stress_config.commission_rate *= 2
        stress_config.slippage_rate *= 2
        
        # Run Stress
        engine_stress = BacktestEngine(stress_config)
        res_stress = engine_stress.run(snapshots)
        
        base_ret = res_base.total_return
        stress_ret = res_stress.total_return
        
        status = "INSUFFICIENT_SAMPLE"
        if res_base.number_of_trades >= 5:
            if stress_ret < base_ret * 0.5:
                status = "SENSITIVE"
            else:
                status = "ROBUST"
                
        return RobustnessResult(
            baseline_return=base_ret,
            stress_return=stress_ret,
            baseline_dd=res_base.max_drawdown,
            stress_dd=res_stress.max_drawdown,
            baseline_win_rate=res_base.win_rate,
            stress_win_rate=res_stress.win_rate,
            status=status
        )

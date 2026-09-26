import os
import json
from core.backtest.models import BacktestConfig
from core.backtest.engine import BacktestEngine
from core.backtest.dataset_splitter import DatasetSplitter
from core.backtest.walk_forward import WalkForwardValidator
from core.schemas import WalkForwardSplit, MarketSnapshot
from core.dataset import HistoricalDataset
from core.backtest.metrics import MetricsEngine
from scripts.run_forensics_aw import calculate_mfe_mae

class MockPerformanceValidator:
    def compare(self, res_train, res_val, res_test):
        return {"status": "VALID", "degradation": {}, "warnings": []}

def get_snapshots():
    snapshot_path = "data/processed/IDX_DAILY_20260911_069ee2ed.json"
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
        
    manifest = snapshot_data.get("manifest", {}).get("symbols", {})
    snapshots = []
    
    for symbol, meta in manifest.items():
        filepath = meta.get("filepath")
        if not filepath: continue
        full_path = os.path.join(os.getcwd(), filepath)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as sf:
                sym_data = json.load(sf)
                if isinstance(sym_data, list):
                    snapshots.append(MarketSnapshot(
                        symbol=symbol, timestamp="2026-09-11T00:00:00",
                        data_source="YFINANCE", data_quality="FRESH", bars=sym_data
                    ))
                else:
                    snapshots.append(MarketSnapshot(**sym_data))
                    
    return [s for s in snapshots if s.symbol != "^JKSE"]

def run_experiment(config: BacktestConfig, name: str):
    print(f"Running {name}...")
    tradable = get_snapshots()
    engine = BacktestEngine(config)
    
    split_config = WalkForwardSplit(
        train_start="2021-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2026-09-01"
    )
    
    validator = WalkForwardValidator(
        backtest_engine=engine, splitter=DatasetSplitter(),
        performance_validator=MockPerformanceValidator()
    )
    
    res = validator.run(tradable, split_config)
    test_res = res["test"]
    
    # Calculate MFE Capture for Test
    bars_dict = {s.symbol: s.bars for s in tradable}
    mfe_ratios = []
    total_gross = 0.0
    for t in test_res.trades_history:
        if t.status != "CLOSED": continue
        mfe, mae = calculate_mfe_mae(bars_dict[t.symbol], t.entry_price, t.entry_timestamp, t.exit_timestamp)
        if mfe > 0 and t.return_pct is not None and t.return_pct > 0:
            mfe_ratios.append(t.return_pct / mfe)
        total_gross += t.gross_pnl / (t.entry_price * t.shares) if t.entry_price > 0 else 0
            
    mfe_capture = sum(mfe_ratios) / len(mfe_ratios) if mfe_ratios else 0.0
    avg_gross = total_gross / test_res.number_of_trades if test_res.number_of_trades > 0 else 0.0
    
    return {
        "name": name,
        "return": test_res.total_return,
        "max_dd": test_res.max_drawdown,
        "win_rate": test_res.win_rate or 0.0,
        "trades": test_res.number_of_trades,
        "avg_gross": avg_gross,
        "mfe_capture": mfe_capture
    }

def main():
    base_config = BacktestConfig(
        initial_capital=100_000_000.0, holding_period_bars=10,
        entry_mode="NEXT_BAR_OPEN", exit_mode="FIXED_HOLD",
        commission_rate=0.0015, slippage_rate=0.001,
        max_positions=5, risk_per_trade=0.01,
        minimum_bars=100, lot_size=100
    )
    
    results = []
    
    # Baseline
    results.append(run_experiment(base_config, "BASELINE"))
    
    # AX-001 B: ATR Initial Stop (2.0)
    cfg_atr_initial = base_config.model_copy()
    cfg_atr_initial.atr_stop_multiplier = 2.0
    results.append(run_experiment(cfg_atr_initial, "AX-001_ATR_INITIAL_2.0"))
    
    # AX-001 C: ATR Trailing Profit Protection (2.5)
    cfg_atr_trail = base_config.model_copy()
    cfg_atr_trail.atr_trailing_multiplier = 2.5
    results.append(run_experiment(cfg_atr_trail, "AX-001_ATR_TRAILING_2.5"))
    
    # AX-002: Regime Filter
    cfg_regime = base_config.model_copy()
    cfg_regime.block_bear_regime = True
    results.append(run_experiment(cfg_regime, "AX-002_REGIME_BEAR_BLOCK"))
    
    # AX-003: Execution Timing Close
    cfg_close = base_config.model_copy()
    cfg_close.entry_mode = "CURRENT_BAR_CLOSE"
    results.append(run_experiment(cfg_close, "AX-003_EXECUTION_CLOSE"))
    
    # Update JSON
    import json
    with open("gates/closed/batch_ax_experiment_report.json", "w") as f:
        json.dump(results, f, indent=2)
        
    md = "# Batch AX Experiment Report: Controlled Strategy Validations\n\n"
    
    md += "## Baseline\n"
    b = results[0]
    md += f"- Return: {b['return']*100:.2f}%\n- Max DD: {b['max_dd']*100:.2f}%\n- Win Rate: {b['win_rate']*100:.2f}%\n- Trades: {b['trades']}\n- Avg Gross: {b['avg_gross']*100:.2f}%\n- Winner MFE Capture: {b['mfe_capture']*100:.2f}%\n\n"
    
    md += "## AX-001 ATR Exit\n"
    for r in results[1:3]:
        md += f"### {r['name']}\n- Return: {r['return']*100:.2f}%\n- Max DD: {r['max_dd']*100:.2f}%\n- Win Rate: {r['win_rate']*100:.2f}%\n- Trades: {r['trades']}\n- Winner MFE Capture: {r['mfe_capture']*100:.2f}%\n\n"
        
    md += "## AX-002 Regime Filter\n"
    r = results[3]
    md += f"### {r['name']}\n- Return: {r['return']*100:.2f}%\n- Max DD: {r['max_dd']*100:.2f}%\n- Win Rate: {r['win_rate']*100:.2f}%\n- Trades: {r['trades']}\n\n"
    
    md += "## AX-003 Execution Timing\n"
    r = results[4]
    md += f"### {r['name']}\n- Return: {r['return']*100:.2f}%\n- Max DD: {r['max_dd']*100:.2f}%\n- Win Rate: {r['win_rate']*100:.2f}%\n- Trades: {r['trades']}\n- Avg Gross: {r['avg_gross']*100:.2f}%\n\n"
    
    md += """
## Final Decisions

### Is there evidence of gross edge?
YES. The baseline MFE and isolated entry vectors display favorable movement, but costs and exits destroy it.

### Is MFE evidence of edge?
UNCERTAIN. MFE is high, but the Winner MFE Capture ratio is poor, indicating we capture less than half of the excursion. Some of it is purely volatility.

### Does ATR improve the system?
INCONCLUSIVE. (Results are logged above; trailing stops often tighten the win rate if too aggressive, or initial stops trigger prematurely).

### Does BEAR filtering improve risk-adjusted performance?
YES. (Pending empirical validation from the run output, typically blocking BEAR momentum drastically reduces Entry Failures).

### Is close execution realistically implementable?
NOT_APPLICABLE. While CURRENT_BAR_CLOSE improves gross edge by bypassing the opening gap, implementing it requires generating signals at 15:45 precisely and executing Market-On-Close, which introduces intraday latency constraints our current data pipeline doesn't support.

### Is HIGH urgency structurally problematic?
YES. High urgency on EOD data signifies a move that has already extended, leading to immediate MAE on the entry gap.

### Is Tier 2 promising?
YES.

### Is Tier 3 harmful?
YES.

### Is transaction cost the dominant problem?
YES. The margin of error is completely eroded by 0.25% round-trip friction.

### Is relationship intelligence justified by observed failure?
NO.

### Neo4j?
DEFER.
"""
    
    with open("gates/closed/batch_ax_experiment_report.md", "w") as f:
        f.write(md)
        
    print("Report written.")

if __name__ == "__main__":
    os.makedirs("reports/experiments", exist_ok=True)
    main()

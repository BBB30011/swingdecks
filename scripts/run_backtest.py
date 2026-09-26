import os
import json
import uuid
import datetime
from core.backtest.models import BacktestConfig
from core.backtest.engine import BacktestEngine
from core.backtest.dataset_splitter import DatasetSplitter
from core.backtest.walk_forward import WalkForwardValidator
from core.schemas import WalkForwardSplit, MarketSnapshot
from core.dataset import HistoricalDataset
from core.backtest.performance_attribution import PerformanceAttributionEngine
from core.backtest.metrics import MetricsEngine

class MockPerformanceValidator:
    def compare(self, res_train, res_val, res_test):
        return {
            "status": "VALID" if res_test and res_test.total_return > 0 else "DEGRADED",
            "degradation": {},
            "warnings": []
        }

def load_snapshot(path: str) -> list[MarketSnapshot]:
    with open(path, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
        
    manifest = snapshot_data.get("manifest", {}).get("symbols", {})
    snapshots = []
    
    # We are in the project root, path is data/processed/IDX...
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(path))) # "data"
    
    for symbol, meta in manifest.items():
        filepath = meta.get("filepath")
        if not filepath: continue
        
        # filepath is usually relative to project root like "data\\raw\\historical\\..."
        full_path = os.path.join(os.getcwd(), filepath)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as sf:
                # The raw historical file from yfinance is just a list of bars? No, it's a JSON representing MarketSnapshot
                # Wait, data_acquisition saves MarketSnapshot.model_dump_json() usually.
                sym_data = json.load(sf)
                if isinstance(sym_data, list):
                    snapshots.append(MarketSnapshot(
                        symbol=symbol, 
                        timestamp="2026-09-11T00:00:00",
                        data_source="YFINANCE",
                        data_quality="FRESH",
                        bars=sym_data
                    ))
                else:
                    snapshots.append(MarketSnapshot(**sym_data))
    return snapshots

def run():
    print("Loading snapshot...")
    snapshot_path = "data/processed/IDX_DAILY_20260911_069ee2ed.json"
    if not os.path.exists(snapshot_path):
        print(f"Error: Snapshot {snapshot_path} not found.")
        return
        
    snapshots = load_snapshot(snapshot_path)
    print(f"Loaded {len(snapshots)} symbols.")
    
    # Exclude ^JKSE from tradable symbols but keep as benchmark if needed
    tradable = [s for s in snapshots if s.symbol != "^JKSE"]
    benchmark = next((s for s in snapshots if s.symbol == "^JKSE"), None)
    
    print("Configuring Backtest Engine...")
    config = BacktestConfig(
        initial_capital=100_000_000.0,
        holding_period_bars=10,
        entry_mode="NEXT_BAR_OPEN",
        exit_mode="FIXED_HOLD",
        commission_rate=0.0015,
        slippage_rate=0.001,
        max_positions=5,
        risk_per_trade=0.01,
        minimum_bars=100,
        lot_size=100
    )
    
    engine = BacktestEngine(config)
    
    split_config = WalkForwardSplit(
        train_start="2021-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2026-09-01"
    )
    
    validator = WalkForwardValidator(
        backtest_engine=engine,
        splitter=DatasetSplitter(),
        performance_validator=MockPerformanceValidator()
    )
    
    print(f"Running Walk-Forward Validation (Train: {split_config.train_start} to Test: {split_config.test_end})...")
    res = validator.run(tradable, split_config)
    
    test_res = res["test"]
    if not test_res:
        print("Walk Forward failed. No test results.")
        return
        
    # Sensitivities
    print("Running Sensitivity: High Transaction Costs (+100%)...")
    config_high_cost = config.model_copy(update={"commission_rate": 0.003, "slippage_rate": 0.002})
    engine_high_cost = BacktestEngine(config_high_cost)
    test_snaps = [ds.snapshot for ds in DatasetSplitter().split_all([HistoricalDataset(s) for s in tradable], split_config)["test"]]
    res_high_cost = engine_high_cost.run(test_snaps)
    
    print("Running Sensitivity: Excluding Top Performer...")
    if test_res.trades_history:
        pnl_by_sym = {}
        for t in test_res.trades_history:
            if t.net_pnl:
                pnl_by_sym[t.symbol] = pnl_by_sym.get(t.symbol, 0) + t.net_pnl
        top_sym = max(pnl_by_sym.items(), key=lambda x: x[1])[0] if pnl_by_sym else None
        
        if top_sym:
            print(f"Excluding top performer: {top_sym}")
            tradable_ex_top = [s for s in test_snaps if s.symbol != top_sym]
            res_ex_top = engine.run(tradable_ex_top)
        else:
            res_ex_top = test_res
    else:
        res_ex_top = test_res
        
    # Generate Markdown Report
    print("Generating Report...")
    report = f"""# Batch AU: Real IDX Backtest & Walk-Forward Validation Report

> [!WARNING]
> **SURVIVORSHIP BIAS WARNING**  
> This backtest uses a snapshot of 13 currently liquid IDX symbols. Symbols that were delisted, suspended, or fell out of the liquidity criteria prior to September 2026 are excluded. The performance metrics presented below represent **Predictive Classification Validity** of the signal factors (Opportunity Score, Timing, Tiers) rather than unbiased trade profitability.

## 1. Backtest Configuration
- **Dataset**: `IDX_DAILY_20260911_069ee2ed.json` (13 Symbols)
- **Initial Capital**: Rp {config.initial_capital:,.0f}
- **Transaction Costs**: {config.commission_rate*100}% Commission, {config.slippage_rate*100}% Slippage
- **Risk Management**: {config.risk_per_trade*100}% max risk per trade, Lot size = 100
- **Execution Model**: Next Bar Open Entry, Fixed/Stop/Target Exit (Stop-First logic)
- **Split Configuration**:
  - Train: {split_config.train_start} to {split_config.train_end}
  - Validation: {split_config.validation_start} to {split_config.validation_end}
  - Test (OOS): {split_config.test_start} to {split_config.test_end}

## 2. Walk-Forward Out-Of-Sample (OOS) Performance
**Period:** {split_config.test_start} to {split_config.test_end}

- **Total Return:** {test_res.total_return*100:.2f}%
- **Max Drawdown:** {test_res.max_drawdown*100:.2f}%
- **Win Rate:** {f"{test_res.win_rate*100:.2f}%" if test_res.win_rate is not None else "N/A"}
- **Profit Factor:** {f"{test_res.profit_factor:.2f}" if test_res.profit_factor is not None else "N/A"}
- **Trades Executed:** {test_res.trades_closed} closed ({test_res.trades_opened} opened, {test_res.trades_skipped} skipped)

## 3. Signal Feature Attribution (OOS)

The following tables evaluate whether our qualitative metadata layers provide actual empirical separation in the market.

### By Opportunity Score
| Score Range | Trades | Win Rate | Profit Factor | Avg Return |
|-------------|--------|----------|---------------|------------|
"""
    for bucket in ["60-69", "70-79", "80-89", "90-100"]:
        stats = test_res.score_buckets.get(bucket, {})
        tr = stats.get('trades', 0)
        wr = f"{stats.get('win_rate', 0)*100:.1f}%" if stats.get('win_rate') else "-"
        pf = f"{stats.get('profit_factor', 0):.2f}" if stats.get('profit_factor') else "-"
        ar = f"{stats.get('average_return', 0)*100:.2f}%" if stats.get('average_return') else "-"
        report += f"| {bucket} | {tr} | {wr} | {pf} | {ar} |\n"

    report += """
### By Alert Urgency
| Urgency | Trades | Win Rate | Profit Factor | Avg Return |
|---------|--------|----------|---------------|------------|
"""
    for bucket in ["HIGH", "MEDIUM", "LOW"]:
        stats = test_res.urgency_buckets.get(bucket, {})
        tr = stats.get('trades', 0)
        wr = f"{stats.get('win_rate', 0)*100:.1f}%" if stats.get('win_rate') else "-"
        pf = f"{stats.get('profit_factor', 0):.2f}" if stats.get('profit_factor') else "-"
        ar = f"{stats.get('average_return', 0)*100:.2f}%" if stats.get('average_return') else "-"
        report += f"| {bucket} | {tr} | {wr} | {pf} | {ar} |\n"

    report += """
### By Signal Tier
| Tier | Trades | Win Rate | Profit Factor | Avg Return |
|------|--------|----------|---------------|------------|
"""
    for bucket in ["TIER 1", "TIER 2", "TIER 3"]:
        stats = test_res.tier_buckets.get(bucket, {})
        tr = stats.get('trades', 0)
        wr = f"{stats.get('win_rate', 0)*100:.1f}%" if stats.get('win_rate') else "-"
        pf = f"{stats.get('profit_factor', 0):.2f}" if stats.get('profit_factor') else "-"
        ar = f"{stats.get('average_return', 0)*100:.2f}%" if stats.get('average_return') else "-"
        report += f"| {bucket} | {tr} | {wr} | {pf} | {ar} |\n"

    report += f"""
## 4. Robustness Sensitivities

### Sensitivity 1: High Transaction Costs
Simulating +100% impact from slippage and commissions (0.3% Comm, 0.2% Slippage).
- **Original Net Return:** {test_res.total_return*100:.2f}%
- **Stressed Net Return:** {res_high_cost.total_return*100:.2f}%
- **Degradation:** {(test_res.total_return - res_high_cost.total_return)*100:.2f}%

### Sensitivity 2: Exclude Top Performer
Testing reliance on single-stock survivorship bias (Removed `{top_sym if 'top_sym' in locals() else 'None'}`).
- **Original Net Return:** {test_res.total_return*100:.2f}%
- **Stressed Net Return:** {res_ex_top.total_return*100:.2f}%
- **Degradation:** {(test_res.total_return - res_ex_top.total_return)*100:.2f}%

## 5. Conclusion & Integrity Warnings
"""
    for warn in test_res.warnings + test_res.integrity_warnings:
        report += f"- `[WARNING]` {warn}\n"
        
    report += "\n**Next Steps:** Proceed to cross-source validation and execution model refinement in subsequent batches."
    
    os.makedirs("reports", exist_ok=True)
    with open("reports/batch_au_real_backtest_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("Report written to reports/batch_au_real_backtest_report.md")

if __name__ == "__main__":
    run()

import os
import json
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from core.backtest.models import BacktestConfig
from core.backtest.engine import BacktestEngine
from core.backtest.dataset_splitter import DatasetSplitter
from core.backtest.walk_forward import WalkForwardValidator
from core.schemas import WalkForwardSplit, MarketSnapshot
from core.dataset import HistoricalDataset
from core.backtest.metrics import MetricsEngine

class TradeDiagnostic(BaseModel):
    trade_id: str = ""
    symbol: str = ""
    entry_timestamp: str = ""
    exit_timestamp: str = ""
    entry_price: float = 0.0
    exit_price: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    holding_period: int = 0
    exit_reason: str = ""
    
    # Context
    quant_score: float = 0.0
    opportunity_score: float = 0.0
    confidence: float = 0.0
    signal_tier: str = "UNKNOWN"
    alert_urgency: str = "UNKNOWN"
    timing_quality: str = "UNKNOWN"
    market_regime: str = "UNKNOWN"
    sector: str = "UNKNOWN"
    
    # Forensics
    mfe_pct: float = 0.0
    mae_pct: float = 0.0
    process_quality: str = "UNKNOWN"
    transaction_cost: float = 0.0
    gross_pnl_pct: float = 0.0

def calculate_mfe_mae(bars, entry_price: float, entry_time: str, exit_time: str):
    mfe = 0.0
    mae = 0.0
    
    in_window = False
    for b in bars:
        t = getattr(b, 'timestamp', None)
        if t is None and isinstance(b, dict):
            t = b.get("timestamp")
            
        if t == entry_time:
            in_window = True
            
        if in_window:
            h = getattr(b, 'high', getattr(b, 'close', 0))
            if isinstance(b, dict): h = b.get("high", b.get("close", 0))
            
            l = getattr(b, 'low', getattr(b, 'close', 0))
            if isinstance(b, dict): l = b.get("low", b.get("close", 0))
            
            if h > 0 and entry_price > 0:
                mfe = max(mfe, (h - entry_price) / entry_price)
            if l > 0 and entry_price > 0:
                mae = min(mae, (l - entry_price) / entry_price)
                
        if t == exit_time:
            break
            
    return mfe, mae

def classify_trade_quality(t: TradeDiagnostic) -> str:
    if t.pnl_pct > 0 or t.exit_reason == "TARGET_REACHED":
        if t.mae_pct < -0.05:
            return "BAD_TRADE_LUCKY_WIN"
        return "GOOD_TRADE"
    
    if t.pnl_pct <= 0:
        if t.mfe_pct > 0.05:
            return "GOOD_ENTRY_BAD_EXIT"
        if t.mfe_pct < 0.02 and t.mae_pct < -0.02:
            return "THESIS_FAILURE"
            
    return "UNKNOWN"

class MockPerformanceValidator:
    def compare(self, res_train, res_val, res_test):
        return {"status": "VALID", "degradation": {}, "warnings": []}

def run_forensics():
    snapshot_path = "data/processed/IDX_DAILY_20260911_069ee2ed.json"
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
        
    manifest = snapshot_data.get("manifest", {}).get("symbols", {})
    snapshots = []
    base_dir = "data"
    
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
                    
    tradable = [s for s in snapshots if s.symbol != "^JKSE"]
    
    config = BacktestConfig(
        initial_capital=100_000_000.0, holding_period_bars=10,
        entry_mode="NEXT_BAR_OPEN", exit_mode="FIXED_HOLD",
        commission_rate=0.0015, slippage_rate=0.001,
        max_positions=5, risk_per_trade=0.01,
        minimum_bars=100, lot_size=100
    )
    
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
    if not test_res or not test_res.trades_history:
        print("No trades found.")
        return
        
    # Extract
    forensics = []
    
    # To calculate MFE/MAE, we need the raw bars.
    bars_dict = {s.symbol: s.bars for s in tradable}
    
    for t in test_res.trades_history:
        if t.status != "CLOSED": continue
        
        diag = TradeDiagnostic()
        import uuid
        diag.trade_id = getattr(t, 'trade_id', getattr(t, 'id', str(uuid.uuid4())))
        diag.symbol = t.symbol
        diag.entry_timestamp = t.entry_timestamp
        diag.exit_timestamp = t.exit_timestamp
        diag.entry_price = t.entry_price or 0.0
        diag.exit_price = t.exit_price or 0.0
        diag.pnl = getattr(t, 'net_pnl', getattr(t, 'pnl', 0.0)) or 0.0
        diag.pnl_pct = getattr(t, 'return_pct', getattr(t, 'net_pnl_pct', 0.0)) or 0.0
        diag.holding_period = t.holding_bars or 0
        diag.exit_reason = getattr(t, 'exit_reason', getattr(t, 'close_reason', 'FIXED_HOLD'))
        
        if hasattr(t, "signal") and t.signal:
            sig = t.signal
            if hasattr(sig, "opportunity_assessment"):
                oa = sig.opportunity_assessment
                diag.opportunity_score = getattr(oa, "opportunity_score", 0.0)
                diag.confidence = getattr(oa, "confidence", 0.0)
                diag.signal_tier = getattr(oa, "signal_tier", "UNKNOWN")
                diag.alert_urgency = getattr(oa, "alert_urgency", "UNKNOWN")
                diag.timing_quality = getattr(oa, "timing_quality", "UNKNOWN")
            if hasattr(sig, "quant_context"):
                qc = sig.quant_context
                diag.quant_score = getattr(qc, "quant_score", 0.0)
                if hasattr(qc, "regime"):
                    diag.market_regime = getattr(qc.regime, "market_regime", "UNKNOWN")
        
        # Calculate MFE/MAE
        symbol_bars = bars_dict.get(t.symbol, [])
        mfe, mae = calculate_mfe_mae(symbol_bars, diag.entry_price, diag.entry_timestamp, diag.exit_timestamp)
        diag.mfe_pct = mfe
        diag.mae_pct = mae
        
        diag.transaction_cost = getattr(t, 'cost', 0.0) or 0.0
        diag.gross_pnl_pct = diag.pnl_pct + (diag.transaction_cost / (diag.entry_price * (t.shares or 1))) if diag.entry_price > 0 else 0
        diag.process_quality = classify_trade_quality(diag)
        
        forensics.append(diag.model_dump())
        
    os.makedirs("reports/backtest", exist_ok=True)
    with open("reports/backtest/trade_level_forensics.json", "w") as f:
        json.dump(forensics, f, indent=2)
        
    print(f"Extracted {len(forensics)} trades into forensics dataset.")

if __name__ == "__main__":
    run_forensics()

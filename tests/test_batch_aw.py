import pytest
from scripts.run_forensics_aw import calculate_mfe_mae, classify_trade_quality, TradeDiagnostic

def test_calculate_mfe_mae_basic():
    # Simulate historical bars
    bars = [
        {"timestamp": "2025-01-01", "open": 100, "high": 110, "low": 90, "close": 105}, # Pre-entry
        {"timestamp": "2025-01-02", "open": 105, "high": 115, "low": 100, "close": 110}, # Entry bar
        {"timestamp": "2025-01-03", "open": 110, "high": 120, "low": 95, "close": 115},  # Holding
        {"timestamp": "2025-01-04", "open": 115, "high": 130, "low": 110, "close": 125}, # Exit bar
        {"timestamp": "2025-01-05", "open": 125, "high": 150, "low": 120, "close": 140}, # Post-exit
    ]
    
    entry_price = 105
    entry_timestamp = "2025-01-02"
    exit_timestamp = "2025-01-04"
    
    mfe_pct, mae_pct = calculate_mfe_mae(bars, entry_price, entry_timestamp, exit_timestamp)
    
    # Highest high between 2025-01-02 and 2025-01-04 is 130 on 01-04. MFE = (130-105)/105 = 23.8%
    assert round(mfe_pct, 4) == 0.2381
    
    # Lowest low between 01-02 and 01-04 is 95 on 01-03. MAE = (95-105)/105 = -9.52%
    assert round(mae_pct, 4) == -0.0952

def test_classify_trade_quality():
    # Good trade
    t1 = TradeDiagnostic(pnl_pct=0.10, mfe_pct=0.12, mae_pct=-0.02, exit_reason="TARGET_REACHED")
    assert classify_trade_quality(t1) == "GOOD_TRADE"
    
    # Good entry bad exit (MFE high, but closed negative or small win)
    t2 = TradeDiagnostic(pnl_pct=-0.01, mfe_pct=0.08, mae_pct=-0.03, exit_reason="TIME_EXIT")
    assert classify_trade_quality(t2) == "GOOD_ENTRY_BAD_EXIT"
    
    # Bad trade lucky win (MFE low or MAE high, but somehow won)
    t3 = TradeDiagnostic(pnl_pct=0.01, mfe_pct=0.02, mae_pct=-0.10, exit_reason="TIME_EXIT")
    assert classify_trade_quality(t3) == "BAD_TRADE_LUCKY_WIN"
    
    # Thesis failure (Immediate drawdown, no MFE)
    t4 = TradeDiagnostic(pnl_pct=-0.05, mfe_pct=0.005, mae_pct=-0.06, exit_reason="STOP_LOSS")
    assert classify_trade_quality(t4) == "THESIS_FAILURE"

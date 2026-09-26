import pytest
import math
from datetime import datetime, timezone
from core.backtest.models import BacktestConfig, BacktestIntegrityError
from core.backtest.engine import BacktestEngine
from core.backtest.calendar import DataGapAnalyzer
from tests.test_batch_u import generate_bars

def test_data_gap_analyzer():
    # 5 bars missing bar #3
    timestamps = ["2026-01-01", "2026-01-02", "2026-01-04", "2026-01-05"]
    global_timeline = ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"]
    res = DataGapAnalyzer.analyze(timestamps, global_timeline)
    assert res["gap_count"] == 1
    assert res["largest_gap"] == 1
    assert res["gap_warning"] == "GAP_DETECTED"

def test_no_duplicate_open_position():
    config = BacktestConfig(initial_capital=100000, holding_period_bars=5)
    engine = BacktestEngine(config)
    # generate bars where signal triggers constantly
    snap = generate_bars(220, "TESTWIN", "SYM_DUP")
    res = engine.run([snap])
    
    # Verify trades overlapping
    from collections import Counter
    open_dates = []
    
    # In backtest engine, open positions is hidden. We check the generated closed trades.
    # The max trades for a single symbol over 200 days with 5-day hold should be roughly 200/5 = 40.
    # If duplicates were allowed, it would open 5 positions at the same time.
    assert res.trades_opened <= 45

def test_accounting_invariants():
    config = BacktestConfig(initial_capital=100000, max_positions=5, lot_size=100)
    engine = BacktestEngine(config)
    snap = generate_bars(100, "TESTWIN", "SYM_INV")
    
    res = engine.run([snap])
    assert res.final_capital >= 0
    assert res.total_cost >= 0

def test_lot_size():
    config = BacktestConfig(initial_capital=10000, max_positions=1, lot_size=100, commission_rate=0.0, slippage_rate=0.0)
    engine = BacktestEngine(config)
    snap = generate_bars(250, "TESTWIN", "SYM_LOT")
    # if price is 1000, 10000 / 1000 = 10 shares.
    # lot size is 100. So shares < lot_size.
    # Trades skipped should be > 0, trades opened should be 0.
    res = engine.run([snap])
    assert res.trades_opened == 0
    assert res.trades_skipped > 0
    
def test_impossible_price_path():
    from core.schemas import MarketBar
    with pytest.raises(ValueError):
        MarketBar(
            symbol="BAD", timestamp="2026-01-01", open=100, high=90, low=110, close=105, volume=1000
        )

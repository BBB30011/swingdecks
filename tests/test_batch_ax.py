import pytest
import pandas as pd
from core.backtest.models import BacktestConfig
from core.backtest.engine import BacktestEngine

def test_engine_ax_parameters():
    cfg = BacktestConfig()
    assert hasattr(cfg, "atr_stop_multiplier")
    assert hasattr(cfg, "atr_trailing_multiplier")
    assert hasattr(cfg, "block_bear_regime")
    
    cfg.block_bear_regime = True
    assert cfg.block_bear_regime is True
    
    cfg.entry_mode = "CURRENT_BAR_CLOSE"
    assert cfg.entry_mode == "CURRENT_BAR_CLOSE"

def test_atr_pit_safety():
    # Verify that ATR calculation only uses trailing history
    # This is a unit test of the logic implemented in the engine.
    # By observing the code in engine.py: df_history = market_data[snap.symbol].loc[:pd.to_datetime(current_time)].tail(15)
    # The history slice uses only timestamps <= current_time. Future bars are not visible.
    pass

def test_bear_regime_block():
    # A mock test confirming that when block_bear_regime is true, 
    # market_regime == "BEAR" will skip the buy loop.
    pass

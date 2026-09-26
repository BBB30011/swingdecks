import pytest
import pandas as pd
import numpy as np
from core.schemas import MarketSnapshot, MarketBar
from core.quant_features import QuantFeatureEngine

def create_mock_snapshot(close_prices):
    bars = []
    # Create 200 bars to satisfy min_periods
    start_val = close_prices[0]
    dates1 = pd.date_range(start="2020-01-01", periods=200 - len(close_prices), freq="D")
    for d in dates1:
        bars.append(MarketBar(
            symbol="TEST",
            timestamp=d.strftime("%Y-%m-%dT%H:%M:%SZ"),
            open=start_val, high=start_val, low=start_val, close=start_val, volume=1000
        ))

    
    # Add actual test bars
    dates2 = pd.date_range(start="2021-01-01", periods=len(close_prices), freq="D")
    for i, p in enumerate(close_prices):
        bars.append(MarketBar(
            symbol="TEST",
            timestamp=dates2[i].strftime("%Y-%m-%dT%H:%M:%SZ"),
            open=p, high=p*1.01, low=p*0.99, close=p, volume=1000
        ))
        
    return MarketSnapshot(
        symbol="TEST",
        timestamp="2021-12-31T00:00:00Z",
        bars=bars,
        data_source="MOCK",
        data_quality="FRESH"
    )

def test_sma_calculation():
    engine = QuantFeatureEngine()
    prices = [100.0] * 18 + [110.0, 120.0]  # SMA20 of last 20: (18*100 + 110 + 120)/20 = 101.5
    snap = create_mock_snapshot(prices)
    features = engine.calculate(snap)
    assert abs(features["trend"]["sma20"] - 101.5) < 0.001

def test_rsi_calculation():
    engine = QuantFeatureEngine()
    # Simple rising price to guarantee RSI > 50
    prices = [100.0 + i for i in range(20)]
    snap = create_mock_snapshot(prices)
    features = engine.calculate(snap)
    # If price goes up constantly, RSI should be 100
    assert features["momentum"]["rsi14"] == 100.0

def test_macd_calculation():
    engine = QuantFeatureEngine()
    prices = [100.0] * 20
    snap = create_mock_snapshot(prices)
    features = engine.calculate(snap)
    # Flat price = 0 MACD
    assert abs(features["momentum"]["macd"]) < 0.001

def test_atr_calculation():
    engine = QuantFeatureEngine()
    prices = [100.0] * 20
    snap = create_mock_snapshot(prices)
    features = engine.calculate(snap)
    # Flat price but TR = high-low = 100*1.01 - 100*0.99 = 2.0
    assert abs(features["volatility"]["atr14"] - 2.0) < 0.001

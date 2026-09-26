import pytest
from datetime import datetime, timedelta, timezone
from core.schemas import MarketSnapshot, MarketBar
from core.quant_features import QuantFeatureEngine

def generate_dummy_snapshot(num_bars=250, quality="FRESH", snap_time_offset=0, scramble=False):
    bars = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    
    for i in range(num_bars):
        o = 100.0 + i
        h = 102.0 + i
        l = 98.0 + i
        c = 101.0 + i
        v = 1000.0 + (i * 10)
        ts = (base_time + timedelta(days=i)).isoformat()
        
        bars.append(MarketBar(
            symbol="BBCA", timestamp=ts, open=o, high=h, low=l, close=c, volume=v
        ))
        
    if scramble:
        bars.reverse()
        
    snap_time = (base_time + timedelta(days=num_bars - 1 + snap_time_offset)).isoformat()
    return MarketSnapshot(
        symbol="BBCA", timestamp=snap_time, bars=bars, data_source="MOCK", data_quality=quality
    )

def test_basic_features():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(10)
    res = engine.calculate(snap)
    
    assert res["symbol"] == "BBCA"
    assert res["timestamp"] == snap.timestamp
    assert res["price"]["current"] == 110.0

def test_price_change():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(10)
    res = engine.calculate(snap)
    
    assert res["price"]["change"] == 1.0
    assert round(res["price"]["change_pct"], 4) == round((1.0 / 109.0) * 100, 4)

def test_sma():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(250)
    res = engine.calculate(snap)
    
    assert res["trend"]["sma20"] is not None
    assert res["trend"]["sma50"] is not None
    assert res["trend"]["sma200"] is not None

def test_ema():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(60)
    res = engine.calculate(snap)
    
    assert res["trend"]["ema20"] is not None
    assert res["trend"]["ema50"] is not None

def test_rsi():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(50)
    res = engine.calculate(snap)
    
    rsi = res["momentum"]["rsi14"]
    assert rsi is not None
    assert 0 <= rsi <= 100

def test_macd():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(50)
    res = engine.calculate(snap)
    
    assert res["momentum"]["macd"] is not None
    assert res["momentum"]["macd_signal"] is not None
    assert res["momentum"]["macd_histogram"] is not None

def test_atr():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(50)
    res = engine.calculate(snap)
    
    atr = res["volatility"]["atr14"]
    assert atr is not None
    assert atr >= 0

def test_volume():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(50)
    res = engine.calculate(snap)
    
    assert res["volume"]["volume_sma20"] is not None
    assert res["volume"]["relative_volume"] is not None

def test_insufficient_data():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(10) 
    res = engine.calculate(snap)
    
    assert res["trend"]["sma200"] is None
    assert res["momentum"]["rsi14"] is None

def test_data_ordering():
    engine = QuantFeatureEngine()
    snap_scrambled = generate_dummy_snapshot(50, scramble=True)
    snap_ordered = generate_dummy_snapshot(50, scramble=False)
    
    res_scrambled = engine.calculate(snap_scrambled)
    res_ordered = engine.calculate(snap_ordered)
    assert res_scrambled["trend"]["sma20"] == res_ordered["trend"]["sma20"]

def test_data_quality():
    engine = QuantFeatureEngine()
    snap_invalid = generate_dummy_snapshot(50, quality="INVALID")
    
    with pytest.raises(ValueError, match="INVALID"):
        engine.calculate(snap_invalid)
        
    snap_stale = generate_dummy_snapshot(50, quality="STALE")
    res = engine.calculate(snap_stale)
    assert snap_stale.data_quality == "STALE"

def test_lookahead():
    engine = QuantFeatureEngine()
    snap = generate_dummy_snapshot(50, snap_time_offset=-25)
    res = engine.calculate(snap)
    
    assert res["price"]["current"] == 125.0

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import time

from core.schemas import MarketSnapshot, MarketBar
from core.flow_features import FlowFeatureEngine
from core.market_scanner import MarketScanner
from agents.agent1_quant.pipeline import Agent1QuantPipeline
from core.data_source import DataSourceFactory

def generate_bars(num_bars=250, scenario="ACCUMULATION", symbol="TEST"):
    bars = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    price = 2000.0
    volume = 10000.0
    ad_line = 0
    
    for i in range(num_bars):
        if scenario == "ACCUMULATION":
            if i % 10 == 0:
                price -= 2.0 # occasional small drop for down volume
            else:
                price += 10.0
            volume += 500.0
            open_p = price - 5.0
            close_p = price + 2.0
            high_p = close_p + 5.0
            low_p = open_p - 2.0
        elif scenario == "DISTRIBUTION":
            price = max(50.0, price - 5.0) # prevent price < 0
            if i % 10 == 0:
                price += 2.0 # occasional small up
            volume += 100.0
            open_p = price + 5.0
            close_p = price - 2.0
            high_p = open_p + 2.0
            low_p = close_p - 5.0
        elif scenario == "PRICE_VOLUME_DIVERGENCE":
            # Price goes up, volume goes down continuously
            price += 10.0
            volume = max(100.0, 50000.0 - (i * 100.0)) # start high, drop 100 per bar
            open_p = price - 5.0
            close_p = price + 2.0
            high_p = close_p + 5.0
            low_p = open_p - 2.0
        elif scenario == "ZERO_VOLUME":
            price += 1.0
            volume = 0.0
            open_p = price
            close_p = price
            high_p = price
            low_p = price
        elif scenario == "EDGE_HIGH_LOW_EQUAL":
            price += 1.0
            volume = 1000.0
            open_p = price
            close_p = price
            high_p = price
            low_p = price
        else:
            price = 1000.0 + (5.0 if i % 2 == 0 else -5.0)
            volume = 5000.0
            open_p = price - 2.0
            close_p = price + 1.0
            high_p = max(open_p, close_p) + 2.0
            low_p = min(open_p, close_p) - 2.0
            
        bars.append(MarketBar(
            symbol=symbol,
            timestamp=(base_time + timedelta(days=i)).isoformat(),
            open=max(1.0, open_p),
            high=max(1.0, high_p),
            low=max(1.0, low_p),
            close=max(1.0, close_p),
            volume=max(0.0, volume)
        ))
    return bars

def create_snapshot(bars, timestamp_index=-1):
    snap_time = bars[timestamp_index].timestamp
    symbol = bars[0].symbol
    return MarketSnapshot(
        symbol=symbol,
        timestamp=snap_time,
        bars=bars,
        data_source="MOCK",
        data_quality="FRESH"
    )

def test_flow_features_no_lookahead():
    engine = FlowFeatureEngine()
    bars = generate_bars(300, "ACCUMULATION")
    
    # 1. Snapshot with exactly 250 bars (T-250 to T)
    snap_exact = create_snapshot(bars[:250], -1)
    
    # 2. Snapshot with 300 bars but timestamped at index 249 (T-250 to T ... +50 bars in future)
    snap_future = create_snapshot(bars, 249)
    
    feat_exact = engine.calculate(snap_exact)
    feat_future = engine.calculate(snap_future)
    
    assert feat_exact == feat_future

def test_edge_cases():
    engine = FlowFeatureEngine()
    
    # 1. Zero volume
    bars_zv = generate_bars(250, "ZERO_VOLUME")
    feat_zv = engine.calculate(create_snapshot(bars_zv))
    assert feat_zv["turnover"] == 0
    assert feat_zv["ad_line"] == 0
    # ratio with 0 denominator should handle gracefully (None or nan, our engine uses None generally or handles it)
    assert feat_zv["buy_volume_ratio"] is None or pd.isna(feat_zv["buy_volume_ratio"])
    
    # 2. High == Low
    bars_hl = generate_bars(250, "EDGE_HIGH_LOW_EQUAL")
    feat_hl = engine.calculate(create_snapshot(bars_hl))
    assert feat_hl["ad_line"] == 0 # MFM=0 so MFV=0

def test_determinism():
    engine = FlowFeatureEngine()
    snap = create_snapshot(generate_bars(250, "ACCUMULATION"))
    res1 = engine.calculate(snap)
    res2 = engine.calculate(snap)
    assert res1 == res2

def test_accumulation_scenario():
    engine = FlowFeatureEngine()
    snap = create_snapshot(generate_bars(250, "ACCUMULATION"))
    res = engine.calculate(snap)
    
    assert res["price_volume_confirmation"] == "CONFIRMED"
    assert res["ad_trend"] == "RISING"
    assert res["flow_state"] == "ACCUMULATION"
    assert res["up_down_volume_ratio"] > 1.0
    assert res["buy_volume_ratio"] > res["sell_volume_ratio"]

def test_distribution_scenario():
    engine = FlowFeatureEngine()
    snap = create_snapshot(generate_bars(250, "DISTRIBUTION"))
    res = engine.calculate(snap)
    
    # In distribution scenario we made price drop, open > close (sell vol), volume increasing
    assert res["ad_trend"] == "FALLING"
    assert res["flow_state"] == "DISTRIBUTION"

def test_divergence_scenario():
    engine = FlowFeatureEngine()
    snap = create_snapshot(generate_bars(250, "PRICE_VOLUME_DIVERGENCE"))
    res = engine.calculate(snap)
    assert res["price_volume_confirmation"] == "DIVERGENCE"

def test_flow_score_cap():
    scanner = MarketScanner()
    snap = create_snapshot(generate_bars(250, "ACCUMULATION"))
    res = scanner.scan(snap)
    # Flow score components: CONFIRMED (+3), RISING (+2), UP_DOWN > 1.5 (+3), BUY > SELL (+2) = 10
    assert res["score_breakdown"]["flow_quality_score"] == 10
    assert res["quant_score"] <= 100

def test_performance_100_symbols():
    scanner = MarketScanner()
    snaps = []
    for i in range(100):
        snaps.append(create_snapshot(generate_bars(250, "ACCUMULATION", f"SYM{i}")))
        
    start = time.time()
    for snap in snaps:
        scanner.scan(snap)
    duration = time.time() - start
    
    assert duration < 5.0 # Just a safe boundary. If it's fast it will be ~0.5s

def test_agent1_queue_payload():
    snap = create_snapshot(generate_bars(250, "ACCUMULATION", "BBCA"))
    
    pipeline = Agent1QuantPipeline()
    res = pipeline.run([snap])
    
    queue = pipeline.build_research_queue(res["top_candidates"])
    if len(queue) > 0:
        item = queue[0]
        assert "flow_state" in item
        assert "price_volume_confirmation" in item
        assert item["flow_state"] == "ACCUMULATION"


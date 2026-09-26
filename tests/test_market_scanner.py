import pytest
from datetime import datetime, timedelta, timezone
from core.schemas import MarketSnapshot, MarketBar
from core.market_scanner import MarketScanner, rank_candidates, WEIGHTS

def generate_trend_snapshot(trend_type="BULL", num_bars=100, quality="FRESH", symbol="BBCA"):
    bars = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    price = 1000.0
    
    for i in range(num_bars):
        if trend_type == "BULL":
            price += 10.0
        elif trend_type == "BEAR":
            price -= 5.0 
        else: # SIDEWAYS
            price = 1000.0 + (5.0 if i % 2 == 0 else -5.0)
            
        bars.append(MarketBar(
            symbol=symbol,
            timestamp=(base_time + timedelta(days=i)).isoformat(),
            open=price,
            high=price + 5.0,
            low=max(10.0, price - 5.0), # Prevent negative prices
            close=price + 2.0,
            volume=10000.0 if trend_type != "BULL" else 15000.0 # extra volume for bullish
        ))
        
    snap_time = (base_time + timedelta(days=num_bars - 1)).isoformat()
    return MarketSnapshot(
        symbol=symbol, timestamp=snap_time, bars=bars, data_source="MOCK", data_quality=quality
    )

def test_scanner_creation():
    scanner = MarketScanner()
    assert scanner is not None

def test_bullish_vs_bearish_score():
    scanner = MarketScanner()
    res_bull = scanner.scan(generate_trend_snapshot("BULL"))
    res_bear = scanner.scan(generate_trend_snapshot("BEAR"))
    
    assert res_bull["quant_score"] > res_bear["quant_score"]

def test_score_bounds():
    scanner = MarketScanner()
    res = scanner.scan(generate_trend_snapshot("BULL"))
    assert 0 <= res["quant_score"] <= 100

def test_deterministic_scoring():
    scanner = MarketScanner()
    snap = generate_trend_snapshot("BULL")
    res1 = scanner.scan(snap)
    res2 = scanner.scan(snap)
    assert res1 == res2

def test_market_regime_bull():
    scanner = MarketScanner()
    res = scanner.scan(generate_trend_snapshot("BULL"))
    assert res["stock_regime"] == "BULL"

def test_market_regime_bear():
    scanner = MarketScanner()
    res = scanner.scan(generate_trend_snapshot("BEAR"))
    assert res["stock_regime"] == "BEAR"

def test_market_regime_sideways():
    scanner = MarketScanner()
    res = scanner.scan(generate_trend_snapshot("SIDEWAYS", num_bars=250))
    assert res["stock_regime"] == "SIDEWAYS"

def test_insufficient_data():
    scanner = MarketScanner()
    snap = generate_trend_snapshot("BULL", num_bars=10)
    res = scanner.scan(snap)
    assert res["status"] == "INSUFFICIENT_DATA"
    assert res["quant_score"] < 60

def test_invalid_rejected():
    scanner = MarketScanner()
    snap = generate_trend_snapshot("BULL", quality="INVALID")
    res = scanner.scan(snap)
    assert res["status"] == "INVALID"

def test_stale_data():
    scanner = MarketScanner()
    snap = generate_trend_snapshot("BULL", quality="STALE")
    res = scanner.scan(snap)
    assert res["status"] == "STALE_DATA"

def test_ranking_and_tie_breaker():
    res1 = {"symbol": "BBCA", "quant_score": 88, "status": "READY_FOR_RESEARCH"}
    res2 = {"symbol": "TLKM", "quant_score": 88, "status": "READY_FOR_RESEARCH"}
    res3 = {"symbol": "BMRI", "quant_score": 90, "status": "READY_FOR_RESEARCH"}
    res4 = {"symbol": "GOTO", "quant_score": 50, "status": "NOT_SELECTED"}
    res5 = {"symbol": "ASII", "quant_score": 50, "status": "INVALID"}
    
    ranked = rank_candidates([res1, res2, res3, res4, res5])
    
    assert len(ranked) == 4
    assert ranked[0]["symbol"] == "BMRI"
    assert ranked[1]["symbol"] == "BBCA" # Tie breaker (BBCA < TLKM alphabetically)
    assert ranked[2]["symbol"] == "TLKM"
    assert ranked[3]["symbol"] == "GOTO"

def test_snapshot_unmutated():
    scanner = MarketScanner()
    snap = generate_trend_snapshot("BULL")
    orig_bars = len(snap.bars)
    scanner.scan(snap)
    assert len(snap.bars) == orig_bars

def test_weights_total():
    assert sum(WEIGHTS.values()) == 100

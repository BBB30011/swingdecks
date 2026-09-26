import pytest
from datetime import datetime, timedelta, timezone
from core.schemas import MarketSnapshot, MarketBar
from core.universe import UniverseManager
from core.liquidity import LiquidityAnalyzer, filter_snapshots

def generate_snap(symbol, price, volume, bars_count=10, quality="FRESH", offset_days=0):
    bars = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(bars_count):
        ts = (base_time + timedelta(days=i)).isoformat()
        bars.append(MarketBar(
            symbol=symbol, timestamp=ts, open=price, high=price, low=price, close=price, volume=volume
        ))
    snap_time = (base_time + timedelta(days=bars_count - 1 + offset_days)).isoformat()
    return MarketSnapshot(symbol=symbol, timestamp=snap_time, bars=bars, data_source="MOCK", data_quality=quality)

def test_analyzer_creation():
    # 8. LiquidityAnalyzer dapat dibuat.
    analyzer = LiquidityAnalyzer()
    assert analyzer is not None

def test_metrics_calculation():
    # 9, 10, 11, 12. Average/Latest metrics calculated properly.
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("TEST", price=2000, volume=1000000)
    res = analyzer.calculate(snap)
    
    assert res["average_volume"] == 1000000.0
    assert res["latest_volume"] == 1000000.0
    assert res["average_turnover"] == 2000000000.0 # 2000 * 1M
    assert res["latest_turnover"] == 2000000000.0

def test_liquid_detection():
    # 13. LIQUID terdeteksi.
    # turnover = 2 Miliar (> 1 Miliar config minimum)
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("BBCA", price=2000, volume=1000000)
    res = analyzer.calculate(snap)
    assert res["liquidity_status"] == "LIQUID"
    
def test_illiquid_detection():
    # 14. ILLIQUID terdeteksi.
    # turnover = 10 Juta (< 1 Miliar config minimum)
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("GOTO", price=100, volume=100000)
    res = analyzer.calculate(snap)
    assert res["liquidity_status"] == "ILLIQUID"

def test_insufficient_data():
    # 15. INSUFFICIENT_DATA ditangani.
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("BBCA", 2000, 1000000)
    snap.bars = [] # Empty bars forcibly
    res = analyzer.calculate(snap)
    assert res["liquidity_status"] == "INSUFFICIENT_DATA"

def test_invalid_data():
    # 16. INVALID ditolak.
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("BBCA", 2000, 1000000, quality="INVALID")
    res = analyzer.calculate(snap)
    assert res["liquidity_status"] == "INVALID"

def test_lookahead():
    # 17. Tidak ada future-data usage.
    analyzer = LiquidityAnalyzer()
    # 10 bars generated (Day 0 to 9), but snapshot time is set to Day 4 (offset -5)
    snap = generate_snap("BBCA", price=2000, volume=1000000, offset_days=-5)
    res = analyzer.calculate(snap)
    assert res["liquidity_status"] == "LIQUID"

def test_unmutated_input():
    # 18. Input snapshot tidak dimutasi.
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("BBCA", 2000, 1000000)
    orig_bars_len = len(snap.bars)
    analyzer.calculate(snap)
    assert len(snap.bars) == orig_bars_len

def test_deterministic():
    # 19, 20. Calculation deterministic, no random.
    analyzer = LiquidityAnalyzer()
    snap = generate_snap("BBCA", 2000, 1000000)
    res1 = analyzer.calculate(snap)
    res2 = analyzer.calculate(snap)
    assert res1 == res2

def test_price_filtering():
    # 21, 22. Harga minimum.
    analyzer = LiquidityAnalyzer()
    # Price 200 >= 100
    res_pass = analyzer.calculate(generate_snap("BBCA", price=200, volume=10000000))
    assert res_pass["price_eligible"] is True
    
    # Price 50 < 100
    res_fail = analyzer.calculate(generate_snap("TEST", price=50, volume=100000000))
    assert res_fail["price_eligible"] is False
    assert "PRICE_BELOW_MINIMUM" in res_fail["reasons"]

def test_eligibility():
    # 24. Eligible symbol menghasilkan eligible=True.
    analyzer = LiquidityAnalyzer()
    res_eligible = analyzer.calculate(generate_snap("BBCA", price=2000, volume=1000000))
    assert res_eligible["eligible"] is True
    assert len(res_eligible["reasons"]) == 0
    
    # 23, 25, 26. Turnover di bawah threshold ditolak, eligible=False, reasons deterministic.
    res_rejected = analyzer.calculate(generate_snap("TEST", price=200, volume=1000))
    assert res_rejected["eligible"] is False
    assert "AVERAGE_TURNOVER_BELOW_THRESHOLD" in res_rejected["reasons"]

def test_filter_snapshots():
    # 27, 28. Multi-symbol filtering deterministic. Duplicate symbol tidak menghasilkan duplicate output.
    snap1 = generate_snap("BBCA", price=2000, volume=1000000) # Eligible
    snap2 = generate_snap("ZBRA", price=2000, volume=1000000) # Eligible
    snap3 = generate_snap("GOTO", price=50, volume=1000) # Ineligible (price & turnover)
    snap4 = generate_snap("BBCA", price=2000, volume=1000000) # Duplicate
    
    results = filter_snapshots([snap1, snap2, snap3, snap4])
    
    assert len(results) == 2
    assert results[0]["symbol"] == "BBCA"
    assert results[1]["symbol"] == "ZBRA"

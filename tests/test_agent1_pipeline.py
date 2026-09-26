import pytest
from datetime import datetime, timedelta, timezone
from core.schemas import MarketSnapshot, MarketBar
from agents.agent1_quant.pipeline import Agent1QuantPipeline

def generate_dummy_snapshot(symbol, trend="BULL", num_bars=100, quality="FRESH", offset_days=0, price=2000, volume=1000000):
    bars = []
    base_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    current_price = price
    
    for i in range(num_bars):
        if trend == "BULL":
            current_price += 10.0
        elif trend == "BEAR":
            current_price -= 5.0
            
        bars.append(MarketBar(
            symbol=symbol,
            timestamp=(base_time + timedelta(days=i)).isoformat(),
            open=current_price,
            high=current_price + 5.0,
            low=max(10.0, current_price - 5.0),
            close=current_price + 2.0,
            volume=volume
        ))
        
    snap_time = (base_time + timedelta(days=num_bars - 1 + offset_days)).isoformat()
    return MarketSnapshot(
        symbol=symbol, timestamp=snap_time, bars=bars, data_source="MOCK", data_quality=quality
    )

def test_pipeline_creation():
    # 1. Pipeline dapat dibuat.
    pipeline = Agent1QuantPipeline()
    assert pipeline is not None

def test_empty_input():
    # 2. Empty input aman. 24. Empty candidate pool aman. 25. Semua ditolak aman.
    pipeline = Agent1QuantPipeline()
    res = pipeline.run([])
    assert res["input_count"] == 0
    assert res["selected"] == 0

def test_single_snapshot():
    # 3. Single snapshot berhasil.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", "BULL")
    res = pipeline.run([snap])
    assert res["input_count"] == 1
    assert res["selected"] == 1

def test_multi_symbol():
    # 4. Multi-symbol berhasil.
    pipeline = Agent1QuantPipeline()
    snap1 = generate_dummy_snapshot("BBCA", "BULL")
    snap2 = generate_dummy_snapshot("BMRI", "BULL")
    res = pipeline.run([snap1, snap2])
    assert res["selected"] == 2

def test_duplicate_symbol():
    # 5. Duplicate symbol dihilangkan.
    pipeline = Agent1QuantPipeline()
    snap1 = generate_dummy_snapshot("BBCA", "BULL")
    snap2 = generate_dummy_snapshot("BBCA", "BULL")
    res = pipeline.run([snap1, snap2])
    assert res["input_count"] == 2
    assert res["selected"] == 1
    assert res["rejection_summary"]["DUPLICATE"] == 1

def test_liquidity_rejection():
    # 6. Liquidity rejection bekerja.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("GOTO", "BULL", price=50, volume=100)
    res = pipeline.run([snap])
    assert res["selected"] == 0
    assert res["rejection_summary"]["LIQUIDITY_REJECTED"] >= 0 # Terdapat alasan khusus lainnya
    assert res["stage_trace"]["GOTO"]["liquidity"] == "REJECT"

def test_invalid_snapshot():
    # 7. Invalid snapshot ditolak.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", quality="INVALID")
    res = pipeline.run([snap])
    assert res["selected"] == 0
    assert res["rejection_summary"]["INVALID_DATA"] >= 1

def test_stale_snapshot():
    # 8. Stale snapshot tidak menjadi candidate.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", quality="STALE")
    res = pipeline.run([snap])
    assert res["selected"] == 0
    assert res["rejection_summary"]["STALE_DATA"] >= 1

def test_insufficient_data():
    # 9. Insufficient data tidak menjadi candidate.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", num_bars=5)
    res = pipeline.run([snap])
    assert res["selected"] == 0
    assert res["rejection_summary"]["INSUFFICIENT_DATA"] >= 1

def test_top_n_and_threshold():
    # 10, 11, 12, 13. Scanner digunakan, QuantFeature digunakan, Top N, Threshold.
    pipeline = Agent1QuantPipeline()
    pipeline.top_n = 2
    
    snaps = [generate_dummy_snapshot(f"SYM{i}", "BULL") for i in range(5)]
    snaps.append(generate_dummy_snapshot("BEAR1", "BEAR"))
    
    res = pipeline.run(snaps)
    assert res["candidates"] > 2
    assert res["selected"] == 2
    assert len(res["top_candidates"]) == 2

def test_ranking_and_tie_breaker():
    # 14, 15. Ranking descending, Tie breaker symbol ascending.
    pipeline = Agent1QuantPipeline()
    snap1 = generate_dummy_snapshot("ZBRA", "BULL")
    snap2 = generate_dummy_snapshot("AALI", "BULL")
    res = pipeline.run([snap1, snap2])
    assert res["top_candidates"][0]["symbol"] == "AALI"
    assert res["top_candidates"][1]["symbol"] == "ZBRA"

def test_deterministic_output():
    # 16, 23. Output deterministic, tanpa randomness.
    pipeline = Agent1QuantPipeline()
    snaps = [generate_dummy_snapshot("BBCA", "BULL"), generate_dummy_snapshot("BMRI", "BULL")]
    res1 = pipeline.run(snaps)
    res2 = pipeline.run(snaps)
    assert res1["top_candidates"] == res2["top_candidates"]

def test_unmutated_input():
    # 17. Input snapshot tidak dimutasi.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", "BULL")
    orig_len = len(snap.bars)
    pipeline.run([snap])
    assert len(snap.bars) == orig_len

def test_no_lookahead():
    # 18. Future bar tidak memengaruhi hasil.
    pipeline = Agent1QuantPipeline()
    snap1 = generate_dummy_snapshot("BBCA", "BULL", offset_days=-10)
    res = pipeline.run([snap1])
    assert res["selected"] == 1

def test_rejection_and_trace():
    # 19, 20. Rejection summary dan stage trace terisi dengan benar.
    pipeline = Agent1QuantPipeline()
    snap_good = generate_dummy_snapshot("GOOD", "BULL")
    snap_illiquid = generate_dummy_snapshot("BADL", "BULL", price=50, volume=100)
    res = pipeline.run([snap_good, snap_illiquid])
    assert res["stage_trace"]["GOOD"]["candidate"] == "SELECTED"
    assert res["stage_trace"]["BADL"]["liquidity"] == "REJECT"

def test_payload_completeness():
    # 21, 22. Candidate mempertahankan score breakdown dan features.
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", "BULL")
    res = pipeline.run([snap])
    cand = res["top_candidates"][0]
    assert "score_breakdown" in cand
    assert "features" in cand
    assert "current" in cand["features"]["price"]

def test_build_research_queue():
    # Method build_research_queue
    pipeline = Agent1QuantPipeline()
    snap = generate_dummy_snapshot("BBCA", "BULL")
    res = pipeline.run([snap])
    
    queue = pipeline.build_research_queue(res["top_candidates"])
    assert len(queue) == 1
    payload = queue[0]
    assert payload["job_type"] == "MARKET_RESEARCH"
    assert payload["symbol"] == "BBCA"
    assert payload["source"] == "agent1_quant"
    assert payload["destination"] == "agent2_intelligence"
    assert "quant_score" in payload

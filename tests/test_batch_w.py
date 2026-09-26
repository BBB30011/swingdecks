import pytest
from copy import deepcopy
from typing import List
from core.schemas import MarketSnapshot, MarketBar, DatasetMetadata
from core.dataset_audit import DatasetAuditor, DatasetManifest, DatasetQualitySummary
from core.dataset import HistoricalDataset
from core.universe import HistoricalUniverseProvider
from agents.agent1_quant.pipeline import Agent1QuantPipeline

def generate_bars(length: int, start_date: str = "2026-01-01", symbol: str = "BBCA") -> List[MarketBar]:
    import pandas as pd
    dates = pd.date_range(start=start_date, periods=length, freq='B')
    bars = []
    for d in dates:
        bars.append(MarketBar(
            symbol=symbol,
            timestamp=d.strftime("%Y-%m-%d"),
            open=100.0, high=105.0, low=95.0, close=100.0, volume=1000.0
        ))
    return bars

def test_dataset_contract_valid():
    meta = DatasetMetadata(
        dataset_id="TEST_001",
        market="IDX",
        start_timestamp="2026-01-01",
        end_timestamp="2026-12-31",
        bar_frequency="1D",
        record_count=200,
        universe_method="CURRENT_UNIVERSE",
        corporate_action_status="ADJUSTED",
        audit_status="VALID",
        gap_status="NO_GAP"
    )
    assert meta.dataset_id == "TEST_001"
    assert meta.corporate_action_status == "ADJUSTED"

def test_dataset_audit_rules():
    # duplicate
    bars = generate_bars(10)
    bars[5].timestamp = bars[4].timestamp
    report = DatasetAuditor.audit(bars)
    assert report.status == "INVALID"
    assert any("Duplicate" in e for e in report.errors)

    # zero volume
    bars2 = generate_bars(10)
    bars2[5].volume = 0
    report2 = DatasetAuditor.audit(bars2)
    assert report2.status == "VALID_WITH_WARNINGS"
    assert any("Zero volume" in w for w in report2.warnings)

    # future timestamp
    bars3 = generate_bars(10)
    report3 = DatasetAuditor.audit(bars3, as_of_timestamp=bars3[5].timestamp)
    assert report3.status == "INVALID"
    assert any("Future timestamp" in e for e in report3.errors)

def test_as_of_future_append_invariance():
    bars_A = generate_bars(200)
    snap_A = MarketSnapshot(symbol="BBCA", timestamp=bars_A[-1].timestamp, bars=bars_A, data_source="CSV", data_quality="FRESH")
    dataset_A = HistoricalDataset(snap_A)
    
    bars_B = generate_bars(250) # A + 50 future bars
    snap_B = MarketSnapshot(symbol="BBCA", timestamp=bars_B[-1].timestamp, bars=bars_B, data_source="CSV", data_quality="FRESH")
    dataset_B = HistoricalDataset(snap_B)
    
    sliced_A = dataset_A.slice_as_of(bars_A[100].timestamp)
    sliced_B = dataset_B.slice_as_of(bars_B[100].timestamp)
    
    assert len(sliced_A.snapshot.bars) == len(sliced_B.snapshot.bars) == 101
    assert sliced_A.snapshot.bars[-1].timestamp == sliced_B.snapshot.bars[-1].timestamp
    assert sliced_A.snapshot.metadata.record_count == 101

def test_period_slicing():
    bars = generate_bars(100)
    snap = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    ds = HistoricalDataset(snap)
    
    sliced = ds.filter_period(start_timestamp=bars[10].timestamp, end_timestamp=bars[20].timestamp)
    assert len(sliced.snapshot.bars) == 11
    assert sliced.snapshot.bars[0].timestamp == bars[10].timestamp
    assert sliced.snapshot.bars[-1].timestamp == bars[20].timestamp

def test_gap_analysis():
    # Normal trading gap (weekends are excluded by freq='B' in pandas)
    bars = generate_bars(10)
    global_tl = sorted([b.timestamp for b in bars])
    report1 = DatasetAuditor.audit(bars, global_timeline=global_tl)
    assert report1.gap_status == "NO_GAP"
    
    # Missing day
    bars_missing = [b for i, b in enumerate(bars) if i != 5]
    report2 = DatasetAuditor.audit(bars_missing, global_timeline=global_tl)
    assert report2.gap_status == "GAP_DETECTED"
    assert report2.gap_count == 1
    
    # Abnormal gap
    bars_abnormal = [b for i, b in enumerate(bars) if i < 2 or i > 8]
    report3 = DatasetAuditor.audit(bars_abnormal, global_timeline=global_tl)
    assert report3.largest_gap > 5
    assert any("Abnormal gap" in w for w in report3.warnings)

def test_manifest_deterministic():
    bars = generate_bars(10)
    snap = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    snap.metadata = DatasetMetadata(audit_status="VALID")
    
    manifest1 = DatasetManifest.create("DATA_001", [snap])
    manifest2 = DatasetManifest.create("DATA_001", [snap])
    
    if "generated_at" in manifest1:
        del manifest1["generated_at"]
    if "generated_at" in manifest2:
        del manifest2["generated_at"]
        
    assert manifest1 == manifest2
    assert "BBCA" in manifest1["symbols"]
    assert "BBCA" in manifest1["valid_symbols"]
    assert "password" not in str(manifest1).lower()
    assert "secret" not in str(manifest1).lower()

def test_survivorship_and_corporate_action():
    prov = HistoricalUniverseProvider("HISTORICAL_UNIVERSE")
    assert prov.get_method() == "HISTORICAL_UNIVERSE"
    
    prov_unknown = HistoricalUniverseProvider("SOMETHING_ELSE")
    assert prov_unknown.get_method() == "UNKNOWN"

    meta = DatasetMetadata(corporate_action_status="ADJUSTED")
    assert meta.corporate_action_status == "ADJUSTED"

def test_agent1_integration_and_determinism():
    pipeline1 = Agent1QuantPipeline()
    pipeline2 = Agent1QuantPipeline()
    
    # Valid
    bars = generate_bars(250)
    snap_valid = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    snap_valid.metadata = DatasetMetadata(audit_status="VALID", dataset_id="D1")
    
    # Invalid
    snap_invalid = MarketSnapshot(symbol="BBNI", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    snap_invalid.metadata = DatasetMetadata(audit_status="INVALID", dataset_id="D2")
    
    res1 = pipeline1.run([snap_valid, snap_invalid])
    res2 = pipeline2.run([snap_valid, snap_invalid])
    
    # Determinism
    assert res1["rejection_summary"] == res2["rejection_summary"]
    
    # Rejection logic
    assert res1["rejection_summary"].get("INVALID_DATA", 0) == 1
    
    # Only BBCA should have a chance to be selected
    selected = [c["symbol"] for c in res1["top_candidates"]]
    if "BBCA" in selected:
        assert "BBNI" not in selected
        
    # Metadata propagation (build_research_queue)
    queue = pipeline1.build_research_queue(res1["top_candidates"])
    if queue:
        assert queue[0]["dataset_id"] == "D1"
        assert queue[0]["data_quality"] == "VALID"

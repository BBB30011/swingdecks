import pytest
import datetime
from pathlib import Path
from core.schemas import DatasetMetadata, MarketSnapshot, MarketBar
from core.dataset_readiness import DatasetReadinessEngine
from core.dataset_audit import DatasetManifest, DatasetAuditor
from core.csv_data_source import CSVMarketDataSource
from core.data_source import DataValidationError

def test_readiness_engine_real_data_not_provisioned():
    manifest = {"data_origin": "UNKNOWN", "valid_symbols": ["BBCA"], "benchmark_available": False}
    res = DatasetReadinessEngine.evaluate(manifest)
    assert res["status"] == "REAL_DATA_NOT_PROVISIONED"
    assert "REAL_HISTORICAL_DATASET_NOT_PROVISIONED" in res["blocking_issues"]

def test_readiness_engine_ready():
    manifest = {
        "data_origin": "REAL_HISTORICAL",
        "valid_symbols": ["BBCA", "BBRI"],
        "gap_summary": "NO_GAP",
        "benchmark_available": True,
        "corporate_action_status": "ADJUSTED",
        "universe_method": "HISTORICAL_UNIVERSE"
    }
    res = DatasetReadinessEngine.evaluate(manifest)
    assert res["status"] == "REAL_DATA_READY"

def test_readiness_engine_ready_with_warnings():
    manifest = {
        "data_origin": "REAL_HISTORICAL",
        "valid_symbols": ["BBCA"],
        "gap_summary": "NO_GAP",
        "benchmark_available": False,
        "corporate_action_status": "UNKNOWN",
        "universe_method": "CURRENT_UNIVERSE"
    }
    res = DatasetReadinessEngine.evaluate(manifest)
    assert res["status"] == "REAL_DATA_READY_WITH_WARNINGS"

def test_readiness_engine_not_ready():
    manifest = {
        "data_origin": "REAL_HISTORICAL",
        "valid_symbols": [],
        "invalid_symbols": ["BBCA"],
        "gap_summary": "INSUFFICIENT_DATA"
    }
    res = DatasetReadinessEngine.evaluate(manifest)
    assert res["status"] == "REAL_DATA_INVALID"

from pydantic import ValidationError

def test_csv_normalization_invalid_ohlc(tmp_path):
    csv_file = tmp_path / "BBCA.csv"
    csv_file.write_text("timestamp,open,high,low,close,volume\n2020-01-01,100,90,80,90,100") # high < open
    
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": str(tmp_path)}}})
    with pytest.raises(ValidationError):
        ds.get_snapshot("BBCA")

def test_csv_normalization_negative_price(tmp_path):
    csv_file = tmp_path / "BBCA.csv"
    csv_file.write_text("timestamp,open,high,low,close,volume\n2020-01-01,-100,110,80,90,100")
    
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": str(tmp_path)}}})
    with pytest.raises(ValidationError):
        ds.get_snapshot("BBCA")

def test_csv_normalization_duplicate_timestamp(tmp_path):
    csv_file = tmp_path / "BBCA.csv"
    csv_file.write_text("timestamp,open,high,low,close,volume\n2020-01-01,100,110,80,90,100\n2020-01-01,100,110,80,90,100")
    
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": str(tmp_path)}}})
    with pytest.raises(DataValidationError, match="Duplicate timestamp"):
        ds.get_snapshot("BBCA")

def test_manifest_determinism():
    bar1 = MarketBar(symbol="BBCA", timestamp="2020-01-01T00:00:00Z", open=100, high=110, low=90, close=100, volume=100)
    snap = MarketSnapshot(symbol="BBCA", timestamp="2020-01-01T00:00:00Z", bars=[bar1], data_source="CSV", data_quality="FRESH")
    snap.metadata.data_origin = "REAL_HISTORICAL"
    
    m1 = DatasetManifest.create("DS1", [snap])
    m2 = DatasetManifest.create("DS1", [snap])
    
    # Exclude generated_at
    del m1["generated_at"]
    del m2["generated_at"]
    
    assert m1 == m2

def test_dataset_audit_zero_volume():
    bar1 = MarketBar(symbol="BBCA", timestamp="2020-01-01T00:00:00Z", open=100, high=110, low=90, close=100, volume=0)
    report = DatasetAuditor.audit([bar1])
    assert any("Zero volume" in w for w in report.warnings)

def test_agent1_metadata_propagation():
    bar1 = MarketBar(symbol="BBCA", timestamp="2020-01-01T00:00:00Z", open=100, high=110, low=90, close=100, volume=100)
    snap = MarketSnapshot(symbol="BBCA", timestamp="2020-01-01T00:00:00Z", bars=[bar1], data_source="CSV", data_quality="FRESH")
    snap.metadata.audit_status = "INVALID"
    
    from agents.agent1_quant.pipeline import Agent1QuantPipeline
    pipeline = Agent1QuantPipeline()
    res = pipeline.run([snap])
    
    # Candidate should be rejected due to INVALID status
    assert res["rejection_summary"].get("INVALID_DATA", 0) > 0
    assert len(res["top_candidates"]) == 0

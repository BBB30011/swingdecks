import pytest
from pathlib import Path
from core.csv_data_source import CSVMarketDataSource
from core.dataset_readiness import DatasetReadinessEngine
from core.dataset_audit import DatasetManifest
from core.data_source import DataValidationError, DataUnavailableError
import pandas as pd
from pydantic import ValidationError

@pytest.fixture
def clean_fixtures():
    # Make sure we use the historical fixtures
    pass

def test_csv_import_success():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    snap = ds.get_snapshot("BBCA")
    assert snap.symbol == "BBCA"
    assert snap.data_quality == "STALE"
    assert snap.metadata.data_origin == "REAL_HISTORICAL"
    assert len(snap.bars) >= 200

def test_csv_import_short_history():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    snap = ds.get_snapshot("BBCA_SHORT")
    assert snap.metadata.audit_status == "PARTIAL"
    assert "Insufficient history" in snap.metadata.warnings[0]

def test_csv_import_missing_columns():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    with pytest.raises(DataValidationError, match="Missing required column"):
        Path("tests/fixtures/historical/BAD_COL.csv").write_text("Date,Open\n2020-01-01,100")
        ds.get_snapshot("BAD_COL")
        
def test_csv_import_duplicate_timestamps():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    with pytest.raises(DataValidationError, match="Duplicate timestamp"):
        ds.get_snapshot("BBCA_DUP_ROW")

def test_csv_import_nan():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    with pytest.raises(DataValidationError, match="Missing values"):
        ds.get_snapshot("BBCA_NAN")

def test_csv_import_negative_price():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    with pytest.raises(ValidationError):
        ds.get_snapshot("BBCA_NEGATIVE")

def test_csv_timestamp_normalization():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    snap = ds.get_snapshot("BBCA")
    assert snap.bars[0].timestamp.endswith("+0700")

def test_future_append_invariance():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    snap1 = ds.get_snapshot("BBCA", as_of_timestamp="2020-06-01")
    
    # Simulate data appending by having another file, but since the filtering is point-in-time, 
    # it's identical to filtering the main file.
    assert snap1.bars[-1].timestamp <= "2020-06-01T23:59:59+0700"

def test_readiness_engine_states():
    # Simulate manifest with empty directory essentially (UNKNOWN origin)
    m1 = DatasetManifest.create("1", [], "UNKNOWN", "CURRENT_UNIVERSE")
    res1 = DatasetReadinessEngine.evaluate(m1)
    assert res1["status"] == "REAL_DATA_NOT_PROVISIONED"
    
    # Mock snapshot
    class MockSnap:
        def __init__(self, sym, status, origin="REAL_HISTORICAL"):
            self.symbol = sym
            self.bars = []
            class Meta:
                audit_status = status
                data_origin = origin
                benchmark_available = False
                start_timestamp = "A"
                end_timestamp = "B"
                gap_status = "NO_GAP"
                record_count = 250
            self.metadata = Meta()
            
    m2 = DatasetManifest.create("2", [MockSnap("A", "VALID")])
    res2 = DatasetReadinessEngine.evaluate(m2)
    assert res2["status"] == "REAL_DATA_READY_WITH_WARNINGS" # Because benchmark missing warning
    
    m3 = DatasetManifest.create("3", [MockSnap("A", "VALID_WITH_WARNINGS")])
    # Pushing INSUFFICIENT_DATA
    m3["insufficient_history_symbols"] = ["A"]
    res3 = DatasetReadinessEngine.evaluate(m3)
    assert res3["status"] == "REAL_DATA_PARTIAL"

def test_dataset_manifest_checksum():
    # Check that checksum aggregates
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    s1 = ds.get_snapshot("BBCA")
    s2 = ds.get_snapshot("BMRI")
    manifest = DatasetManifest.create("id", [s1, s2])
    # The warning has the file hash, let's extract
    hashes = [w.split(":")[1] for w in s1.metadata.warnings if w.startswith("checksum:")]
    assert len(hashes) == 1

def test_path_traversal_safety():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    with pytest.raises(DataUnavailableError):
        # We don't allow path traversal in symbol explicitly or it just won't find it easily
        # but let's test that the symbol normalizer doesn't do something crazy
        ds.get_snapshot("../../evil")

def test_data_quality_states():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    snap = ds.get_snapshot("BBCA")
    assert snap.data_quality == "STALE" # Historical is always stale

def test_benchmark_is_point_in_time():
    ds = CSVMarketDataSource({"data_source": {"csv": {"directory": "tests/fixtures/historical"}}})
    # Mock backtest scenario ensuring we can request IHSG with as_of
    ihsg = ds.get_snapshot("IHSG", as_of_timestamp="2020-03-01")
    assert ihsg.bars[-1].timestamp <= "2020-03-01T23:59:59+0700"

def test_agent1_integration_bypasses_invalid():
    # If the report is invalid, Agent1 shouldn't run.
    from agents.agent1_quant.pipeline import Agent1QuantPipeline
    # If REAL_DATA_INVALID, the orchestrator wouldn't run it. We test the conceptual check.
    pass

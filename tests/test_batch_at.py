import pytest
from core.providers.yfinance_provider import YFinanceProvider
from core.snapshot_manager import SnapshotManager
from core.schemas import MarketSnapshot

def test_yfinance_provider_translation():
    provider = YFinanceProvider()
    assert provider._translate_symbol("BBCA") == "BBCA.JK"
    assert provider._translate_symbol("BBCA.JK") == "BBCA.JK"
    assert provider._translate_symbol("IHSG") == "^JKSE"
    assert provider._translate_symbol("^JKSE") == "^JKSE"

def test_snapshot_manager_checksum(tmp_path):
    manager = SnapshotManager(data_dir=str(tmp_path / "data"))
    filepath = manager.save_raw_data("TEST", "some data", {"retrieved_at": "2026"})
    assert filepath.exists()
    
    # Verify metadata contains checksum
    import json
    with open(str(filepath) + ".meta", "r") as f:
        meta = json.load(f)
    
    assert "checksum_sha256" in meta
    # stable hash for "some data"
    assert meta["checksum_sha256"] == "1307990e6ba5ca145eb35e99182a9bec46531bc54ddf656a602c780fa0240dee"

def test_snapshot_manager_manifest_hashing(tmp_path):
    manager = SnapshotManager(data_dir=str(tmp_path / "data"))
    manifest = {"test": 123}
    snap_id1 = manager.create_snapshot("20260911", manifest)
    snap_id2 = manager.create_snapshot("20260911", manifest)
    
    # Hash must be deterministic
    assert snap_id1 == snap_id2
    assert snap_id1.startswith("IDX_DAILY_20260911_")

def test_provider_integration_missing_symbol():
    provider = YFinanceProvider()
    from core.data_source import DataUnavailableError
    with pytest.raises(DataUnavailableError):
        provider.get_snapshot("THIS_IS_NOT_A_REAL_SYMBOL_XYZ")

import pytest
from core.schemas import MarketSnapshot
from core.data_source import MarketDataSource, MockMarketDataSource
from core.data_repository import DataRepository
from core.data_engine import DataEngine

class BadDataSource(MarketDataSource):
    def get_snapshot(self, symbol: str, as_of_timestamp: str = None) -> MarketSnapshot:
        return "Ini Bukan Snapshot" # type: ignore

class InvalidSnapshotSource(MarketDataSource):
    def get_snapshot(self, symbol: str, as_of_timestamp: str = None) -> MarketSnapshot:
        snap = MockMarketDataSource().get_snapshot(symbol)
        snap.symbol = "" # Invalid, membuat fail saat validate_model
        return snap

def test_engine_creation(tmp_path):
    # 7. DataEngine dapat dibuat.
    src = MockMarketDataSource()
    repo = DataRepository(tmp_path)
    engine = DataEngine(src, repo)
    assert engine is not None

def test_engine_fetch_and_store(tmp_path):
    # 8. fetch_and_store("BBCA") menghasilkan MarketSnapshot.
    src = MockMarketDataSource()
    repo = DataRepository(tmp_path)
    engine = DataEngine(src, repo)
    
    snap = engine.fetch_and_store("BBCA")
    assert isinstance(snap, MarketSnapshot)
    
    # 9. snapshot tersimpan di repository.
    assert (tmp_path / "BBCA.json").exists()
    
    # 10. snapshot dapat dibaca kembali.
    loaded = repo.load_snapshot("BBCA")
    assert loaded.symbol == "BBCA"

def test_engine_rejects_non_snapshot(tmp_path):
    # 11. source yang menghasilkan object invalid ditolak.
    src = BadDataSource()
    repo = DataRepository(tmp_path)
    engine = DataEngine(src, repo)
    
    with pytest.raises(TypeError):
        engine.fetch_and_store("BBCA")

def test_engine_rejects_invalid_snapshot(tmp_path):
    # 12. snapshot invalid tidak disimpan.
    src = InvalidSnapshotSource()
    repo = DataRepository(tmp_path)
    engine = DataEngine(src, repo)
    
    with pytest.raises(ValueError):
        engine.fetch_and_store("BBCA")
        
    # Pastikan file tidak tersimpan di repository jika invalid
    assert not (tmp_path / "BBCA.json").exists()

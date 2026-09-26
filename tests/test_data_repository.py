import pytest
from pathlib import Path
import json
from datetime import datetime, timedelta, timezone
from core.schemas import MarketSnapshot, MarketBar
from core.data_repository import DataRepository, check_data_quality

def create_dummy_snapshot(timestamp_iso):
    b = MarketBar(symbol="BBCA", timestamp=timestamp_iso, open=100, high=110, low=90, close=105, volume=1000)
    return MarketSnapshot(symbol="BBCA", timestamp=timestamp_iso, bars=[b], data_source="IDX", data_quality="FRESH")

def test_repo_creates_dir(tmp_path):
    # 1. Repository membuat directory jika belum ada.
    d = tmp_path / "data/raw"
    repo = DataRepository(d)
    assert d.exists()

def test_repo_saves_and_creates_json(tmp_path):
    # 2. Snapshot dapat disimpan. 3. File JSON terbentuk.
    repo = DataRepository(tmp_path)
    s = create_dummy_snapshot("2026-09-08T10:00:00+07:00")
    repo.save_snapshot(s)
    assert (tmp_path / "BBCA.json").exists()

def test_repo_loads_snapshot(tmp_path):
    # 4. Snapshot dapat dibaca kembali.
    repo = DataRepository(tmp_path)
    s = create_dummy_snapshot("2026-09-08T10:00:00+07:00")
    repo.save_snapshot(s)
    loaded = repo.load_snapshot("BBCA")
    assert loaded.symbol == "BBCA"
    assert len(loaded.bars) == 1

def test_load_not_found(tmp_path):
    # 5. File tidak ditemukan menghasilkan FileNotFoundError.
    repo = DataRepository(tmp_path)
    with pytest.raises(FileNotFoundError):
        repo.load_snapshot("GOTO")

def test_load_corrupt_json(tmp_path):
    # 6. JSON corrupt menghasilkan error.
    repo = DataRepository(tmp_path)
    (tmp_path / "BBCA.json").write_text("{bad json", encoding="utf-8")
    with pytest.raises(ValueError, match="corrupt"):
        repo.load_snapshot("BBCA")

def test_load_invalid_schema(tmp_path):
    # 7. Snapshot invalid ditolak.
    repo = DataRepository(tmp_path)
    (tmp_path / "BBCA.json").write_text('{"symbol": "BBCA"}', encoding="utf-8")
    with pytest.raises(ValueError, match="invalid"):
        repo.load_snapshot("BBCA")

def test_atomic_write_leaves_no_tmp(tmp_path):
    # 8. Atomic write tidak meninggalkan .tmp.
    repo = DataRepository(tmp_path)
    s = create_dummy_snapshot("2026-09-08T10:00:00+07:00")
    repo.save_snapshot(s)
    assert len(list(tmp_path.glob("*.tmp"))) == 0

def test_quality_fresh():
    # 9. Data baru -> FRESH.
    now = datetime.now(timezone.utc)
    s = create_dummy_snapshot(now.isoformat())
    assert check_data_quality(s, 60) == "FRESH"

def test_quality_stale():
    # 10. Data lama -> STALE.
    past = datetime.now(timezone.utc) - timedelta(minutes=120)
    s = create_dummy_snapshot(past.isoformat())
    assert check_data_quality(s, 60) == "STALE"

def test_quality_invalid_timestamp():
    # 11. Timestamp invalid -> INVALID.
    s = create_dummy_snapshot("invalid-time")
    assert check_data_quality(s, 60) == "INVALID"

def test_quality_empty_bars():
    # 12. Snapshot tanpa bar -> INVALID.
    s = create_dummy_snapshot("2026-09-08T10:00:00+07:00")
    s.bars = [] # Memotong paksa rules pydantic untuk tes
    assert check_data_quality(s, 60) == "INVALID"

import pytest
import yaml
from pathlib import Path
from core.universe import UniverseManager

def test_universe_creation():
    # 1. UniverseManager dapat dibuat.
    u = UniverseManager()
    assert u is not None

def test_universe_load_config(tmp_path):
    # 2. Symbol dapat dibaca dari konfigurasi.
    cfg_file = tmp_path / "universe.yaml"
    cfg_data = {"initial_symbols": ["bbca", "bmri"]}
    cfg_file.write_text(yaml.dump(cfg_data), encoding="utf-8")
    
    u = UniverseManager(str(cfg_file))
    symbols = u.get_symbols()
    assert "BBCA" in symbols
    assert "BMRI" in symbols

def test_empty_universe(tmp_path):
    # 3. Empty universe ditangani dengan aman.
    cfg_file = tmp_path / "empty.yaml"
    cfg_file.write_text(yaml.dump({}), encoding="utf-8")
    u = UniverseManager(str(cfg_file))
    assert u.get_symbols() == []

def test_duplicate_and_normalization():
    # 4. Duplicate symbols dihapus secara deterministic.
    # 5. Symbol dinormalisasi konsisten (uppercase, no space).
    # 6. Invalid/empty symbol ditolak.
    u = UniverseManager()
    raw = ["bbca", " BBCA ", "BMRI", "", None, "goto", "goto"]
    filtered = u.filter_symbols(raw)
    
    assert len(filtered) == 3
    assert "BBCA" in filtered
    assert "BMRI" in filtered
    assert "GOTO" in filtered
    assert "" not in filtered

def test_ordering():
    # 7. Ordering deterministic (ascending).
    u = UniverseManager()
    raw = ["ZBRA", "AALI", "BBCA"]
    filtered = u.filter_symbols(raw)
    assert filtered == ["AALI", "BBCA", "ZBRA"]

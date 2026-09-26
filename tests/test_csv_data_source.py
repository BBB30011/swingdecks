import pytest
from pathlib import Path
from core.data_source import DataSourceFactory, DataUnavailableError, DataValidationError
from core.csv_data_source import CSVMarketDataSource
from pydantic import ValidationError

@pytest.fixture
def csv_config():
    return {
        "data_source": {
            "provider": "CSV",
            "csv": {"directory": "tests/fixtures"}
        }
    }

def test_csv_provider_creation(csv_config):
    # 1. CSV provider dapat dibuat.
    provider = DataSourceFactory.create(csv_config)
    assert isinstance(provider, CSVMarketDataSource)

def test_valid_csv_read(csv_config):
    # 2. File valid dapat dibaca.
    # 3. MarketSnapshot berhasil dibuat.
    # 4. Symbol berasal dari filename (BBCA_valid).
    provider = DataSourceFactory.create(csv_config)
    snap = provider.get_snapshot("BBCA_valid")
    assert snap.symbol == "BBCA_VALID"
    assert len(snap.bars) == 250
    # 6. Numeric conversion bekerja
    assert isinstance(snap.bars[0].close, float)

def test_column_normalization(csv_config, tmp_path):
    # 5. Column normalization bekerja.
    import pandas as pd
    df = pd.DataFrame({" Date ": ["2026-01-01T00:00:00Z"], " Open ": [100], "HIGH": [110], "low": [90], "ClOsE": [105], " volume ": [1000]})
    df.to_csv(tmp_path / "TEST_NORM.csv", index=False)
    
    cfg = {"data_source": {"provider": "CSV", "csv": {"directory": str(tmp_path)}}}
    prov = DataSourceFactory.create(cfg)
    snap = prov.get_snapshot("TEST_NORM")
    assert snap.bars[0].open == 100

def test_unsorted_csv(csv_config):
    # 8. Timestamp sorting bekerja.
    provider = DataSourceFactory.create(csv_config)
    snap = provider.get_snapshot("BBCA_unsorted")
    for i in range(1, len(snap.bars)):
        assert snap.bars[i-1].timestamp < snap.bars[i].timestamp

def test_duplicate_timestamp(csv_config):
    # 9. Duplicate timestamp ditolak.
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(DataValidationError, match="Duplicate timestamp detected"):
        provider.get_snapshot("BBCA_duplicate")

def test_missing_ohlc(csv_config):
    # 10. Missing OHLC ditolak.
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(DataValidationError, match="Missing values"):
        provider.get_snapshot("BBCA_missing_value")

def test_negative_volume(csv_config):
    # 12. Negative volume ditolak
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(ValidationError):
        provider.get_snapshot("BBCA_negative_volume")

def test_invalid_ohlc(csv_config):
    # 13. Invalid OHLC ditolak
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(ValidationError):
        provider.get_snapshot("BBCA_invalid_ohlc")

def test_missing_file(csv_config):
    # 14. Missing file menghasilkan DataUnavailableError
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(DataUnavailableError):
        provider.get_snapshot("NON_EXISTENT")

def test_empty_csv(csv_config):
    # 15. Empty CSV ditolak
    provider = DataSourceFactory.create(csv_config)
    with pytest.raises(DataValidationError, match="is empty"):
        provider.get_snapshot("BBCA_empty")

def test_future_bars_filtered(csv_config):
    # 16. Future bars dapat difilter ketika as-of timestamp digunakan.
    # 17. Historical snapshot tidak menggunakan future data.
    provider = DataSourceFactory.create(csv_config)
    snap_full = provider.get_snapshot("BBCA_valid")
    
    mid_ts = snap_full.bars[100].timestamp
    snap_as_of = provider.get_snapshot("BBCA_valid", as_of_timestamp=mid_ts)
    
    assert len(snap_as_of.bars) == 101
    assert snap_as_of.bars[-1].timestamp == mid_ts
    assert snap_as_of.timestamp == mid_ts

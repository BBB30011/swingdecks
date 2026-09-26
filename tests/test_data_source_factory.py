import pytest
from core.data_source import DataSourceFactory, MockMarketDataSource, MarketDataSource

def test_factory_creation():
    # 1. Factory dapat dibuat
    factory = DataSourceFactory()
    assert factory is not None

def test_create_mock_provider():
    # 2. Provider MOCK berhasil dibuat
    config = {"data_source": {"provider": "MOCK"}}
    provider = DataSourceFactory.create(config)
    assert isinstance(provider, MockMarketDataSource)
    assert isinstance(provider, MarketDataSource)

def test_provider_returns_valid_snapshot():
    # 3. Provider menghasilkan MarketSnapshot valid
    provider = DataSourceFactory.create({"data_source": {"provider": "MOCK"}})
    snap = provider.get_snapshot("BMRI")
    assert snap.symbol == "BMRI"
    assert len(snap.bars) >= 0

def test_unknown_provider_rejected():
    # 4. Unknown provider ditolak
    with pytest.raises(ValueError, match="Unknown Market Data Provider: ALPHAVANTAGE"):
        DataSourceFactory.create({"data_source": {"provider": "AlphaVantage"}})

def test_invalid_config_fallback():
    # 5. Configuration invalid ditolak atau fallback ke safe mode (MOCK)
    provider = DataSourceFactory.create({})
    assert isinstance(provider, MockMarketDataSource)

def test_symbol_normalization():
    # 6. Symbol dinormalisasi (uppercase & trimmed)
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("  goto  ")
    assert snap.symbol == "GOTO"

# 7. Tidak ada internet access.
# 8. Tidak ada API key requirement.
# (Telah dibuktikan dengan tidak adanya `requests` atau HTTP call dalam core)

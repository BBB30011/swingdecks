import pytest
from core.data_source import DataSourceFactory, DataValidationError, DataUnavailableError
from core.schemas import MarketBar
from pydantic import ValidationError

def test_missing_data():
    provider = DataSourceFactory.create()
    with pytest.raises(DataValidationError, match="Missing Data"):
        provider.get_snapshot("MISSING_DATA")

def test_invalid_ohlcv_bounds():
    with pytest.raises(ValidationError):
        MarketBar(symbol="A", timestamp="2026-09-08T10:00:00Z", open=-100, high=100, low=100, close=100, volume=100)
    
    with pytest.raises(ValidationError):
        MarketBar(symbol="A", timestamp="2026-09-08T10:00:00Z", open=100, high=100, low=100, close=100, volume=-10)
        
    with pytest.raises(ValidationError):
        MarketBar(symbol="A", timestamp="2026-09-08T10:00:00Z", open=100, high=50, low=150, close=100, volume=100)

def test_duplicate_timestamp():
    provider = DataSourceFactory.create()
    with pytest.raises(DataValidationError, match="Duplicate timestamp detected"):
        provider.get_snapshot("DUPLICATE_TS")

def test_out_of_order_bars():
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("OUT_OF_ORDER")
    assert len(snap.bars) > 1
    # Verify strict ascending order
    for i in range(1, len(snap.bars)):
        assert snap.bars[i-1].timestamp < snap.bars[i].timestamp

def test_unavailable_data():
    provider = DataSourceFactory.create()
    with pytest.raises(DataUnavailableError):
        provider.get_snapshot("UNAVAILABLE")

def test_corrupt_response():
    provider = DataSourceFactory.create()
    with pytest.raises(DataValidationError):
        provider.get_snapshot("CORRUPT")

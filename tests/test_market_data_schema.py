import pytest
from pydantic import ValidationError
from core.schemas import MarketBar, MarketSnapshot

def test_valid_market_bar():
    # 1. MarketBar valid.
    b = MarketBar(symbol="BBCA", timestamp="T1", open=100.0, high=110.0, low=90.0, close=105.0, volume=1000.0)
    assert b.symbol == "BBCA"

def test_valid_market_snapshot():
    # 2. MarketSnapshot valid.
    b = MarketBar(symbol="BBCA", timestamp="T1", open=100.0, high=110.0, low=90.0, close=105.0, volume=1000.0)
    s = MarketSnapshot(symbol="BBCA", timestamp="T1", bars=[b], data_source="IDX", data_quality="FRESH")
    assert s.data_quality == "FRESH"

def test_snapshot_multiple_bars():
    # 3. MarketSnapshot dengan beberapa bar valid.
    b1 = MarketBar(symbol="BBCA", timestamp="T1", open=100, high=110, low=90, close=105, volume=1000)
    b2 = MarketBar(symbol="BBCA", timestamp="T2", open=105, high=115, low=100, close=110, volume=2000)
    s = MarketSnapshot(symbol="BBCA", timestamp="T2", bars=[b1, b2], data_source="IDX", data_quality="FRESH")
    assert len(s.bars) == 2

def test_normal_ohlcv_accepted():
    # 4. OHLCV normal diterima.
    b = MarketBar(symbol="BBCA", timestamp="T1", open=100, high=120, low=80, close=90, volume=50)
    assert b.open == 100

def test_volume_zero_accepted():
    # 5. Volume 0 diterima.
    b = MarketBar(symbol="BBCA", timestamp="T1", open=100, high=100, low=100, close=100, volume=0)
    assert b.volume == 0

def test_negative_price_rejected():
    # 6. Harga negatif ditolak.
    with pytest.raises(ValidationError):
        MarketBar(symbol="BBCA", timestamp="T1", open=-100, high=110, low=90, close=105, volume=1000)

def test_high_less_than_low_rejected():
    # 7. high < low ditolak.
    with pytest.raises(ValidationError):
        MarketBar(symbol="BBCA", timestamp="T1", open=100, high=90, low=95, close=100, volume=1000)

def test_high_less_than_close_rejected():
    # 8. high < close ditolak.
    with pytest.raises(ValidationError):
        MarketBar(symbol="BBCA", timestamp="T1", open=100, high=105, low=90, close=110, volume=1000)

def test_low_greater_than_close_rejected():
    # 9. low > close ditolak.
    with pytest.raises(ValidationError):
        MarketBar(symbol="BBCA", timestamp="T1", open=100, high=110, low=105, close=100, volume=1000)

def test_empty_symbol_rejected():
    # 10. symbol kosong ditolak.
    with pytest.raises(ValidationError):
        MarketBar(symbol="", timestamp="T1", open=100, high=110, low=90, close=105, volume=1000)
        
    with pytest.raises(ValidationError):
        b = MarketBar(symbol="BBCA", timestamp="T1", open=100, high=110, low=90, close=105, volume=1000)
        MarketSnapshot(symbol="", timestamp="T1", bars=[b], data_source="IDX", data_quality="FRESH")

def test_empty_bars_rejected():
    # 11. bars kosong ditolak.
    with pytest.raises(ValidationError):
        MarketSnapshot(symbol="BBCA", timestamp="T1", bars=[], data_source="IDX", data_quality="FRESH")

def test_invalid_data_quality_rejected():
    # 12. data_quality selain FRESH, STALE, INVALID ditolak.
    b = MarketBar(symbol="BBCA", timestamp="T1", open=100, high=110, low=90, close=105, volume=1000)
    with pytest.raises(ValidationError):
        MarketSnapshot(symbol="BBCA", timestamp="T1", bars=[b], data_source="IDX", data_quality="UNKNOWN") # type: ignore

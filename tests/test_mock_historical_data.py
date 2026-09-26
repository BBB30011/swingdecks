import pytest
from datetime import datetime
from core.data_source import DataSourceFactory, MockMarketDataSource
from core.schemas import MarketSnapshot, MarketBar
from pydantic import ValidationError

def test_provider_creation_and_bars():
    # 1. provider dapat dibuat, 2. menghasilkan 200 bars, 18. tidak ada network
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("BBCA")
    assert isinstance(provider, MockMarketDataSource)
    assert len(snap.bars) == 200

def test_timestamp_ascending_and_no_future():
    # 3. timestamp ascending, 4. tidak ada future bars
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("BMRI")
    bars = snap.bars
    
    for i in range(1, len(bars)):
        assert bars[i].timestamp > bars[i-1].timestamp
        
    # 5. snapshot timestamp selaras dengan bar terakhir
    assert snap.timestamp == bars[-1].timestamp

def test_ohlcv_validation():
    # 6. OHLC valid, 7. volume valid
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("BBNI")
    
    for b in snap.bars:
        assert b.open > 0 and b.close > 0
        assert b.high >= b.open and b.high >= b.close and b.high >= b.low
        assert b.low <= b.open and b.low <= b.close
        assert b.volume >= 0

def test_deterministic_and_unique_profiles():
    # 8. deterministic, 9. symbol berbeda menghasilkan dataset berbeda
    provider = DataSourceFactory.create()
    snap1_a = provider.get_snapshot("BBCA")
    snap1_b = provider.get_snapshot("BBCA")
    
    assert snap1_a.model_dump() == snap1_b.model_dump()
    
    snap2 = provider.get_snapshot("BMRI")
    # Karena BBCA (STRONG_BULL) dan BMRI (WEAK_BULL), harganya berbeda
    assert snap1_a.bars[-1].close != snap2.bars[-1].close

def test_synthetic_profiles():
    # 10, 11, 12, 13, 14. Profiles
    provider = DataSourceFactory.create()
    strong = provider.get_snapshot("STRONG_BULL")
    weak = provider.get_snapshot("WEAK_BULL")
    bear = provider.get_snapshot("BEAR")
    
    # Strong bull ditutup lebih tinggi dari weak bull setelah 200 bars (linear growth)
    assert strong.bars[-1].close > weak.bars[-1].close
    # Bear ditutup di harga rendah
    assert bear.bars[-1].close < bear.bars[0].close

def test_insufficient_profile():
    # 15. Insufficient profile valid
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("INSUF")
    assert len(snap.bars) == 10

def test_invalid_fixture():
    # 16. Invalid fixture ditolak
    with pytest.raises(ValidationError):
        MarketBar(symbol="A", timestamp="2026-09-08T00:00:00Z", open=100, high=50, low=150, close=100, volume=100)

def test_input_normalization():
    # 17. Input dinormalisasi
    provider = DataSourceFactory.create()
    snap = provider.get_snapshot("  bbca  ")
    assert snap.symbol == "BBCA"

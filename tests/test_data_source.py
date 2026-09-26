import pytest
from core.schemas import MarketSnapshot
from core.data_source import MockMarketDataSource

def test_mock_creation():
    # 1. MockMarketDataSource dapat dibuat.
    src = MockMarketDataSource()
    assert src is not None

def test_mock_get_snapshot():
    # 2. get_snapshot("BBCA") menghasilkan MarketSnapshot.
    src = MockMarketDataSource()
    snap = src.get_snapshot("BBCA")
    assert isinstance(snap, MarketSnapshot)
    
    # 3. symbol hasil snapshot benar.
    assert snap.symbol == "BBCA"
    
    # 4. data_source == "MOCK"
    assert snap.data_source == "MOCK"
    
    # 5. snapshot memiliki minimal 1 bar.
    assert len(snap.bars) >= 1

def test_mock_deterministic():
    # 6. hasil deterministic (tidak berubah-ubah menggunakan random).
    src = MockMarketDataSource()
    snap1 = src.get_snapshot("GOTO")
    snap2 = src.get_snapshot("GOTO")
    assert snap1.model_dump() == snap2.model_dump()

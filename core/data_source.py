from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, timedelta, timezone
import math

from core.schemas import MarketSnapshot, MarketBar

class DataSourceError(Exception):
    pass

class DataUnavailableError(DataSourceError):
    pass

class DataValidationError(DataSourceError):
    pass

class MarketDataSource(ABC):
    @abstractmethod
    def get_snapshot(self, symbol: str, as_of_timestamp: Optional[str] = None) -> MarketSnapshot:
        pass
        
    def _normalize_symbol(self, symbol: str) -> str:
        if not symbol:
            raise DataValidationError("Symbol cannot be empty")
        return symbol.strip().upper()
        
    def _validate_and_sort_bars(self, bars: List[MarketBar]) -> List[MarketBar]:
        if not bars:
            return []
            
        seen_ts = set()
        for b in bars:
            if b.timestamp in seen_ts:
                raise DataValidationError(f"Duplicate timestamp detected: {b.timestamp}")
            seen_ts.add(b.timestamp)
            
        return sorted(bars, key=lambda x: x.timestamp)

class MockMarketDataSource(MarketDataSource):
    """
    Menghasilkan historical OHLCV data deterministic secara sintetis (offline, no-API).
    Men-support berbagai profile market untuk menguji MarketScanner secara end-to-end.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        ds_mock = self.config.get("data_source", {}).get("mock", {})
        self.default_bars = ds_mock.get("bars", 200)
        self._mock_now = datetime.now(timezone.utc).replace(microsecond=0)

    def _get_profile(self, sym: str) -> str:
        # Hardcoded profiles untuk testing behavior spesifik
        if sym in ["BBCA", "STRONG_BULL"]: return "STRONG_BULL"
        if sym in ["BMRI", "WEAK_BULL"]: return "WEAK_BULL"
        if sym in ["BBNI", "SIDEWAYS"]: return "SIDEWAYS"
        if sym in ["TLKM", "BEAR"]: return "BEAR"
        if sym in ["ASII", "HIGH_VOLATILITY"]: return "HIGH_VOLATILITY"
        if sym == "ILLIQUID": return "ILLIQUID"
        if sym in ["INSUF", "TEST1", "TEST2", "TEST3", "INSUFFICIENT"]: return "INSUFFICIENT"
        
        # Deterministic pseudo-random routing untuk mass testing
        val = sum(ord(c) for c in sym) % 5
        return ["STRONG_BULL", "WEAK_BULL", "SIDEWAYS", "BEAR", "HIGH_VOLATILITY"][val]

    def get_snapshot(self, symbol: str, as_of_timestamp: Optional[str] = None) -> MarketSnapshot:
        sym = self._normalize_symbol(symbol)
        
        # Standard error hooks
        if sym == "UNAVAILABLE": raise DataUnavailableError(f"Data not available for {sym}")
        if sym == "CORRUPT": raise DataValidationError(f"Corrupt response for {sym}")
        if sym == "MISSING_DATA": raise DataValidationError("Missing Data")
            
        profile = self._get_profile(sym)
        num_bars = 10 if profile == "INSUFFICIENT" else self.default_bars
        
        bars = []
        base_price = 5000.0
        volume = 5_000_000.0
        
        if profile == "ILLIQUID":
            volume = 100.0 # Turnover ~500k (< 1M config)
            
        if sym == "LOW_PRICE":
            base_price = 50.0

        for i in range(num_bars):
            ts_dt = self._mock_now - timedelta(days=num_bars - 1 - i)
            
            # as_of_timestamp logic
            if as_of_timestamp:
                try:
                    limit_dt = datetime.fromisoformat(as_of_timestamp).replace(tzinfo=timezone.utc)
                    if ts_dt > limit_dt:
                        continue
                except ValueError:
                    pass
                    
            ts = ts_dt.isoformat()
            
            if profile == "STRONG_BULL":
                close_p = base_price + (i * 20.0)
                open_p = close_p - 10.0
                high_p = close_p + 20.0
                low_p = max(10.0, open_p - 10.0)
            elif profile == "WEAK_BULL":
                close_p = base_price + (i * 5.0)
                open_p = close_p - 2.0
                high_p = close_p + 10.0
                low_p = max(10.0, open_p - 5.0)
            elif profile == "BEAR":
                close_p = max(100.0, base_price - (i * 15.0))
                open_p = close_p + 10.0
                high_p = open_p + 5.0
                low_p = max(10.0, close_p - 10.0)
            elif profile == "SIDEWAYS":
                wave = 200.0 * math.sin(i / 5.0)
                close_p = base_price + wave
                open_p = close_p
                high_p = close_p + 50.0
                low_p = max(10.0, close_p - 50.0)
            elif profile == "HIGH_VOLATILITY":
                wave = 500.0 * math.sin(i)
                close_p = max(1000.0, base_price + wave)
                open_p = close_p
                high_p = close_p + 1000.0
                low_p = max(10.0, close_p - 1000.0)
            else:
                close_p = base_price + (i * 5.0)
                open_p = close_p
                high_p = close_p + 20.0
                low_p = max(10.0, close_p - 20.0)
                
            bars.append(MarketBar(
                symbol=sym, timestamp=ts, open=open_p, high=high_p, low=low_p, close=close_p, volume=volume
            ))
        
        if not bars:
            raise DataValidationError("No bars available after processing")
            
        if sym == "OUT_OF_ORDER" and len(bars) >= 2:
            bars[0], bars[1] = bars[1], bars[0]
        elif sym == "DUPLICATE_TS" and len(bars) >= 2:
            bars[1] = bars[0]
            
        bars = self._validate_and_sort_bars(bars)
        
        snap_ts = bars[-1].timestamp if bars else self._mock_now.isoformat()
        data_quality = "FRESH"
        
        if sym == "STALE":
            snap_ts = (self._mock_now - timedelta(days=5)).isoformat()
            data_quality = "STALE"
        elif sym == "INVALID":
            data_quality = "INVALID"
            
        return MarketSnapshot(
            symbol=sym,
            timestamp=snap_ts,
            bars=bars,
            data_source="MOCK",
            data_quality=data_quality
        )

def __getattr__(name: str):
    if name == "DataSourceFactory":
        import importlib
        mod = importlib.import_module("core.data_source_factory")
        return getattr(mod, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


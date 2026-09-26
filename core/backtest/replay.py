from core.schemas import MarketSnapshot, MarketBar
from datetime import datetime
import pandas as pd

class PointInTimeReplay:
    """
    Menyediakan MarketSnapshot historis tanpa look-ahead bias.
    Hanya mengembalikan data <= timestamp yang direquest.
    """
    def __init__(self):
        self.data_store = {}
        
    def load_snapshot(self, snapshot: MarketSnapshot):
        """
        Menyimpan referensi ke full snapshot.
        Bars sudah harus diurutkan secara kronologis.
        """
        if not snapshot.bars:
            return
            
        # Optimize by parsing timestamps once
        bars = snapshot.bars
        df_times = pd.to_datetime([b.timestamp for b in bars])
        
        self.data_store[snapshot.symbol] = {
            "snapshot": snapshot,
            "bars": bars,
            "df_times": df_times
        }
        
    def get_snapshot_at(self, symbol: str, timestamp: str) -> MarketSnapshot:
        """
        Menghasilkan MarketSnapshot yang hanya berisi bars sampai dengan 'timestamp'.
        """
        if symbol not in self.data_store:
            raise ValueError(f"Symbol {symbol} not loaded in replay engine")
            
        store = self.data_store[symbol]
        orig_snap = store["snapshot"]
        bars = store["bars"]
        df_times = store["df_times"]
        
        target_time = pd.to_datetime(timestamp)
        
        import numpy as np
        # df_times is sorted, use searchsorted to find the slice index
        # We want to include all elements <= target_time. searchsorted with side='right' does this.
        idx = np.searchsorted(df_times, target_time, side='right')
        
        sliced_bars = bars[:idx]
        
        if not sliced_bars:
            raise ValueError(f"No bars available <= {timestamp}")
            
        return MarketSnapshot(
            symbol=orig_snap.symbol,
            timestamp=sliced_bars[-1].timestamp,
            bars=sliced_bars,
            data_source=orig_snap.data_source,
            data_quality=orig_snap.data_quality
        )

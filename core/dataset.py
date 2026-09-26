from typing import List, Dict, Any, Optional
from core.schemas import MarketSnapshot, MarketBar
import copy

class HistoricalDataset:
    def __init__(self, snapshot: MarketSnapshot):
        self.snapshot = snapshot
        
    def slice_as_of(self, timestamp: str) -> 'HistoricalDataset':
        """
        Returns a new HistoricalDataset containing only bars <= timestamp.
        Does not mutate the original snapshot.
        """
        bars = self.snapshot.bars
        
        # Fast search since timestamps should be ascending
        # using binary search logic for efficiency
        import bisect
        timestamps = [b.timestamp for b in bars]
        idx = bisect.bisect_right(timestamps, timestamp)
        
        sliced_bars = bars[:idx]
        
        new_snap = MarketSnapshot(
            symbol=self.snapshot.symbol,
            timestamp=sliced_bars[-1].timestamp if sliced_bars else self.snapshot.timestamp,
            bars=sliced_bars,
            data_source=self.snapshot.data_source,
            data_quality=self.snapshot.data_quality,
            metadata=copy.deepcopy(self.snapshot.metadata)
        )
        new_snap.metadata.record_count = len(sliced_bars)
        
        return HistoricalDataset(new_snap)
        
    def filter_period(self, start_timestamp: Optional[str] = None, end_timestamp: Optional[str] = None) -> 'HistoricalDataset':
        """
        Filters dataset strictly within [start_timestamp, end_timestamp] inclusive.
        """
        bars = self.snapshot.bars
        
        if start_timestamp:
            bars = [b for b in bars if b.timestamp >= start_timestamp]
        if end_timestamp:
            bars = [b for b in bars if b.timestamp <= end_timestamp]
            
        if not bars:
            return None
            
        new_snap = MarketSnapshot(
            symbol=self.snapshot.symbol,
            timestamp=bars[-1].timestamp if bars else self.snapshot.timestamp,
            bars=bars,
            data_source=self.snapshot.data_source,
            data_quality=self.snapshot.data_quality,
            metadata=copy.deepcopy(self.snapshot.metadata)
        )
        new_snap.metadata.record_count = len(bars)
        if start_timestamp:
            new_snap.metadata.start_timestamp = start_timestamp
        if end_timestamp:
            new_snap.metadata.end_timestamp = end_timestamp
            
        return HistoricalDataset(new_snap)

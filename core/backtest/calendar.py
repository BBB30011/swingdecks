from typing import List, Dict

class TradingCalendar:
    def __init__(self, global_timeline: List[str]):
        self.timeline = sorted(global_timeline)
        self.timeset = frozenset(self.timeline)

    def is_trading_timestamp(self, timestamp: str) -> bool:
        return timestamp in self.timeset

    def next_trading_timestamp(self, timestamp: str) -> str | None:
        """Finds the first timestamp strictly greater than the given timestamp."""
        for t in self.timeline:
            if t > timestamp:
                return t
        return None

    def previous_trading_timestamp(self, timestamp: str) -> str | None:
        """Finds the first timestamp strictly less than the given timestamp."""
        for t in reversed(self.timeline):
            if t < timestamp:
                return t
        return None

class DataGapAnalyzer:
    @staticmethod
    def analyze(timestamps: List[str], global_timeline: List[str]) -> dict:
        if not timestamps:
            return {"gap_count": 0, "largest_gap": 0, "gap_warning": "INSUFFICIENT_DATA"}
            
        try:
            start_idx = global_timeline.index(timestamps[0])
            end_idx = global_timeline.index(timestamps[-1])
        except ValueError:
            return {"gap_count": 0, "largest_gap": 0, "gap_warning": "INSUFFICIENT_DATA"}
            
        expected_bars = end_idx - start_idx + 1
        actual_bars = len(timestamps)
        gap_count = expected_bars - actual_bars
        
        largest_gap = 0
        gaps = 0
        if len(timestamps) > 1:
            for i in range(1, len(timestamps)):
                idx1 = global_timeline.index(timestamps[i-1])
                idx2 = global_timeline.index(timestamps[i])
                gap = idx2 - idx1 - 1
                if gap > 0:
                    gaps += gap
                    if gap > largest_gap:
                        largest_gap = gap
                        
        if gap_count > 0:
            warning = "GAP_DETECTED"
        else:
            warning = "NO_GAP"
            
        return {"gap_count": gaps, "largest_gap": largest_gap, "gap_warning": warning}

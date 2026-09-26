from core.schemas import PerformanceAttribution
from typing import Dict, Any

class ScoreAnalysisEngine:
    @staticmethod
    def evaluate_score_monotonicity(attribution: PerformanceAttribution) -> str:
        buckets = ["60_69", "70_79", "80_89", "90_100"]
        valid_buckets = []
        for b in buckets:
            grp = attribution.by_score.get(b)
            if grp and grp.trades_closed > 0 and grp.win_rate is not None:
                valid_buckets.append(grp.win_rate)
                
        if len(valid_buckets) < 2:
            return "INSUFFICIENT_SAMPLE"
            
        is_increasing = all(valid_buckets[i] <= valid_buckets[i+1] for i in range(len(valid_buckets)-1))
        
        return "MONOTONIC" if is_increasing else "NON_MONOTONIC"

    @staticmethod
    def evaluate_confidence_alignment(attribution: PerformanceAttribution) -> str:
        buckets = ["0_59", "60_69", "70_79", "80_89", "90_100"]
        valid_buckets = []
        for b in buckets:
            grp = attribution.by_confidence.get(b)
            if grp and grp.trades_closed > 0 and grp.win_rate is not None:
                valid_buckets.append(grp.win_rate)
                
        if len(valid_buckets) < 2:
            return "INSUFFICIENT_SAMPLE"
            
        is_increasing = all(valid_buckets[i] <= valid_buckets[i+1] for i in range(len(valid_buckets)-1))
        
        return "CONFIDENCE_ALIGNED" if is_increasing else "CONFIDENCE_NOT_ALIGNED"

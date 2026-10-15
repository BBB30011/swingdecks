import math
import os
import sys
from typing import List, Dict, Any, Tuple
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.intelligence_engine import IntelligenceEngine

class OOSResearchFramework:
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.engine = IntelligenceEngine(db_path=db_path)
    
    def audit_dataset(self) -> Dict[str, Any]:
        """Audits the dataset before any experiments are run."""
        stats = {}
        # Support published_at column name
        events_query = "SELECT COUNT(*), MIN(published_at), MAX(published_at) FROM fact_event"
        res = self.engine._execute_query(events_query)
        if res:
            stats['event_count'] = res[0][0]
            stats['min_date'] = res[0][1]
            stats['max_date'] = res[0][2]
            
        entities_query = "SELECT COUNT(DISTINCT entity_id) FROM dim_entity"
        res_e = self.engine._execute_query(entities_query)
        stats['unique_entities'] = res_e[0][0] if res_e else 0
        return stats

    def split_oos(self, candidate_family_events: List[Dict[str, Any]], train_ratio: float = 0.5, val_ratio: float = 0.2) -> Dict[str, List[Dict[str, Any]]]:
        """Chronologically splits events into train, validation, and OOS."""
        # Sort chronologically
        sorted_events = sorted(candidate_family_events, key=lambda x: x['publication_time'] or datetime.datetime.min)
        n = len(sorted_events)
        
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)
        
        return {
            "train": sorted_events[:train_end],
            "validation": sorted_events[train_end:val_end],
            "oos": sorted_events[val_end:]
        }
        
    def _permutation_test(self, group1: List[float], num_permutations: int = 1000) -> float:
        """
        Simple permutation test for whether mean > 0 (or != 0).
        Since we don't have a 2-sample case, we compare against 0.
        We randomly flip the signs of the observations.
        """
        import random
        if not group1:
            return 1.0
        
        observed_mean = sum(group1) / len(group1)
        if observed_mean == 0:
            return 1.0
            
        count_extreme = 0
        for _ in range(num_permutations):
            permuted_mean = sum(val if random.random() > 0.5 else -val for val in group1) / len(group1)
            if abs(permuted_mean) >= abs(observed_mean):
                count_extreme += 1
                
        return count_extreme / num_permutations

    def statistical_validation(self, differentials: List[float]) -> Dict[str, Any]:
        """Calculates statistical properties of the differential returns."""
        n = len(differentials)
        if n == 0:
            return {"status": "INSUFFICIENT_SAMPLE"}
            
        mean = sum(differentials) / n
        sorted_diffs = sorted(differentials)
        median = sorted_diffs[n//2] if n % 2 != 0 else (sorted_diffs[n//2 - 1] + sorted_diffs[n//2]) / 2.0
        
        variance = sum((x - mean) ** 2 for x in differentials) / (n - 1) if n > 1 else 0
        std_dev = math.sqrt(variance)
        
        effect_size = mean / std_dev if std_dev > 0 else 0
        p_value = self._permutation_test(differentials)
        
        return {
            "status": "COMPLETED",
            "n": n,
            "mean": mean,
            "median": median,
            "std_dev": std_dev,
            "effect_size": effect_size,
            "p_value": p_value
        }

    def run_experiment(self, event_type: str = 'POLICY') -> Dict[str, Any]:
        """Runs the deterministic chronological experiment on a specific candidate family."""
        
        # 1. Fetch Candidate Events
        query = "SELECT event_id, published_at FROM fact_event WHERE event_type = ? ORDER BY published_at ASC"
        events_rows = self.engine._execute_query(query, (event_type,))
        
        events = [{"event_id": r[0], "publication_time": r[1]} for r in events_rows]
        
        if not events:
            return {"status": "NO_EVENTS_FOUND"}
            
        # 2. Chronological Split (Train 50%, Val 20%, OOS 30%)
        # In a very small dataset (e.g. 1 event), we just use the event as OOS to prove architecture,
        # but realistically this fails statistical significance.
        if len(events) == 1:
            split = {"train": [], "validation": [], "oos": events}
        else:
            split = self.split_oos(events)
            
        results = {}
        for phase, phase_events in split.items():
            phase_differentials = []
            phase_analysis = []
            
            for event in phase_events:
                # The prediction timestamp is exactly the event timestamp.
                # We analyze impact using the knowledge available at that moment.
                decision_timestamp = event['publication_time']
                # But wait, analyze_event_impact computes target_reaction vs peer_average_reaction.
                impact = self.engine.analyze_event_impact(event['event_id'], as_of=str(decision_timestamp))
                
                if impact.get("status") == "ANALYSIS_COMPLETE":
                    for res in impact["results"]:
                        phase_differentials.append(res["differential"])
                        phase_analysis.append(res)
                        
            stats = self.statistical_validation(phase_differentials)
            results[phase] = {
                "events_tested": len(phase_events),
                "differentials_found": len(phase_differentials),
                "stats": stats,
                "raw_results": phase_analysis
            }
            
        return {
            "candidate_family": event_type,
            "split_results": results
        }

if __name__ == "__main__":
    oos = OOSResearchFramework()
    print("Audit:", oos.audit_dataset())
    print("Experiment:", oos.run_experiment('POLICY'))

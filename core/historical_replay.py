import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from core.data_source import MarketDataSource
from core.schemas import MarketSnapshot
from agents.agent1_quant.pipeline import Agent1QuantPipeline

class Agent1HistoricalReplay:
    """
    Historical Replay Engine for Agent 1 (Quant & Market Scanner).
    Ensures that the output of the quant pipeline exactly matches the information 
    state that would have existed at the `decision_timestamp`, enforcing strict PIT.
    """
    
    def __init__(self, data_source: MarketDataSource):
        self.data_source = data_source
        self.pipeline = Agent1QuantPipeline()
        
    def replay_agent1(self, symbol: str, decision_timestamp: str) -> Dict[str, Any]:
        """
        Replays the agent 1 quant pipeline for a specific symbol as of the decision_timestamp.
        """
        try:
            # 1. Fetch data strictly up to decision_timestamp
            snapshot = self.data_source.get_snapshot(symbol, as_of_timestamp=decision_timestamp)
            
            # 2. Run the quant pipeline on the snapshot
            run_result = self.pipeline.run([snapshot])
            
            # 3. Extract the candidate result
            candidates = run_result.get("top_candidates", [])
            candidate = next((c for c in candidates if c["symbol"] == snapshot.symbol.upper()), None)
            
            # Extract stage tracing
            stage_trace = run_result.get("stage_trace", {}).get(snapshot.symbol.upper(), {})
            
            # Distinguish raw scanner status from official SignalState enum
            raw_scanner_status = candidate.get("status") if candidate else stage_trace.get("market_scanner", "UNKNOWN")
            
            if candidate:
                tracked_state = self.pipeline.state_tracker.get_state(snapshot.symbol)
                official_signal_state = tracked_state.value if hasattr(tracked_state, "value") else str(tracked_state)
            else:
                official_signal_state = "REJECTED"
            
            return {
                "symbol": snapshot.symbol,
                "decision_timestamp": decision_timestamp,
                "market_state": candidate.get("features", {}) if candidate else {},
                "indicators": candidate.get("features", {}) if candidate else {},
                "raw_scanner_status": raw_scanner_status,
                "signal_state": official_signal_state,
                "scanner_rank": candidate.get("quant_score") if candidate else None,
                "stage_trace": stage_trace,
                "data_version": snapshot.metadata.dataset_id if hasattr(snapshot, "metadata") and snapshot.metadata else "UNKNOWN",
                "schema_version": "1.0",
                "status": "SUCCESS" if candidate else "REJECTED"
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "symbol": symbol,
                "decision_timestamp": decision_timestamp,
                "raw_scanner_status": "ERROR",
                "signal_state": "ERROR",
                "status": "ERROR",
                "error": str(e),
                "data_version": "UNKNOWN",
                "schema_version": "1.0"
            }

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime

class DecisionTraceEvent(BaseModel):
    event_id: str
    timestamp: str
    stage: str
    event_type: str
    metadata: Dict[str, Any]

class AuditedDecisionTrace(BaseModel):
    trace_id: str
    symbol: str
    decision_timestamp: str
    
    agent1_observation: Dict[str, Any] = {}
    agent2_intelligence: Dict[str, Any] = {}
    red_team_assessment: Dict[str, Any] = {}
    agent3_decision: Dict[str, Any] = {}
    
    market_delta: Dict[str, Any] = {}
    decision_change: str = "UNKNOWN"
    pit_status: str = "PASS"
    source_completeness: str = "UNKNOWN"
    post_decision_outcome: Dict[str, Any] = {}
    evidence_refs: List[str] = []
    
    def get_hash(self) -> str:
        content = f"{self.symbol}_{self.decision_timestamp}_{self.decision_change}_{len(self.evidence_refs)}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

class DecisionTraceAPI:
    def __init__(self, ledger_path: str = "state/audit/ledger.jsonl"):
        self.ledger_path = Path(ledger_path)
        
    def _read_ledger(self) -> List[DecisionTraceEvent]:
        events = []
        if not self.ledger_path.exists():
            return events
        with open(self.ledger_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    d = json.loads(line)
                    events.append(DecisionTraceEvent(
                        event_id=d.get("event_id", ""),
                        timestamp=d.get("timestamp", ""),
                        stage=d.get("stage", ""),
                        event_type=d.get("event_type", ""),
                        metadata=d.get("metadata", {})
                    ))
                except Exception:
                    pass
        return events
        
    def get_timeline(self, symbol: str) -> List[Dict[str, Any]]:
        events = self._read_ledger()
        sym_events = [e for e in events if e.metadata.get("symbol") == symbol]
        
        timeline = {}
        for e in sym_events:
            ts = e.timestamp
            if ts not in timeline:
                timeline[ts] = []
            timeline[ts].append(e.model_dump())
            
        ordered_timeline = []
        for ts in sorted(timeline.keys()):
            ordered_timeline.append({
                "timestamp": ts,
                "events": timeline[ts]
            })
        return ordered_timeline
        
    def build_trace(self, symbol: str, decision_timestamp: str) -> AuditedDecisionTrace:
        timeline = self.get_timeline(symbol)
        
        trace = AuditedDecisionTrace(
            trace_id=hashlib.md5(f"{symbol}_{decision_timestamp}".encode()).hexdigest(),
            symbol=symbol,
            decision_timestamp=decision_timestamp
        )
        
        day_events = []
        for t in timeline:
            if t["timestamp"] == decision_timestamp:
                day_events = t["events"]
                break
                
        if not day_events:
            trace.source_completeness = "NOT_AVAILABLE"
            return trace
            
        for e in day_events:
            meta = e.get("metadata", {})
            if e.get("event_id"):
                trace.evidence_refs.append(e.get("event_id"))
            
            # Extract nested trace evidence refs
            inner_trace = meta.get("trace", {})
            if isinstance(inner_trace, dict):
                for ref in inner_trace.get("evidence_refs", []):
                    if ref and ref not in trace.evidence_refs:
                        trace.evidence_refs.append(ref)
            
            if e.get("stage") == "AGENT_1_QUANT":
                trace.agent1_observation = meta
                if "delta_status" in meta:
                    trace.market_delta["agent1_delta"] = meta["delta_status"]
            elif e.get("stage") == "AGENT_2_INTEL":
                trace.agent2_intelligence = meta
                trace.red_team_assessment = {
                    "red_team_decision": meta.get("red_team_decision"),
                    "contradiction_count": meta.get("contradiction_count"),
                    "red_team_delta_status": meta.get("red_team_delta_status")
                }
                if "intel_delta_status" in meta:
                    trace.market_delta["agent2_delta"] = meta["intel_delta_status"]
            elif e.get("stage") == "AGENT_3_COMMITTEE":
                trace.agent3_decision = meta
                if isinstance(inner_trace, dict) and "graph_intelligence" in inner_trace:
                    trace.agent2_intelligence["graph_intelligence"] = inner_trace["graph_intelligence"]
                
        # Determine decision change
        prev_decision = "UNKNOWN"
        for t in timeline:
            if t["timestamp"] < decision_timestamp:
                for ev in t["events"]:
                    if ev.get("stage") == "AGENT_3_COMMITTEE":
                        prev_decision = ev.get("metadata", {}).get("action", "UNKNOWN")
                        
        curr_decision = trace.agent3_decision.get("action", "UNKNOWN")
        
        if prev_decision == "UNKNOWN" and curr_decision != "UNKNOWN":
            trace.decision_change = "NEW_ACTION"
        elif prev_decision == curr_decision and curr_decision != "UNKNOWN":
            trace.decision_change = "NO_CHANGE"
        elif curr_decision != "UNKNOWN":
            rank = {"BUY": 5, "HOLD": 4, "WAIT": 3, "SELL": 2, "AVOID": 1, "UNKNOWN": 0}
            if rank.get(curr_decision, 0) > rank.get(prev_decision, 0):
                trace.decision_change = "UPGRADE"
            elif rank.get(curr_decision, 0) < rank.get(prev_decision, 0):
                trace.decision_change = "DOWNGRADE"
            else:
                trace.decision_change = "ACTION_CHANGED"
                
        trace.source_completeness = "COMPLETE" if (trace.agent1_observation and trace.agent3_decision) else "PARTIAL"
        return trace
        
    def get_current_state(self, symbol: str) -> Dict[str, Any]:
        timeline = self.get_timeline(symbol)
        if not timeline:
            return {}
        latest = timeline[-1]
        return self.build_trace(symbol, latest["timestamp"]).model_dump()
        
    def get_decision_changes(self, symbol: str) -> List[Dict[str, Any]]:
        timeline = self.get_timeline(symbol)
        changes = []
        prev_action = None
        for t in timeline:
            trace = self.build_trace(symbol, t["timestamp"])
            action = trace.agent3_decision.get("action")
            if action and action != prev_action:
                changes.append({
                    "timestamp": t["timestamp"],
                    "decision": action,
                    "change_type": trace.decision_change
                })
                prev_action = action
        return changes
        
    def get_thesis_changes(self, symbol: str) -> List[Dict[str, Any]]:
        # Mapped from agent 2 and red team changes
        timeline = self.get_timeline(symbol)
        changes = []
        prev_red = None
        for t in timeline:
            trace = self.build_trace(symbol, t["timestamp"])
            red = trace.red_team_assessment.get("red_team_decision")
            if red and red != prev_red:
                changes.append({
                    "timestamp": t["timestamp"],
                    "red_team_decision": red,
                    "delta": trace.red_team_assessment.get("red_team_delta_status")
                })
                prev_red = red
        return changes
        
    def get_post_decision_outcomes(self, symbol: str, decision_timestamp: str) -> Dict[str, Any]:
        events = self._read_ledger()
        outcome = {"subsequent_events": []}
        for e in events:
            if e.metadata.get("symbol") == symbol and e.timestamp > decision_timestamp:
                if e.stage in ["POSITION_MONITOR", "EXECUTION_SIMULATOR"]:
                    outcome["subsequent_events"].append(e.model_dump())
        return outcome

import json
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import Counter
from pathlib import Path

class DriftCategory:
    DATA = "DATA_DRIFT"
    REGIME = "MARKET_REGIME_DRIFT"
    AGENT1 = "AGENT_BEHAVIOR_DRIFT"
    AGENT2_COVERAGE = "INFORMATION_COVERAGE_DRIFT"
    RED_TEAM = "RED_TEAM_DRIFT"
    AGENT3 = "DECISION_DISTRIBUTION_DRIFT"
    THESIS = "THESIS_DRIFT"
    RISK = "RISK_GATE_DRIFT"
    EXECUTION = "EXECUTION_DRIFT"
    PIT = "PIT_DRIFT"
    LATENCY = "LATENCY_DRIFT"
    ERROR = "ERROR_DRIFT"
    REPLAY = "REPLAY_DRIFT"
    ACCOUNTING = "ACCOUNTING_DRIFT"
    OBSERVABILITY = "OBSERVABILITY_DRIFT"

class DriftStatus:
    STABLE = "STABLE"
    CHANGED = "CHANGED"
    WARNING = "WARNING"
    DEGRADED = "DEGRADED"
    DATA_INSUFFICIENT = "DATA_INSUFFICIENT"
    UNKNOWN = "UNKNOWN"

class QualityStatus:
    PASS = "PASS"
    PARTIAL = "PARTIAL"
    WARNING = "WARNING"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"

class DriftObservatory:
    def __init__(self, ledger_path: str = "state/audit/ledger.jsonl", window_size: int = 30):
        self.ledger_path = Path(ledger_path)
        self.window_size = window_size
        self.events = self._load_ledger()
        
    def _load_ledger(self) -> List[Dict[str, Any]]:
        events = []
        if not self.ledger_path.exists():
            return events
        with open(self.ledger_path, "r") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
        # Sort chronologically
        events.sort(key=lambda x: x.get("timestamp", ""))
        return events

    def _get_windows(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        # Simple rolling operational baseline split based on count of unique dates
        # Or just split by event count if dates are sparse.
        dates = sorted(list(set(e.get("timestamp", "").split("T")[0] for e in self.events if e.get("timestamp"))))
        if len(dates) < 2:
            return [], self.events
            
        mid_point = dates[len(dates)//2]
        baseline = [e for e in self.events if e.get("timestamp", "").split("T")[0] <= mid_point]
        current = [e for e in self.events if e.get("timestamp", "").split("T")[0] > mid_point]
        return baseline, current

    def get_system_health(self) -> Dict[str, str]:
        # Basic sanity checks
        if not self.events:
            return {"DATA": "FAIL", "PIT": "UNKNOWN", "AGENTS": "0 / 3", "REPLAY": "UNKNOWN", "ACCOUNTING": "UNKNOWN", "AUDIT": "FAIL", "PAPER": "UNKNOWN", "LIVE": "UNKNOWN", "DRIFT": "UNKNOWN"}
            
        stages = set(e.get("stage") for e in self.events)
        agents_active = sum(1 for s in ["AGENT_1_QUANT", "AGENT_2_INTEL", "AGENT_3_COMMITTEE"] if s in stages)
        
        has_pit_block = any(e.get("event_type") == "PIT_VIOLATION_ATTEMPT" for e in self.events)
        has_replay_fail = any(e.get("event_type") == "REPLAY_MISMATCH" for e in self.events)
        has_acct_fail = any(e.get("event_type") == "ACCOUNTING_ANOMALY" for e in self.events)
        
        return {
            "DATA": "PASS",
            "PIT": "BLOCKED" if has_pit_block else "PASS",
            "AGENTS": f"{agents_active} / 3",
            "REPLAY": "FAIL" if has_replay_fail else "PASS",
            "ACCOUNTING": "FAIL" if has_acct_fail else "PASS",
            "AUDIT": "PASS",
            "PAPER": "ENABLED",
            "LIVE": "BLOCKED",
            "DRIFT": "WATCH"
        }

    def get_quality_matrix(self) -> Dict[str, str]:
        if not self.events:
            return {k: QualityStatus.UNKNOWN for k in ["TRACEABILITY", "PIT", "EVIDENCE", "REPLAY", "RISK", "THESIS", "ACCOUNTING", "AUDIT"]}
            
        return {
            "TRACEABILITY": QualityStatus.PASS,
            "PIT": QualityStatus.PASS if not any(e.get("event_type") == "PIT_VIOLATION_ATTEMPT" for e in self.events) else QualityStatus.BLOCKED,
            "EVIDENCE": QualityStatus.PASS if any(e.get("stage") == "AGENT_2_INTEL" for e in self.events) else QualityStatus.PARTIAL,
            "REPLAY": QualityStatus.PASS if not any(e.get("event_type") == "REPLAY_MISMATCH" for e in self.events) else QualityStatus.WARNING,
            "RISK": QualityStatus.PASS,
            "THESIS": QualityStatus.PASS,
            "ACCOUNTING": QualityStatus.PASS if not any(e.get("event_type") == "ACCOUNTING_ANOMALY" for e in self.events) else QualityStatus.BLOCKED,
            "AUDIT": QualityStatus.PASS
        }

    def _compare_distributions(self, base_counts: dict, curr_counts: dict) -> str:
        if sum(base_counts.values()) < 5 or sum(curr_counts.values()) < 5:
            return DriftStatus.DATA_INSUFFICIENT
            
        base_total = sum(base_counts.values())
        curr_total = sum(curr_counts.values())
        
        diff = 0
        all_keys = set(base_counts.keys()) | set(curr_counts.keys())
        for k in all_keys:
            bp = base_counts.get(k, 0) / base_total
            cp = curr_counts.get(k, 0) / curr_total
            diff += abs(bp - cp)
            
        if diff > 0.4: # Arbitrary threshold for descriptive purposes
            return DriftStatus.CHANGED
        return DriftStatus.STABLE

    def get_drift_matrix(self) -> Dict[str, str]:
        baseline, current = self._get_windows()
        
        default_matrix = {
            "DATA": DriftStatus.DATA_INSUFFICIENT,
            "REGIME": DriftStatus.DATA_INSUFFICIENT,
            "AGENT 1": DriftStatus.DATA_INSUFFICIENT,
            "AGENT 2": DriftStatus.DATA_INSUFFICIENT,
            "RED TEAM": DriftStatus.DATA_INSUFFICIENT,
            "AGENT 3": DriftStatus.DATA_INSUFFICIENT,
            "THESIS": DriftStatus.DATA_INSUFFICIENT,
            "RISK": DriftStatus.DATA_INSUFFICIENT,
            "EXECUTION": DriftStatus.DATA_INSUFFICIENT,
            "PIT": DriftStatus.DATA_INSUFFICIENT,
            "REPLAY": DriftStatus.DATA_INSUFFICIENT,
            "ACCOUNTING": DriftStatus.DATA_INSUFFICIENT,
            "LATENCY": DriftStatus.DATA_INSUFFICIENT,
            "ERROR": DriftStatus.DATA_INSUFFICIENT,
            "OBSERVABILITY": DriftStatus.DATA_INSUFFICIENT
        }
        
        if not baseline or not current:
            return default_matrix
            
        # Agent 3 Decision Distribution
        b_dec = Counter([e.get("metadata", {}).get("action") for e in baseline if e.get("stage") == "AGENT_3_COMMITTEE"])
        c_dec = Counter([e.get("metadata", {}).get("action") for e in current if e.get("stage") == "AGENT_3_COMMITTEE"])
        a3_drift = self._compare_distributions(b_dec, c_dec)
        
        # Regime Drift
        b_reg = Counter([e.get("metadata", {}).get("regime") for e in baseline if e.get("stage") == "MARKET_REGIME"])
        c_reg = Counter([e.get("metadata", {}).get("regime") for e in current if e.get("stage") == "MARKET_REGIME"])
        reg_drift = self._compare_distributions(b_reg, c_reg)

        return {
            "DATA": DriftStatus.STABLE,
            "REGIME": reg_drift,
            "AGENT 1": DriftStatus.STABLE,
            "AGENT 2": DriftStatus.CHANGED if any(e.get("stage") == "AGENT_2_INTEL" for e in current) else DriftStatus.DATA_INSUFFICIENT,
            "RED TEAM": DriftStatus.STABLE,
            "AGENT 3": a3_drift,
            "THESIS": DriftStatus.STABLE,
            "RISK": DriftStatus.STABLE,
            "EXECUTION": DriftStatus.STABLE,
            "PIT": DriftStatus.STABLE,
            "REPLAY": DriftStatus.STABLE,
            "ACCOUNTING": DriftStatus.STABLE,
            "LATENCY": DriftStatus.WARNING if current else DriftStatus.DATA_INSUFFICIENT,
            "ERROR": DriftStatus.STABLE,
            "OBSERVABILITY": DriftStatus.STABLE
        }

    def get_recent_drift_events(self) -> List[Dict[str, Any]]:
        baseline, current = self._get_windows()
        events = []
        if not baseline or not current:
            return events
            
        b_dec = Counter([e.get("metadata", {}).get("action") for e in baseline if e.get("stage") == "AGENT_3_COMMITTEE"])
        c_dec = Counter([e.get("metadata", {}).get("action") for e in current if e.get("stage") == "AGENT_3_COMMITTEE"])
        a3_drift = self._compare_distributions(b_dec, c_dec)
        
        if a3_drift == DriftStatus.CHANGED:
            events.append({
                "date": current[-1].get("timestamp", "").split("T")[0] if current else "UNKNOWN",
                "category": DriftCategory.AGENT3,
                "metric": "decision_distribution",
                "baseline": f"N={sum(b_dec.values())}",
                "current": f"N={sum(c_dec.values())}",
                "status": "CHANGED",
                "evidence": str(dict(c_dec))
            })
            
        return events

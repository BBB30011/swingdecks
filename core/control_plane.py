import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path

from core.drift_observatory import DriftObservatory, DriftStatus

@dataclass
class ControlPlaneSnapshot:
    snapshot_id: str
    generated_at: str
    system_status: str
    daemon: Dict[str, Any]
    market: Dict[str, Any]
    agents: Dict[str, Any]
    positions: List[Dict[str, Any]]
    thesis: Dict[str, Any]
    drift: Dict[str, str]
    accounting: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    recent_events: List[Dict[str, Any]]
    what_changed: List[Dict[str, Any]]

class ControlPlaneAggregator:
    def __init__(self, ledger_path: str = "state/audit/ledger.jsonl", daemon_state_path: str = "runtime/continuous_desk_daemon_state.json"):
        self.ledger_path = Path(ledger_path)
        self.daemon_state_path = Path(daemon_state_path)
        self.events = self._load_ledger()
        self.daemon_state = self._load_daemon_state()
        
    def _load_ledger(self) -> List[Dict[str, Any]]:
        events = []
        if not self.ledger_path.exists():
            return events
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                try:
                    events.append(json.loads(line))
                except Exception:
                    pass
        events.sort(key=lambda x: x.get("timestamp", ""))
        return events
        
    def _load_daemon_state(self) -> Dict[str, Any]:
        if not self.daemon_state_path.exists():
            return {}
        try:
            with open(self.daemon_state_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def get_snapshot(self) -> ControlPlaneSnapshot:
        now = datetime.now(timezone.utc).isoformat()
        snapshot_id = f"SNAP_{int(datetime.now().timestamp())}"
        
        # Base processing
        latest_state = {}
        positions = {}
        alerts = []
        what_changed = []
        
        has_pit_block = False
        has_replay_block = False
        has_accounting_block = False
        
        # Analyze ledger
        for e in self.events:
            sym = e.get("metadata", {}).get("symbol")
            stage = e.get("stage")
            evt_type = e.get("event_type")
            
            if evt_type == "PIT_VIOLATION_ATTEMPT":
                has_pit_block = True
                alerts.append({"priority": "CRITICAL", "message": "PIT violation attempt detected", "event": e})
            elif evt_type == "REPLAY_MISMATCH":
                has_replay_block = True
                alerts.append({"priority": "CRITICAL", "message": "Replay mismatch detected", "event": e})
            elif evt_type == "ACCOUNTING_ANOMALY":
                has_accounting_block = True
                alerts.append({"priority": "CRITICAL", "message": "Accounting variance anomaly", "event": e})
                
            if sym:
                if sym not in latest_state:
                    latest_state[sym] = {"regime": "UNKNOWN", "agent1": {}, "agent2": {}, "agent3": {}, "red_team": {}}
                
                if stage == "MARKET_REGIME":
                    if latest_state[sym]["regime"] != e.get("metadata", {}).get("regime"):
                        what_changed.append({"date": e.get("timestamp"), "symbol": sym, "type": "Market", "change": f"Regime -> {e.get('metadata', {}).get('regime')}"})
                    latest_state[sym]["regime"] = e.get("metadata", {}).get("regime", "UNKNOWN")
                elif stage == "AGENT_1_QUANT":
                    latest_state[sym]["agent1"] = e.get("metadata", {})
                elif stage == "AGENT_2_INTEL":
                    latest_state[sym]["agent2"] = e.get("metadata", {})
                elif stage == "AGENT_3_COMMITTEE":
                    old_action = latest_state[sym]["agent3"].get("action", "UNKNOWN")
                    new_action = e.get("metadata", {}).get("action", "UNKNOWN")
                    if old_action != "UNKNOWN" and old_action != new_action:
                        what_changed.append({"date": e.get("timestamp"), "symbol": sym, "type": "Agent 3", "change": f"{old_action} -> {new_action}"})
                    latest_state[sym]["agent3"] = e.get("metadata", {})
                elif stage == "PORTFOLIO" or evt_type in ["POSITION_OPENED", "POSITION_CLOSED", "POSITION_UPDATED", "POSITION_ADDED"]:
                    if evt_type in ["POSITION_OPENED", "POSITION_ADDED"]:
                        positions[sym] = e.get("metadata", {})
                    elif evt_type == "POSITION_CLOSED":
                        if sym in positions:
                            del positions[sym]
                    elif evt_type == "POSITION_UPDATED":
                        if sym in positions:
                            positions[sym].update(e.get("metadata", {}))

        # Drift Observatory
        obs = DriftObservatory(ledger_path=str(self.ledger_path))
        drift_matrix = obs.get_drift_matrix()
        
        # System Status Precedence
        # BLOCKED -> RECOVERY -> DEGRADED -> WATCH -> WAITING_FOR_DATA -> HEALTHY -> UNKNOWN
        status = "UNKNOWN"
        if has_pit_block or has_replay_block or has_accounting_block:
            status = "BLOCKED"
        elif not self.events:
            status = "WAITING_FOR_DATA"
        elif any(v in [DriftStatus.DEGRADED, DriftStatus.DATA_INSUFFICIENT] for v in drift_matrix.values()):
            if status not in ["BLOCKED", "RECOVERY"]:
                status = "DEGRADED"
        elif any(v in [DriftStatus.WARNING, DriftStatus.CHANGED] for v in drift_matrix.values()):
            if status not in ["BLOCKED", "RECOVERY", "DEGRADED"]:
                status = "WATCH"
        else:
            status = "HEALTHY"
            
        if self.daemon_state.get("status") == False and status != "BLOCKED":
            status = "WAITING_FOR_DATA"

        return ControlPlaneSnapshot(
            snapshot_id=snapshot_id,
            generated_at=now,
            system_status=status,
            daemon=self.daemon_state,
            market={"latest_date": self.daemon_state.get("processed_dates", ["UNKNOWN"])[-1] if self.daemon_state.get("processed_dates") else "UNKNOWN"},
            agents={"topology": "3 / 3", "agent1": "PASS", "agent2": "PASS", "agent3": "PASS"},
            positions=[{"symbol": k, **v} for k, v in positions.items()],
            thesis={},
            drift=drift_matrix,
            accounting={"status": "BLOCKED" if has_accounting_block else "PASS"},
            alerts=alerts,
            recent_events=self.events[-10:] if self.events else [],
            what_changed=what_changed[-10:]
        )

import hashlib
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from core.control_plane import ControlPlaneAggregator, ControlPlaneSnapshot

class IncidentStatus:
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RECOVERING = "RECOVERING"
    VERIFYING = "VERIFYING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    REOPENED = "REOPENED"

class IncidentSeverity:
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class IncidentEvidenceBundle:
    incident_id: str
    detection_timestamp: str
    control_plane_snapshot_id: str
    trigger_event: Dict[str, Any]
    related_events: List[Dict[str, Any]]
    source_file: str
    symbol: str
    session: str
    verification_evidence: Optional[Dict[str, Any]] = None

@dataclass
class Incident:
    incident_id: str
    deterministic_identity: str
    detected_at: str
    first_seen_at: str
    last_seen_at: str
    category: str
    severity: str
    status: str
    component: str
    symbol: str
    session_date: str
    summary: str
    trigger_event_id: str
    related_event_ids: List[str]
    source_refs: List[str]
    evidence_bundle: IncidentEvidenceBundle
    current_state: str
    root_cause: str
    impact: str
    recovery_plan: str
    recovery_actions: List[Dict[str, Any]]
    verification_status: str
    resolved_at: Optional[str] = None
    closed_at: Optional[str] = None
    incident_hash: str = ""
    occurrence_count: int = 1

    def __post_init__(self):
        hash_input = f"{self.deterministic_identity}_{self.detected_at}_{self.status}"
        self.incident_hash = hashlib.sha256(hash_input.encode()).hexdigest()

class IncidentCenter:
    def __init__(self, ledger_path: str = "state/audit/ledger.jsonl", daemon_state_path: str = "runtime/continuous_desk_daemon_state.json"):
        self.ledger_path = Path(ledger_path)
        self.daemon_state_path = Path(daemon_state_path)
        self.control_plane = ControlPlaneAggregator(ledger_path, daemon_state_path)
        self.incidents: Dict[str, Incident] = {}

    def _generate_fingerprint(self, category: str, component: str, symbol: str, session: str, trigger_id: str) -> str:
        fingerprint_input = f"{category}{component}{symbol}{session}{trigger_id}"
        return hashlib.sha256(fingerprint_input.encode()).hexdigest()

    def scan_for_incidents(self) -> List[Incident]:
        snap = self.control_plane.get_snapshot()
        detected_incidents = []
        now = datetime.now(timezone.utc).isoformat()
        
        # We parse the ledger directly to find anomalies, plus we use snap.alerts
        events = self.control_plane.events
        
        for e in events:
            stage = e.get("stage", "UNKNOWN")
            evt_type = e.get("event_type", "UNKNOWN")
            sym = e.get("metadata", {}).get("symbol", "SYS")
            dt = e.get("timestamp", now)
            
            # Detect PIT Violation
            if evt_type == "PIT_VIOLATION_ATTEMPT":
                detected_incidents.append(self._create_incident(
                    category="PIT", component=stage, severity=IncidentSeverity.CRITICAL,
                    symbol=sym, session=dt.split("T")[0], trigger_event=e, snap=snap,
                    summary="Future information access blocked", impact="PIT_BLOCKED", root_cause="PROVEN"
                ))
            
            # Detect Replay Mismatch
            elif evt_type == "REPLAY_MISMATCH":
                detected_incidents.append(self._create_incident(
                    category="REPLAY", component=stage, severity=IncidentSeverity.CRITICAL,
                    symbol=sym, session=dt.split("T")[0], trigger_event=e, snap=snap,
                    summary="Replay trajectory diverges from historical trace", impact="PROCESS_BLOCKED", root_cause="PROVEN"
                ))
                
            # Detect Accounting Anomaly
            elif evt_type == "ACCOUNTING_ANOMALY":
                detected_incidents.append(self._create_incident(
                    category="ACCOUNTING", component=stage, severity=IncidentSeverity.CRITICAL,
                    symbol=sym, session=dt.split("T")[0], trigger_event=e, snap=snap,
                    summary="Ledger P&L invariant variance detected", impact="ACCOUNTING_BLOCKED", root_cause="PROVEN"
                ))
                
            # Agent / Data Failure Separation (DEF-INCIDENT-001)
            elif "ERROR" in evt_type or "FAILED" in evt_type:
                cat = "DATA" if "DATA" in stage else "AGENT"
                summary = "Data validation error" if cat == "DATA" else "Agent execution error"
                impact = "DATA_BLOCKED" if cat == "DATA" else "DEGRADED_OBSERVABILITY"
                
                # Check temporal context for root cause
                try:
                    evt_time = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                    current_time = datetime.now(timezone.utc)
                    age_days = (current_time - evt_time).days
                    is_historical = age_days > 1
                except:
                    is_historical = True

                root_cause = "HISTORICAL_PARSE" if is_historical else "UNKNOWN"
                
                detected_incidents.append(self._create_incident(
                    category=cat, component=stage, severity=IncidentSeverity.HIGH,
                    symbol=sym, session=dt.split("T")[0], trigger_event=e, snap=snap,
                    summary=summary, impact=impact, root_cause=root_cause
                ))
                
            # Live Boundary Attempt
            elif evt_type == "LIVE_EXECUTION_ATTEMPT":
                detected_incidents.append(self._create_incident(
                    category="LIVE_BOUNDARY", component=stage, severity=IncidentSeverity.CRITICAL,
                    symbol=sym, session=dt.split("T")[0], trigger_event=e, snap=snap,
                    summary="System attempted to breach paper boundary", impact="SECURITY_BLOCKED", root_cause="PROVEN"
                ))
                
        # Daemon checks
        if snap.daemon:
            if snap.daemon.get("status") == False and snap.daemon.get("intentionally_stopped") == False:
                # Daemon stopped unexpectedly
                detected_incidents.append(self._create_incident(
                    category="DAEMON", component="CONTINUOUS_DESK", severity=IncidentSeverity.CRITICAL,
                    symbol="SYS", session=now.split("T")[0], trigger_event={"event_id": "DAEMON_STOP", "timestamp": now}, 
                    snap=snap, summary="Daemon stopped unexpectedly", impact="PROCESSING_DELAY", root_cause="UNKNOWN"
                ))
                
        # Deduplicate
        for inc in detected_incidents:
            if inc.deterministic_identity in self.incidents:
                existing = self.incidents[inc.deterministic_identity]
                existing.occurrence_count += 1
                existing.last_seen_at = inc.detected_at
                
                # Reopen if closed
                if existing.status == IncidentStatus.CLOSED:
                    existing.status = IncidentStatus.REOPENED
            else:
                self.incidents[inc.deterministic_identity] = inc
                
        return list(self.incidents.values())

    def _create_incident(self, category: str, component: str, severity: str, symbol: str, session: str, 
                         trigger_event: Dict[str, Any], snap: ControlPlaneSnapshot, summary: str, impact: str, root_cause: str) -> Incident:
                             
        trigger_id = trigger_event.get("event_id", f"EVT_{datetime.now().timestamp()}")
        fingerprint = self._generate_fingerprint(category, component, symbol, session, trigger_id)
        now = datetime.now(timezone.utc).isoformat()
        
        evidence = IncidentEvidenceBundle(
            incident_id=f"INC_{fingerprint[:8]}",
            detection_timestamp=now,
            control_plane_snapshot_id=snap.snapshot_id,
            trigger_event=trigger_event,
            related_events=[],
            source_file=str(self.ledger_path),
            symbol=symbol,
            session=session
        )
        
        return Incident(
            incident_id=evidence.incident_id,
            deterministic_identity=fingerprint,
            detected_at=now,
            first_seen_at=now,
            last_seen_at=now,
            category=category,
            severity=severity,
            status=IncidentStatus.DETECTED,
            component=component,
            symbol=symbol,
            session_date=session,
            summary=summary,
            trigger_event_id=trigger_id,
            related_event_ids=[],
            source_refs=[str(self.ledger_path)],
            evidence_bundle=evidence,
            current_state="ACTIVE",
            root_cause=root_cause,
            impact=impact,
            recovery_plan="ESCALATE_TO_OPERATOR" if severity == IncidentSeverity.CRITICAL else "AUTO_RETRY",
            recovery_actions=[],
            verification_status="PENDING"
        )

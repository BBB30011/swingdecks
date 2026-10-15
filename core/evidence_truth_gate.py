import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
import duckdb
from core.truth_models import TruthGateSnapshot, TruthFinding
from core.control_plane import ControlPlaneAggregator
from core.incident_center import IncidentCenter
from core.semantic_truth_gate import SemanticTruthGate

class EvidenceTruthGate:
    def __init__(self, ledger_path: str = "state/audit/ledger.jsonl", daemon_path: str = "runtime/continuous_desk_daemon_state.json", graph_db_path: str = "data/duckdb/intelligence.duckdb"):
        self.ledger_path = Path(ledger_path)
        self.daemon_path = Path(daemon_path)
        
        target_path = Path(graph_db_path)
        if not target_path.exists() and Path("state/intelligence_graph.duckdb").exists():
            target_path = Path("state/intelligence_graph.duckdb")
        elif not target_path.exists() and Path("data/duckdb/intelligence.duckdb").exists():
            target_path = Path("data/duckdb/intelligence.duckdb")
            
        self.graph_db_path = target_path
        
        self.events: List[Dict[str, Any]] = []
        if self.ledger_path.exists():
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            self.events.append(json.loads(line))
                        except Exception:
                            pass
                        
        self.control_plane = ControlPlaneAggregator(str(self.ledger_path), str(self.daemon_path))
        self.incident_center = IncidentCenter(str(self.ledger_path), str(self.daemon_path))
        self.semantic_gate = SemanticTruthGate(str(self.graph_db_path))
        
    def _create_finding(self, category: str, severity: str, canonical_ref: str, observed: Any, expected: Any, root_cause: str, impact: str) -> TruthFinding:
        fp = hashlib.sha256(f"{category}{canonical_ref}{str(observed)}{str(expected)}".encode()).hexdigest()
        return TruthFinding(
            finding_id=f"TRUTH_{fp[:8]}",
            category=category,
            severity=severity,
            canonical_ref=canonical_ref,
            affected_systems=["ControlPlane", "IncidentCenter", "IntelligenceGraph", "SemanticWorldModel"],
            observed_value=observed,
            expected_value=expected,
            temporal_class="CURRENT",
            evidence_refs=[str(self.ledger_path)],
            root_cause=root_cause,
            root_cause_status="PROVEN",
            impact=impact,
            recommendation="Fix upstream parsing logic or enforce intelligence graph firewalls",
            status="OPEN"
        )

    def scan(self) -> TruthGateSnapshot:
        now = datetime.now(timezone.utc).isoformat()
        snap = TruthGateSnapshot(
            run_id="run_" + str(int(datetime.now(timezone.utc).timestamp())),
            generated_at=now
        )
        
        # 1. Identity & Integrity
        event_ids = set()
        for e in self.events:
            eid = e.get("event_id")
            if not eid:
                continue
            if eid in event_ids:
                snap.findings.append(self._create_finding(
                    "IDENTITY", "CRITICAL", eid, "DUPLICATE", "UNIQUE", "LEDGER_APPEND", "CORRUPTION"
                ))
            event_ids.add(eid)
            
        # 2. Accounting Integrity
        for e in self.events:
            if e.get("event_type") == "ACCOUNTING_RECORD":
                cash = e.get("metadata", {}).get("cash", 0.0)
                mkt = e.get("metadata", {}).get("market_value", 0.0)
                eq = e.get("metadata", {}).get("equity", 0.0)
                if abs((cash + mkt) - eq) > 0.01:
                    snap.findings.append(self._create_finding(
                        "ACCOUNTING", "CRITICAL", e.get("event_id"), eq, cash+mkt, "ACCOUNTING_ENGINE", "ACCOUNTING_MISMATCH"
                    ))
                    
        # 3. Incident Consistency
        incidents = self.incident_center.scan_for_incidents()
        for inc in incidents:
            evt = inc.evidence_bundle.trigger_event
            stage = evt.get("stage", "")
            if "DATA" in stage and inc.category == "AGENT":
                snap.findings.append(self._create_finding(
                    "SEMANTIC", "HIGH", inc.incident_id, "AGENT", "DATA", "INCIDENT_CENTER", "WRONG_ATTRIBUTION"
                ))
                
        # 4. PIT Integrity
        for e in self.events:
            if e.get("event_type") == "PIT_VIOLATION_ATTEMPT":
                snap.findings.append(self._create_finding(
                    "PIT", "CRITICAL", e.get("event_id"), "FUTURE_ACCESS", "PAST_ONLY", "AGENT", "PIT_BLOCKED"
                ))

        # 5. Semantic & World Model Graph Integrity
        if self.graph_db_path.exists():
            sem_snap = self.semantic_gate.audit_graph()
            for sf in sem_snap.findings:
                cat = "SEMANTIC"
                if "TEMPORAL" in sf.truth_layer:
                    cat = "PIT"
                elif "PROVENANCE" in sf.truth_layer:
                    cat = "PROVENANCE"
                elif "SECURITY" in sf.category or "MNPI" in sf.category or "PROMPT" in sf.category:
                    cat = "SECURITY"
                elif "WORLD_MODEL" in sf.truth_layer:
                    cat = "WORLD_MODEL"

                snap.findings.append(self._create_finding(
                    cat,
                    sf.severity,
                    sf.entity_or_rel_id,
                    sf.observed_value,
                    sf.expected_value,
                    sf.root_cause,
                    sf.impact
                ))
                
        if snap.findings:
            for f in snap.findings:
                if f.severity in ["CRITICAL", "HIGH"]:
                    snap.overall_status = "DEGRADED"
                    if f.category == "ACCOUNTING": snap.accounting_integrity = "FAIL"
                    if f.category == "IDENTITY": snap.identity_integrity = "FAIL"
                    if f.category in ["SEMANTIC", "WORLD_MODEL"]: snap.semantic_integrity = "FAIL"
                    if f.category in ["PIT", "SECURITY"]: snap.pit_integrity = "FAIL"
                
        return snap

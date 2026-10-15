from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class TruthFinding:
    finding_id: str
    category: str
    severity: str
    canonical_ref: str
    affected_systems: List[str]
    observed_value: Any
    expected_value: Any
    temporal_class: str
    evidence_refs: List[str]
    root_cause: str
    root_cause_status: str
    impact: str
    recommendation: str
    status: str

@dataclass
class TruthGateSnapshot:
    run_id: str
    generated_at: str
    source_integrity: str = "PASS"
    event_integrity: str = "PASS"
    temporal_integrity: str = "PASS"
    identity_integrity: str = "PASS"
    semantic_integrity: str = "PASS"
    state_integrity: str = "PASS"
    cross_system_integrity: str = "PASS"
    accounting_integrity: str = "PASS"
    pit_integrity: str = "PASS"
    agent_integrity: str = "PASS"
    decision_integrity: str = "PASS"
    incident_integrity: str = "PASS"
    replay_integrity: str = "PASS"
    thesis_integrity: str = "PASS"
    drift_integrity: str = "PASS"
    observability_integrity: str = "PASS"
    overall_status: str = "PASS"
    findings: List[TruthFinding] = field(default_factory=list)

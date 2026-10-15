import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from core.incident_center import Incident, IncidentStatus

class RecoveryEngine:
    def __init__(self):
        self.recovery_history = []

    def evaluate_safe_recovery(self, incident: Incident) -> str:
        # Determine if autonomous recovery is allowed
        if incident.severity == "CRITICAL" or incident.impact in ["PIT_BLOCKED", "ACCOUNTING_BLOCKED", "SECURITY_BLOCKED"]:
            return "ESCALATE_TO_OPERATOR"
            
        if incident.category == "DATA_FRESHNESS":
            return "WAIT_FOR_DATA"
            
        if incident.category == "AGENT":
            return "SAFE_RETRY"
            
        return "ESCALATE_TO_OPERATOR"

    def execute_recovery(self, incident: Incident) -> bool:
        incident.status = IncidentStatus.RECOVERING
        plan = self.evaluate_safe_recovery(incident)
        
        now = datetime.now(timezone.utc).isoformat()
        
        if plan == "ESCALATE_TO_OPERATOR":
            incident.recovery_actions.append({"action": plan, "timestamp": now, "status": "BLOCKED"})
            incident.status = IncidentStatus.TRIAGED
            return False
            
        if plan == "WAIT_FOR_DATA":
            incident.recovery_actions.append({"action": plan, "timestamp": now, "status": "WAITING"})
            incident.status = IncidentStatus.CONTAINED
            return False
            
        if plan == "SAFE_RETRY":
            # Mock idempotent safe retry execution
            incident.recovery_actions.append({
                "action": "SAFE_RETRY", 
                "timestamp": now, 
                "status": "SUCCESS", 
                "idempotency_key": f"RETRY_{incident.incident_id}"
            })
            incident.status = IncidentStatus.VERIFYING
            return self.verify_recovery(incident)
            
        return False

    def verify_recovery(self, incident: Incident) -> bool:
        # Check if condition cleared
        # In a real system, we'd rescan or verify state
        # For simulation, SAFE_RETRY succeeds
        now = datetime.now(timezone.utc).isoformat()
        
        if any(a["action"] == "SAFE_RETRY" and a["status"] == "SUCCESS" for a in incident.recovery_actions):
            incident.verification_status = "PASSED"
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = now
            return True
            
        incident.verification_status = "FAILED"
        incident.status = IncidentStatus.REOPENED
        return False
        
    def close_incident(self, incident: Incident, operator_reason: str = "") -> bool:
        if incident.status == IncidentStatus.RESOLVED or (operator_reason and incident.status in [IncidentStatus.TRIAGED, IncidentStatus.CONTAINED]):
            incident.status = IncidentStatus.CLOSED
            incident.closed_at = datetime.now(timezone.utc).isoformat()
            if operator_reason:
                incident.recovery_actions.append({"action": "OPERATOR_CLOSURE", "reason": operator_reason, "timestamp": incident.closed_at})
            return True
        return False

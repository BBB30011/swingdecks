import uuid
from datetime import datetime, timezone
import json
from pathlib import Path
from core.schemas import AlertMessage, SignalState, AlertPriority, DecisionResult

class AlertEngine:
    def __init__(self, output_dir: str = "reports/alerts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.alerts_file = self.output_dir / "all_alerts.json"

    def _save_alert(self, alert: AlertMessage):
        data = {"alerts": []}
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # Deduplication check
        dedup_key = f"{alert.symbol}_{alert.alert_type}_{alert.state.value}_{alert.trigger}"
        # We only check recent alerts to allow re-alerting if state cycled back
        is_duplicate = False
        for existing in reversed(data["alerts"][-20:]): # check last 20 alerts
            if existing.get("symbol") == alert.symbol:
                existing_key = f"{existing.get('symbol')}_{existing.get('alert_type')}_{existing.get('state')}_{existing.get('trigger', 'N/A')}"
                if dedup_key == existing_key:
                    # If we already have this exact alert recently, it's a duplicate
                    # UNLESS priority escalated (e.g. from HIGH to CRITICAL)
                    existing_priority = existing.get("priority", "LOW")
                    # simple priority comparison isn't strict string compare, we'd need ordinal, but for now exact match blocks
                    if existing_priority == alert.priority.value:
                        is_duplicate = True
                break # Only compare with the most recent alert for this symbol

        if is_duplicate:
            return # Skip saving and alerting
            
        data["alerts"].append(alert.model_dump())
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
        print(f"\n[ALERT] {alert.priority.value} | {alert.symbol} | {alert.state.value} | {alert.alert_type}")
        print(f"Reason: {alert.reason}")
        if alert.state in [SignalState.ENTRY_READY, SignalState.ENTRY_CONFIRMED]:
            print(f"Zone: {alert.entry_zone} | Stop: {alert.stop_loss} | Target: {alert.target_price} | R/R: {alert.rr_ratio:.2f}")

    def generate_fast_alert(self, quant_res: dict, current_state: SignalState) -> AlertMessage:
        symbol = quant_res["symbol"]
        score = quant_res.get("quant_score", 0)
        
        state = SignalState.EARLY_WATCH
        priority = AlertPriority.LOW
        
        if score >= 80:
            priority = AlertPriority.MEDIUM
            state = SignalState.WATCH
            
        alert = AlertMessage(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=symbol,
            alert_type="FAST_ALERT",
            priority=priority,
            state=state,
            opportunity_score=score,
            evidence_quality=quant_res.get("candidate_quality", "UNKNOWN"),
            reason="Candidate detected by fast quantitative path. Not yet an actionable entry recommendation. WAIT for deep validation."
        )
        self._save_alert(alert)
        return alert

    def generate_deep_alert(self, decision: DecisionResult, current_state: SignalState) -> AlertMessage:
        state = current_state
        priority = AlertPriority.INFO
        
        # Helper variables
        current_price = decision.current_price
        trigger_price = decision.trigger.trigger_price if decision.trigger else decision.trigger_price
        
        if decision.action == "BUY":
            # ENTRY_READY minimum requirements: Risk must be GREEN, RR >= 1.5, Evidence >= PARTIAL
            valid_rr = decision.risk_reward_ratio >= 1.5
            valid_risk = decision.risk_state == "GREEN"
            valid_evidence = decision.evidence_state not in ["INSUFFICIENT", "WEAK", "UNKNOWN"]
            valid_contradictions = len(decision.evidence_matrix.contradictions) == 0 if hasattr(decision, 'evidence_matrix') else True

            if valid_rr and valid_risk and valid_evidence and valid_contradictions:
                if current_state == SignalState.ENTRY_READY:
                    # Point-in-time Trigger Confirmation Logic
                    if current_price > 0 and trigger_price > 0 and current_price >= trigger_price:
                        state = SignalState.ENTRY_CONFIRMED
                        priority = AlertPriority.HIGH
                        decision.reason += f" (Trigger confirmed at {current_price})"
                    else:
                        state = SignalState.ENTRY_READY
                        priority = AlertPriority.HIGH
                else:
                    state = SignalState.ENTRY_READY
                    priority = AlertPriority.HIGH
            else:
                state = SignalState.SETUP_FORMING
                priority = AlertPriority.MEDIUM
                decision.reason += " (Downgraded from BUY due to risk/evidence/contradiction gates)"
                
        elif decision.action == "WAIT":
            if current_state in [SignalState.ENTRY_CONFIRMED, SignalState.HOLD]:
                if decision.thesis.thesis_deteriorating:
                    state = SignalState.EXIT_WARNING
                    priority = AlertPriority.HIGH
                    decision.reason += " (Thesis deteriorating while holding)"
                else:
                    # HOLD + WAIT with no deterioration should remain HOLD
                    state = SignalState.HOLD
                    priority = AlertPriority.INFO
            else:
                state = SignalState.SETUP_FORMING
                priority = AlertPriority.MEDIUM
                
        elif decision.action == "SELL":
            state = SignalState.EXIT_NOW
            priority = AlertPriority.CRITICAL
            
        elif decision.action == "AVOID":
            state = SignalState.INVALIDATED
            priority = AlertPriority.INFO
            
        opp_score = decision.opportunity_assessment.opportunity_score if decision.opportunity_assessment else decision.confidence
        bull_case = decision.thesis.bull_thesis
        
        # Check for Expiration of ENTRY_READY
        window_status = decision.opportunity_assessment.entry_window_status if decision.opportunity_assessment else "UNKNOWN"
        is_expired_window = window_status in ["CLOSED", "MISSED"]
        if current_state == SignalState.ENTRY_READY:
            if (decision.action in ["WAIT", "AVOID"] and decision.thesis.thesis_deteriorating) or is_expired_window:
                 state = SignalState.INVALIDATED
                 priority = AlertPriority.INFO
                 decision.reason += " (Setup invalidated or expired)"

        alert = AlertMessage(
            alert_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol=decision.symbol,
            alert_type="DEEP_ALERT",
            priority=priority,
            state=state,
            entry_zone=f"{decision.entry_price * 0.99:.2f} - {decision.entry_price * 1.01:.2f}",
            stop_loss=decision.stop_loss,
            target_price=decision.target_price,
            rr_ratio=decision.risk_reward_ratio,
            opportunity_score=opp_score,
            evidence_quality=decision.evidence_state,
            bull_case=bull_case,
            bear_case=decision.thesis.bear_thesis,
            catalysts=decision.thesis.key_catalysts,
            risks=decision.thesis.key_risks,
            reason=decision.reason
        )
        self._save_alert(alert)
        return alert

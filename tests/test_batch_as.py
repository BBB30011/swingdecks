from core.schemas import SignalState, AlertPriority, AlertMessage
from core.decision import InvestmentThesis, OpportunityAssessment, DecisionResult
from core.signal_state_tracker import SignalStateTracker
from core.alert_engine import AlertEngine
import json
from pathlib import Path

# --- STATE MACHINE TESTS ---

def test_valid_transitions(tmp_path):
    tracker = SignalStateTracker(state_file=str(tmp_path / "signal_states.json"))
    tracker.attempt_transition("AAPL", SignalState.SETUP_FORMING)
    assert tracker.attempt_transition("AAPL", SignalState.ENTRY_READY) == SignalState.ENTRY_READY
    assert tracker.attempt_transition("AAPL", SignalState.ENTRY_CONFIRMED, current_price=100, trigger_price=105) == SignalState.ENTRY_READY
    assert tracker.attempt_transition("AAPL", SignalState.ENTRY_CONFIRMED, current_price=106, trigger_price=105) == SignalState.ENTRY_CONFIRMED

def test_invalid_regression_blocked(tmp_path):
    tracker = SignalStateTracker(state_file=str(tmp_path / "signal_states.json"))
    tracker.states["MSFT"] = SignalState.ENTRY_READY.value
    assert tracker.attempt_transition("MSFT", SignalState.EARLY_WATCH) == SignalState.ENTRY_READY

def test_invalidation_reset(tmp_path):
    tracker = SignalStateTracker(state_file=str(tmp_path / "signal_states.json"))
    tracker.states["TSLA"] = SignalState.ENTRY_READY.value
    assert tracker.attempt_transition("TSLA", SignalState.INVALIDATED) == SignalState.INVALIDATED

# --- ALERT ENGINE TESTS ---

def test_alert_deduplication(tmp_path):
    output_dir = tmp_path / "alerts"
    engine = AlertEngine(output_dir=str(output_dir))
    
    alert1 = AlertMessage(
        alert_id="1", timestamp="T1", symbol="BBCA", alert_type="DEEP_ALERT",
        priority=AlertPriority.HIGH, state=SignalState.ENTRY_READY,
        trigger="1000", opportunity_score=85
    )
    alert2 = AlertMessage(
        alert_id="2", timestamp="T2", symbol="BBCA", alert_type="DEEP_ALERT",
        priority=AlertPriority.HIGH, state=SignalState.ENTRY_READY,
        trigger="1000", opportunity_score=86
    )
    
    engine._save_alert(alert1)
    engine._save_alert(alert2)
    
    with open(engine.alerts_file, 'r') as f:
        data = json.load(f)
    assert len(data["alerts"]) == 1
    
    alert3 = AlertMessage(
        alert_id="3", timestamp="T3", symbol="BBCA", alert_type="DEEP_ALERT",
        priority=AlertPriority.CRITICAL, state=SignalState.ENTRY_CONFIRMED,
        trigger="1000", opportunity_score=86
    )
    engine._save_alert(alert3)
    
    with open(engine.alerts_file, 'r') as f:
        data = json.load(f)
    assert len(data["alerts"]) == 2

def test_entry_ready_expiration(tmp_path):
    output_dir = tmp_path / "alerts"
    engine = AlertEngine(output_dir=str(output_dir))
    
    opp = OpportunityAssessment(
        symbol="BBRI",
        entry_window_status="MISSED"
    )
    dec = DecisionResult(
        job_id="x", symbol="BBRI", as_of_timestamp="T", action="WAIT",
        risk_state="GREEN", confidence=80, reason="", blockers=[],
        decision_timestamp="2026-09-10T12:00:00Z", decision_source="TEST",
        opportunity_assessment=opp,
        thesis=InvestmentThesis(thesis_deteriorating=False)
    )
    
    alert = engine.generate_deep_alert(dec, SignalState.ENTRY_READY)
    assert alert.state == SignalState.INVALIDATED
    assert "expired" in alert.reason

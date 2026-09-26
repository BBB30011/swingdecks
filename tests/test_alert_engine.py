import pytest
from core.alert_engine import AlertEngine
from core.signal_state_tracker import SignalStateTracker
from core.schemas import SignalState, AlertPriority
from core.decision import InvestmentThesis, DecisionResult

def test_fast_alert_generation(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    quant_res = {
        "symbol": "BBCA",
        "quant_score": 85,
        "candidate_quality": "HIGH"
    }
    
    # Below 80 should be EARLY_WATCH
    quant_res["quant_score"] = 75
    alert = engine.generate_fast_alert(quant_res, SignalState.WATCH)
    assert alert.state == SignalState.EARLY_WATCH
    assert alert.priority == AlertPriority.LOW
    
    # 80+ should be WATCH
    quant_res["quant_score"] = 85
    alert = engine.generate_fast_alert(quant_res, SignalState.EARLY_WATCH)
    assert alert.state == SignalState.WATCH
    assert alert.priority == AlertPriority.MEDIUM

def test_deep_alert_generation(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    decision = DecisionResult(
        job_id="1", symbol="BBCA", as_of_timestamp="2020",
        action="BUY", risk_state="GREEN", confidence=90, opportunity_score=85,
        thesis=InvestmentThesis(bull_thesis="Strong"),
        reason="Good",
        entry_price=1000, stop_loss=900, target_price=1200, risk_reward_ratio=2.0,
        evidence_state="GOOD",
        decision_timestamp="2020"
    )
    
    # BUY + GREEN = ENTRY_READY
    alert = engine.generate_deep_alert(decision, SignalState.WATCH)
    assert alert.state == SignalState.ENTRY_READY
    assert alert.priority == AlertPriority.HIGH
    assert alert.alert_type == "DEEP_ALERT"
    
    # SELL = EXIT_NOW
    decision.action = "SELL"
    alert = engine.generate_deep_alert(decision, SignalState.HOLD)
    assert alert.state == SignalState.EXIT_NOW
    assert alert.priority == AlertPriority.CRITICAL

def test_signal_state_tracker(tmp_path):
    state_file = tmp_path / "states.json"
    tracker = SignalStateTracker(state_file=str(state_file))
    
    # Default is WATCH
    assert tracker.get_state("UNTRACKED") == SignalState.WATCH
    
    # Transition
    tracker.transition_state("GOTO", SignalState.SETUP_FORMING)
    assert tracker.get_state("GOTO") == SignalState.SETUP_FORMING
    
    # Persistence
    tracker2 = SignalStateTracker(state_file=str(state_file))
    assert tracker2.get_state("GOTO") == SignalState.SETUP_FORMING

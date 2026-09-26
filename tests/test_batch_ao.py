import pytest
from core.alert_engine import AlertEngine
from core.schemas import SignalState, AlertPriority
from core.decision import DecisionResult, InvestmentThesis, EvidenceMatrix, EvidenceFactor, FactorState, FactorImpact, EvidenceContradiction, ContradictionSeverity
from agents.agent3_committee.committee import InvestmentCommittee

def build_mock_decision(action="BUY", risk_state="GREEN", rr=2.0, state=SignalState.WATCH, entry_price=1000.0, current_price=1000.0, trigger_price=1000.0, contradictions=None):
    if contradictions is None:
        contradictions = []
    
    ev_matrix = EvidenceMatrix(contradictions=contradictions)
    
    return DecisionResult(
        job_id="test",
        symbol="TEST",
        as_of_timestamp="2020",
        action=action,
        risk_state=risk_state,
        confidence=90.0,
        thesis=InvestmentThesis(),
        evidence_matrix=ev_matrix,
        reason="Test",
        current_price=current_price,
        entry_price=entry_price, # Let's assume entry_price here acts as current_price in our simplistic model
        trigger_price=trigger_price,
        stop_loss=900.0,
        target_price=entry_price + (entry_price - 900.0) * rr, # to match rr
        risk_reward_ratio=rr,
        evidence_state="GOOD",
        decision_timestamp="2020"
    )

def test_entry_ready_gates(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    
    # 1. Valid BUY -> ENTRY_READY
    decision = build_mock_decision(action="BUY", risk_state="GREEN", rr=2.0)
    alert = engine.generate_deep_alert(decision, SignalState.WATCH)
    assert alert.state == SignalState.ENTRY_READY
    assert alert.priority == AlertPriority.HIGH
    
    # 2. Invalid RR -> SETUP_FORMING
    decision = build_mock_decision(action="BUY", risk_state="GREEN", rr=1.2)
    alert = engine.generate_deep_alert(decision, SignalState.WATCH)
    assert alert.state == SignalState.SETUP_FORMING
    assert alert.priority == AlertPriority.MEDIUM
    assert "Downgraded" in alert.reason
    
    # 3. Invalid Risk -> SETUP_FORMING
    decision = build_mock_decision(action="BUY", risk_state="YELLOW", rr=2.0)
    alert = engine.generate_deep_alert(decision, SignalState.WATCH)
    assert alert.state == SignalState.SETUP_FORMING
    assert alert.priority == AlertPriority.MEDIUM
    assert "Downgraded" in alert.reason
    
    # 4. Valid Contradiction -> SETUP_FORMING
    decision = build_mock_decision(action="BUY", risk_state="GREEN", rr=2.0, contradictions=[EvidenceContradiction(topic="Test", description="Conflict!", severity=ContradictionSeverity.CRITICAL)])
    alert = engine.generate_deep_alert(decision, SignalState.WATCH)
    assert alert.state == SignalState.SETUP_FORMING
    assert alert.priority == AlertPriority.MEDIUM
    assert "Downgraded" in alert.reason

def test_entry_confirmed_trigger(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    
    # If previously ENTRY_READY and still BUY, it triggers ENTRY_CONFIRMED
    decision = build_mock_decision(action="BUY", risk_state="GREEN", rr=2.0)
    alert = engine.generate_deep_alert(decision, SignalState.ENTRY_READY)
    assert alert.state == SignalState.ENTRY_CONFIRMED
    assert alert.priority == AlertPriority.HIGH

def test_evidence_matrix_contradiction():
    committee = InvestmentCommittee()
    quant_data = {"quant_score": 85, "entry_price": 1000, "stop_loss": 900, "target_price": 1200}
    research_data = {"flow_state": "NEGATIVE"}
    risk_evaluation = {"action": "BUY", "risk_state": "GREEN", "blockers": [], "risk_per_share": 100, "reward_per_share": 200, "risk_reward_ratio": 2.0, "position_size": 100, "position_lots": 1, "position_value": 100000, "portfolio_risk": 0.01, "trace": {}}
    
    decision = committee.synthesize("job_1", "BBCA", "2020", quant_data, research_data, risk_evaluation)
    
    # Should be downgraded to WAIT due to Technical vs Flow contradiction
    assert decision.action == "WAIT"
    assert any(c.description == "Technical breakout lacks flow confirmation." for c in decision.evidence_matrix.contradictions)
    assert decision.evidence_matrix.factors["technical"].state == FactorState.POSITIVE
    assert decision.evidence_matrix.factors["flow"].state == FactorState.NEGATIVE

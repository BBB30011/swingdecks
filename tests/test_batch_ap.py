import pytest
from core.alert_engine import AlertEngine
from core.schemas import SignalState, AlertPriority
from core.decision import DecisionResult, InvestmentThesis, EvidenceMatrix, EvidenceFactor, FactorState, FactorImpact, EvidenceContradiction, ContradictionSeverity
from agents.agent3_committee.committee import InvestmentCommittee

def build_mock_decision(action="BUY", risk_state="GREEN", rr=2.0, state=SignalState.WATCH, entry_price=1000.0, current_price=1000.0, trigger_price=1000.0, contradictions=None, thesis_deteriorating=False):
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
        thesis=InvestmentThesis(thesis_deteriorating=thesis_deteriorating),
        evidence_matrix=ev_matrix,
        reason="Test",
        current_price=current_price,
        entry_price=entry_price,
        trigger_price=trigger_price,
        stop_loss=900.0,
        target_price=entry_price + (entry_price - 900.0) * rr, # to match rr
        risk_reward_ratio=rr,
        evidence_state="GOOD",
        decision_timestamp="2020"
    )

def test_false_confirmation_prevention(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    
    # 1. current_price < trigger_price -> remains ENTRY_READY
    decision = build_mock_decision(action="BUY", current_price=950, trigger_price=1000)
    alert = engine.generate_deep_alert(decision, SignalState.ENTRY_READY)
    assert alert.state == SignalState.ENTRY_READY
    
    # 2. current_price >= trigger_price -> ENTRY_CONFIRMED
    decision2 = build_mock_decision(action="BUY", current_price=1010, trigger_price=1000)
    alert2 = engine.generate_deep_alert(decision2, SignalState.ENTRY_READY)
    assert alert2.state == SignalState.ENTRY_CONFIRMED

def test_hold_wait_no_deterioration(tmp_path):
    engine = AlertEngine(output_dir=str(tmp_path))
    
    # 1. HOLD + WAIT with no deterioration -> stays HOLD
    decision = build_mock_decision(action="WAIT", thesis_deteriorating=False)
    alert = engine.generate_deep_alert(decision, SignalState.HOLD)
    assert alert.state == SignalState.HOLD
    assert alert.priority == AlertPriority.INFO
    
    # 2. HOLD + WAIT WITH deterioration -> EXIT_WARNING
    decision2 = build_mock_decision(action="WAIT", thesis_deteriorating=True)
    alert2 = engine.generate_deep_alert(decision2, SignalState.HOLD)
    assert alert2.state == SignalState.EXIT_WARNING
    assert alert2.priority == AlertPriority.HIGH

def test_minor_contradiction_allowed():
    committee = InvestmentCommittee()
    quant_data = {"quant_score": 85, "entry_price": 1000, "stop_loss": 900, "target_price": 1200}
    research_data = {
        "flow_state": "POSITIVE", # no technical vs flow conflict
        "contradictions": [
            {
                "topic": "Minor concern",
                "description": "Sector slightly weak",
                "severity": "LOW"
            }
        ]
    }
    risk_evaluation = {"action": "BUY", "risk_state": "GREEN", "blockers": [], "risk_per_share": 100, "reward_per_share": 200, "risk_reward_ratio": 2.0, "position_size": 100, "position_lots": 1, "position_value": 100000, "portfolio_risk": 0.01, "trace": {}}
    
    decision = committee.synthesize("job_1", "BBCA", "2020", quant_data, research_data, risk_evaluation)
    
    # Minor contradiction should NOT downgrade a BUY
    assert decision.action == "BUY"
    assert any(c.severity == ContradictionSeverity.LOW for c in decision.evidence_matrix.contradictions)

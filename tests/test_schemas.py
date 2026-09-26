import pytest
from pydantic import ValidationError
from core.schemas import JobRequest, QuantResult, RedTeamResult, DecisionResult
from core.validator import validate_model

def test_job_request_valid():
    # Test 1: JobRequest valid dapat dibuat
    req = JobRequest(job_id="JOB-123", symbol="BBCA", created_at="2026-09-08T10:00:00Z")
    assert validate_model(req) is True
    assert req.status == "CREATED"

def test_quant_result_valid_score():
    # Test 2: QuantResult dengan score 82 valid
    res = QuantResult(job_id="JOB-123", symbol="BBCA", quant_score=82, market_regime="BULL", data_quality="GOOD")
    assert validate_model(res) is True

def test_quant_result_invalid_score():
    # Test 3: QuantResult dengan score 150 ditolak
    with pytest.raises(ValidationError):
        QuantResult(job_id="JOB-123", symbol="BBCA", quant_score=150, market_regime="BULL", data_quality="GOOD")

def test_red_team_result_valid_decision():
    # Test 4: RedTeamResult dengan PASS valid
    res = RedTeamResult(
        job_id="JOB-123", symbol="BBCA",
        bull_case="...", bear_case="...",
        contradictions=[], unknowns=[],
        decision="PASS"
    )
    assert validate_model(res) is True

def test_red_team_result_invalid_decision():
    # Test 5: RedTeamResult dengan BUY ditolak
    with pytest.raises(ValidationError):
        RedTeamResult(
            job_id="JOB-123", symbol="BBCA",
            bull_case="...", bear_case="...",
            contradictions=[], unknowns=[],
            decision="BUY"
        )

def test_decision_result_valid():
    # Test 6: DecisionResult dengan BUY, GREEN, 82 valid
    res = DecisionResult(
        job_id="JOB-123", symbol="BBCA",
        action="BUY", risk_state="GREEN",
        confidence=82, reason="Looking good"
    )
    assert validate_model(res) is True

def test_decision_result_invalid_confidence():
    # Test 7: DecisionResult dengan confidence 150 ditolak
    with pytest.raises(ValidationError):
        DecisionResult(
            job_id="JOB-123", symbol="BBCA",
            action="BUY", risk_state="GREEN",
            confidence=150, reason="Looking good"
        )

def test_decision_result_invalid_action():
    # Test 8: DecisionResult dengan action yang tidak diperbolehkan ditolak
    with pytest.raises(ValidationError):
        DecisionResult(
            job_id="JOB-123", symbol="BBCA",
            action="JUMP", risk_state="GREEN",
            confidence=82, reason="Looking good"
        )

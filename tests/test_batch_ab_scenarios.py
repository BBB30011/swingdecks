import pytest
from agents.agent3_committee.pipeline import Agent3DecisionPipeline
from core.decision import PortfolioContext

@pytest.fixture
def base_portfolio():
    return PortfolioContext(
        capital=100000000,
        available_cash=100000000,
        current_positions=[],
        total_exposure=0.0,
        total_risk=0.0,
        number_of_positions=0,
        as_of_timestamp="2020-01-01"
    )

def test_synthetic_scenario_1(base_portfolio):
    # STRONG BULL, Research GOOD, Red Team PASS, RR 3.0, Confidence 90, Portfolio risk OK
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95}, # Risk=100, Reward=300 -> RR=3.0
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "BUY"
    assert res["risk_state"] == "GREEN"

def test_synthetic_scenario_2(base_portfolio):
    # STRONG BULL, Research GOOD, Red Team BLOCK, Major contradiction HIGH
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95},
        "research_context": {"completeness": "GOOD", "red_team_decision": "BLOCK", "confidence": 90, "contradictions": [{"severity": "HIGH"}]}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "AVOID"
    assert res["risk_state"] == "RED"

def test_synthetic_scenario_3(base_portfolio):
    # STRONG BULL, Research INSUFFICIENT
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95},
        "research_context": {"completeness": "INSUFFICIENT", "red_team_decision": "BLOCK", "confidence": 0}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "WAIT"
    assert res["risk_state"] == "RED"

def test_synthetic_scenario_4(base_portfolio):
    # STRONG BULL, Research GOOD, RR 1.4
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1140, "quant_score": 95}, # Risk=100, Reward=140 -> RR=1.4
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "WAIT"
    assert res["risk_state"] == "RED"

def test_synthetic_scenario_5(base_portfolio):
    # STRONG BULL, Research GOOD, RR 3.0, Portfolio risk > 2%
    base_portfolio.total_risk = 0.019 # existing risk
    # This trade adds 0.5% risk -> total 2.4% > 2% limit
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95},
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "WAIT"
    assert res["risk_state"] == "RED"

def test_synthetic_scenario_6(base_portfolio):
    # Existing position, Thesis intact, Risk GREEN
    base_portfolio.current_positions = ["BBCA_SYNTHETIC_FIXTURE"]
    pipeline = Agent3DecisionPipeline()
    payload = {
        "job_id": "1", "symbol": "BBCA_SYNTHETIC_FIXTURE",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95},
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    res = pipeline.process_job(payload, base_portfolio)["decision"]
    assert res["action"] == "HOLD"
    assert res["risk_state"] == "GREEN"

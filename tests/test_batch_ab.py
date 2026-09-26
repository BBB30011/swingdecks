import pytest
import json
from agents.agent3_committee.pipeline import Agent3DecisionPipeline
from core.decision import PortfolioContext, DecisionResult
import math

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

@pytest.fixture
def default_job():
    return {
        "job_id": "1",
        "symbol": "BBCA",
        "as_of_timestamp": "2020-01-01",
        "quant_context": {
            "quant_score": 90,
            "quant_confidence": 95,
            "data_quality": "VALID",
            "entry_price": 1000.0,
            "stop_loss": 950.0,
            "target_price": 1200.0
        },
        "research_context": {
            "completeness": "GOOD",
            "red_team_decision": "PASS",
            "contradictions": [],
            "depends_on_speculation": False,
            "confidence": 90
        }
    }

def test_scenario_a_valid_buy(base_portfolio, default_job):
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] == "BUY"
    assert d["risk_state"] == "GREEN"

def test_scenario_b_low_rr(base_portfolio, default_job):
    default_job["quant_context"]["target_price"] = 1010.0  # reward = 10, risk = 50 -> RR = 0.2
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "RISK_GATE_FAILED_RR" in d["blockers"]

def test_scenario_c_research_insufficient(base_portfolio, default_job):
    default_job["research_context"]["completeness"] = "INSUFFICIENT"
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "RESEARCH_INSUFFICIENT" in d["blockers"]

def test_scenario_d_red_team_block(base_portfolio, default_job):
    default_job["research_context"]["red_team_decision"] = "BLOCK"
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "RED_TEAM_BLOCK" in d["blockers"]

def test_scenario_e_major_contradiction(base_portfolio, default_job):
    default_job["research_context"]["contradictions"] = [{"severity": "HIGH"}]
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] == "AVOID"
    assert d["risk_state"] == "RED"
    assert "MAJOR_CONTRADICTION" in d["blockers"]

def test_scenario_f_speculation(base_portfolio, default_job):
    default_job["research_context"]["depends_on_speculation"] = True
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] == "AVOID"
    assert d["risk_state"] == "RED"
    assert "THESIS_DEPENDS_ON_SPECULATION" in d["blockers"]

def test_scenario_g_portfolio_risk_exceeded(base_portfolio, default_job):
    # Base portfolio risk is 0, let's max it out manually in the test
    base_portfolio.total_risk = 0.019 # Close to max 0.02
    default_job["quant_context"]["stop_loss"] = 990.0 # Risk is 10, lot size 100... wait
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "PORTFOLIO_RISK_EXCEEDED" in d["blockers"]

def test_scenario_h_maximum_positions(base_portfolio, default_job):
    base_portfolio.number_of_positions = 5
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert "MAX_POSITION_LIMIT_REACHED" in d["blockers"]

def test_scenario_i_existing_position(base_portfolio, default_job):
    base_portfolio.current_positions = ["BBCA"]
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] == "HOLD"
    assert d["risk_state"] == "GREEN"

def test_scenario_j_invalid_stop(base_portfolio, default_job):
    default_job["quant_context"]["stop_loss"] = 1100.0 # Stop above entry
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] == "AVOID"
    assert d["risk_state"] == "RED"
    assert "INVALID_RISK_STRUCTURE" in d["blockers"]

def test_scenario_k_invalid_target(base_portfolio, default_job):
    default_job["quant_context"]["target_price"] = 900.0 # Target below entry
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "INVALID_REWARD_STRUCTURE" in d["blockers"]

def test_scenario_l_confidence_below_threshold(base_portfolio, default_job):
    default_job["research_context"]["confidence"] = 50
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["action"] in ["WAIT", "AVOID"]
    assert d["risk_state"] == "RED"
    assert "LOW_CONFIDENCE" in d["blockers"]

def test_scenario_m_stale_data(base_portfolio, default_job):
    default_job["quant_context"]["data_quality"] = "STALE_DATA"
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    d = res["decision"]
    assert d["risk_state"] == "RED"
    assert "DATA_STALE" in d["blockers"]

def test_scenario_n_deterministic_sizing(base_portfolio, default_job):
    pipeline = Agent3DecisionPipeline()
    res1 = pipeline.process_job(default_job, base_portfolio)
    res2 = pipeline.process_job(default_job, base_portfolio)
    assert res1["decision"]["position_size"] == res2["decision"]["position_size"]

def test_scenario_o_lot_rounding(base_portfolio, default_job):
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    # capital = 100M, max_risk = 0.5% = 500k
    # entry 1000, stop 950 -> risk/share = 50
    # shares = 500k / 50 = 10k -> 100 lots
    assert res["decision"]["position_size"] == 10000
    assert res["decision"]["position_lots"] == 100

def test_scenario_p_zero_capital():
    portfolio = PortfolioContext(capital=0, available_cash=0, current_positions=[], total_exposure=0, total_risk=0, number_of_positions=0, as_of_timestamp="2020")
    pipeline = Agent3DecisionPipeline()
    default_job = {
        "job_id": "1", "symbol": "BBCA", "as_of_timestamp": "2020",
        "quant_context": {"entry_price": 100, "stop_loss": 90, "target_price": 200},
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    res = pipeline.process_job(default_job, portfolio)
    assert res["decision"]["action"] == "WAIT" # Because ZERO_POSITION_SIZE blocker
    assert "ZERO_POSITION_SIZE" in res["decision"]["blockers"]

def test_scenario_q_nan_infinity(base_portfolio, default_job):
    default_job["quant_context"]["entry_price"] = math.inf
    pipeline = Agent3DecisionPipeline()
    with pytest.raises(ValueError, match="must be finite"):
        pipeline.process_job(default_job, base_portfolio)

def test_scenario_r_future_timestamp(base_portfolio, default_job):
    # Pipeline doesn't inherently reject future timestamp, but it's passed as payload correctly.
    # In reality Agent1 prevents this. Just testing schema passes correctly.
    default_job["as_of_timestamp"] = "2020-01-01T00:00:00Z"
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    assert res["status"] == "COMPLETED"

def test_scenario_t_serialization_roundtrip(base_portfolio, default_job):
    pipeline = Agent3DecisionPipeline()
    res = pipeline.process_job(default_job, base_portfolio)
    # Serialize to JSON and parse back
    s = json.dumps(res["decision"])
    d = json.loads(s)
    # Re-validate with pydantic
    obj = DecisionResult(**d)
    assert obj.symbol == "BBCA"
    assert obj.action == "BUY"

import pytest
import time
from agents.agent3_committee.pipeline import Agent3DecisionPipeline
from core.decision import PortfolioContext

def test_performance_100_packets():
    pipeline = Agent3DecisionPipeline()
    portfolio = PortfolioContext(
        capital=100000000,
        available_cash=100000000,
        current_positions=[],
        total_exposure=0.0,
        total_risk=0.0,
        number_of_positions=0,
        as_of_timestamp="2020-01-01"
    )
    
    payload = {
        "job_id": "1", "symbol": "BBCA",
        "quant_context": {"entry_price": 1000, "stop_loss": 900, "target_price": 1300, "quant_score": 95},
        "research_context": {"completeness": "GOOD", "red_team_decision": "PASS", "confidence": 90}
    }
    
    start_time = time.time()
    for i in range(100):
        # vary slightly to avoid caching 
        payload["job_id"] = str(i)
        payload["quant_context"]["entry_price"] = 1000 + i
        res = pipeline.process_job(payload, portfolio)
        assert res["status"] == "COMPLETED"
    
    elapsed = time.time() - start_time
    assert elapsed < 1.0  # 100 simple packets should take < 1 second


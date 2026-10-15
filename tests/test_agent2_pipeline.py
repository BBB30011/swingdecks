import pytest
import json
from agents.agent2_intelligence.pipeline import MockEvidenceCollector, Agent2IntelligencePipeline
from core.research import ResearchPacket, ResearchCompletenessEngine
from core.research_contradiction import ContradictionEngine

def test_agent1_to_agent2_payload():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    payload = {
        "job_id": "123",
        "symbol": "BBCA",
        "quant_score": 90,
        "quant_confidence": 95,
        "market_regime": "BULL",
        "stock_regime": "BULL",
        "as_of_timestamp": "2020-01-02"
    }
    res = pipeline.process_job(payload)
    assert res["status"] == "COMPLETED"
    assert res["packet"]["symbol"] == "BBCA"
    assert res["packet"]["quant_context"]["quant_score"] == 90

def test_point_in_time_filtering_future_invariance():
    collector = MockEvidenceCollector("BULLISH")
    pipeline = Agent2IntelligencePipeline(collector)
    
    # Dataset A (as_of = 2019-12-31, before evidence published in 2020)
    res_A = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2019-12-31"})
    
    # Dataset B (as_of = 2020-01-02, after evidence published)
    res_B = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2020-01-02"})
    
    # In Dataset A, the fundamental evidence should be filtered out!
    assert len(res_A["packet"]["fundamental"]) == 0
    # In Dataset B, it should be present
    assert len(res_B["packet"]["fundamental"]) == 1

def test_determinism():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    res1 = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2020-01-02"})
    res2 = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2020-01-02"})
    assert json.dumps(res1) == json.dumps(res2)

def test_no_secret_leakage():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    res = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2020-01-02"})
    s = json.dumps(res)
    assert "API_KEY" not in s
    assert "PASSWORD" not in s

def test_packet_serialization():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    res = pipeline.process_job({"symbol": "BBCA", "as_of_timestamp": "2020-01-02"})
    # Check that it can be dumped to JSON without errors
    assert isinstance(json.dumps(res["packet"]), str)

def test_completeness_categories():
    packet = ResearchPacket(job_id="1", symbol="BBCA", as_of_timestamp="2020", quant_context={})
    assert ResearchCompletenessEngine.evaluate(packet) == "INSUFFICIENT"
    packet.fundamental.append(None)
    assert ResearchCompletenessEngine.evaluate(packet) == "WEAK"

def test_contradiction_severity():
    packet = ResearchPacket(job_id="1", symbol="BBCA", as_of_timestamp="2020", quant_context={"quant_score": 90})
    from core.research import FundamentalEvidence, MacroEvidence
    packet.fundamental.append(FundamentalEvidence(
        evidence_id="1", symbol="BBCA", category="FUNDAMENTAL", claim="Bad", claim_class="FACT", source="Filing", as_of_timestamp="2020", metric="rev", direction="NEGATIVE"
    ))
    packet.macro.append(MacroEvidence(
        evidence_id="1", symbol="BBCA", category="MACRO", claim="Bad", claim_class="FACT", source="Gov", as_of_timestamp="2020", indicator="r", value=1.0, unit="%", direction="NEGATIVE", interpretation="bad", timestamp="2020"
    ))
    c = ContradictionEngine.detect(packet)
    assert len(c) == 1
    assert c[0]["severity"] == "HIGH"

def test_synthetic_scenario_bullish():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("BULLISH"))
    res = pipeline.process_job({"symbol": "BBCA_SYNTHETIC_FIXTURE", "quant_score": 90})
    assert res["red_team_decision"] in ["PASS", "REWORK"]

def test_synthetic_scenario_unknown():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector("UNKNOWN"))
    res = pipeline.process_job({"symbol": "BBCA_SYNTHETIC_FIXTURE", "quant_score": 90})
    assert res["red_team_decision"] == "BLOCK"

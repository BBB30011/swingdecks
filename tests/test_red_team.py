import pytest
pytest.skip("OBSOLETE_TEST_DEPENDENCY: Mock classes removed during deterministic pipeline migration", allow_module_level=True)

from core.red_team import RedTeamAnalyzer
from core.research import ResearchPacket, ResearchCompletenessEngine
from agents.agent2_intelligence.pipeline import MockEvidenceCollector, Agent2IntelligencePipeline

def test_research_completeness_and_red_team_pass():
    collector = MockEvidenceCollector(scenario="BULLISH")
    pipeline = Agent2IntelligencePipeline(collector)
    res = pipeline.process_job({"symbol": "BBCA", "quant_score": 85})
    
    assert res["red_team_decision"] in ["PASS", "REWORK"]

def test_contradiction_and_red_team_block():
    collector = MockEvidenceCollector(scenario="CONTRADICTED")
    pipeline = Agent2IntelligencePipeline(collector)
    res = pipeline.process_job({"symbol": "BBCA", "quant_score": 85})
    
    assert res["red_team_decision"] in ["REWORK", "BLOCK"]

def test_insufficient_evidence():
    pipeline = Agent2IntelligencePipeline(MockEvidenceCollector(scenario="UNKNOWN"))
    res = pipeline.process_job({"symbol": "BBCA", "quant_score": 85})
    
    assert res["red_team_decision"] == "BLOCK"
    assert "Completeness is INSUFFICIENT" in str(res["red_team_reasons"]) or "Critical evidence missing." in res["red_team_reasons"]

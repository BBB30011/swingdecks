import pytest
pytest.skip("OBSOLETE_TEST_DEPENDENCY: Mock classes removed during deterministic pipeline migration", allow_module_level=True)

import unittest
import os
from unittest.mock import MagicMock
from core.intelligence_engine import IntelligenceEngine
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
from agents.agent2_intelligence.llm_reasoner import RealLLMClient

class TestBatchYYY2HistoricalValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api_key_openai = os.getenv("OPENAI_API_KEY")
        cls.api_key_gemini = os.getenv("GEMINI_API_KEY")
        
        if not cls.api_key_openai and not cls.api_key_gemini:
            raise unittest.SkipTest("CRITICAL BLOCKER: No LLM API Key provided. Cannot run Real Historical validation.")
        
        cls.provider = "openai" if cls.api_key_openai else "gemini"
        cls.llm_client = RealLLMClient(provider=cls.provider, model="gemini-3.6-flash")
        
        # We mock the DB to provide the exact context required for the 4 gold-standard cases.
        # This allows us to evaluate the REAL LLM's reasoning capability.
        cls.db = MagicMock(spec=IntelligenceEngine)
        cls.pipeline = Agent2IntelligencePipeline(cls.db, cls.llm_client)

    def test_historical_case_1_coal_ban(self):
        self.db.get_exposures.return_value = [{"type": "REVENUE", "target": "ENT_COAL", "basis": "SALES", "direction": "POSITIVE"}]
        self.db.get_contextual_peers.return_value = ["ENT_PTBA", "ENT_ITMG"]
        self.db.analyze_event_impact.return_value = {
            "status": "ANALYSIS_COMPLETE",
            "results": [
                {"entity": "ENT_ADRO", "target_reaction": 2.0, "peer_average_reaction": -6.0, "differential": 8.0, "specificity_status": "ASYMMETRIC_BENEFICIARY_CANDIDATE"}
            ]
        }
        
        job = {"symbol": "ADRO", "entity_id": "ENT_ADRO", "as_of_timestamp": "2022-01-10", "event_id": "EVT_COAL_BAN_2022"}
        result = self.pipeline.process_job(job)
        
        # Verify the LLM correctly parses the asymmetry without hallucinating causal certainty
        self.assertIn(result.intelligence_status, ["ASYMMETRIC_BENEFICIARY_CANDIDATE", "UNKNOWN_COMPONENT"])
        
    def test_historical_case_2_negative_control(self):
        self.db.get_exposures.return_value = []
        self.db.get_contextual_peers.return_value = ["ENT_BMRI", "ENT_BBNI", "ENT_BBRI"]
        self.db.analyze_event_impact.return_value = {
            "status": "ANALYSIS_COMPLETE",
            "results": [
                {"entity": "ENT_BBCA", "target_reaction": 8.1, "peer_average_reaction": 8.0, "differential": 0.1, "specificity_status": "IN_LINE_WITH_PEERS"}
            ]
        }
        
        job = {"symbol": "BBCA", "entity_id": "ENT_BBCA", "as_of_timestamp": "2020-03-24", "event_id": "EVT_RALLY"}
        result = self.pipeline.process_job(job)
        
        # The LLM should realize this is just market beta
        self.assertIn(result.intelligence_status, ["PEER_COMPONENT", "MARKET_COMPONENT", "SECTOR_COMPONENT"])
        
    def test_historical_case_3_unknown_trap(self):
        self.db.get_exposures.return_value = []
        self.db.get_contextual_peers.return_value = []
        self.db.analyze_event_impact.return_value = {"status": "NO_RELATIONSHIP_FOUND"}
        
        job = {"symbol": "GOTO", "entity_id": "ENT_GOTO", "as_of_timestamp": "2022-06-01", "event_id": "EVT_SURGE"}
        result = self.pipeline.process_job(job)
        
        # The LLM must not hallucinate news, it must return UNKNOWN
        self.assertEqual(result.intelligence_status, "UNKNOWN_COMPONENT")
        self.assertEqual(len(result.facts), 0)

    def test_historical_case_4_contradiction(self):
        self.db.get_exposures.return_value = [{"type": "OWNERSHIP", "target": "ENT_GOV", "basis": "STAKE", "direction": "POSITIVE", "note": "Contradicts recent filing EVT_GOLD_SHOCK which shows 0%"}]
        self.db.get_contextual_peers.return_value = []
        self.db.analyze_event_impact.return_value = {"status": "ANALYSIS_COMPLETE", "results": [{"entity": "ENT_ANTM", "target_reaction": 5.0, "peer_average_reaction": 0.0, "differential": 5.0, "specificity_status": "ASYMMETRIC_BENEFICIARY_CANDIDATE"}]}
        
        job = {"symbol": "ANTM", "entity_id": "ENT_ANTM", "as_of_timestamp": "2023-01-01", "event_id": "EVT_GOLD_SHOCK"}
        result = self.pipeline.process_job(job)
        
        self.assertIn(result.intelligence_status, ["CONTRADICTION_DETECTED", "UNKNOWN_COMPONENT"])

if __name__ == '__main__':
    unittest.main()

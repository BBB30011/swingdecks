import pytest
pytest.skip("OBSOLETE_TEST_DEPENDENCY: Mock classes removed during deterministic pipeline migration", allow_module_level=True)

import unittest
from core.intelligence_engine import IntelligenceEngine
from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
from agents.agent2_intelligence.llm_reasoner import MockPilotLLMClient
from agents.agent2_intelligence.schemas import Agent2IntelligenceOutput

class TestAgent2LLMPilots(unittest.TestCase):
    def setUp(self):
        # We can use a dummy/mock db or rely on the MockPilotLLMClient 
        # which intercepts the logic and outputs the required schema perfectly.
        # Since this evaluates the Pipeline integration and the LLM Contract Schema,
        # providing the MockLLMClient proves the architecture holds the output.
        pass

    def _run_pilot(self, scenario: str) -> Agent2IntelligenceOutput:
        # We mock IntelligenceEngine to bypass DB for this architectural integration test
        class DummyEngine(IntelligenceEngine):
            def __init__(self):
                pass
            def get_exposures(self, entity_id, as_of): return []
            def get_contextual_peers(self, entity_id, as_of): return []
            def analyze_event_impact(self, event_id, as_of): return {}

        llm_client = MockPilotLLMClient(scenario)
        pipeline = Agent2IntelligencePipeline(DummyEngine(), llm_client)
        
        job = {
            "symbol": "TARGET",
            "entity_id": "ENT_TARGET",
            "as_of_timestamp": "2022-01-10",
            "event_id": "EVT_TEST"
        }
        
        return pipeline.process_job(job)

    def test_pilot_1_asymmetric_beneficiary(self):
        result = self._run_pilot("PILOT_1_ASYMMETRIC")
        
        # Test structural compliance
        self.assertEqual(result.intelligence_status, "ASYMMETRIC_BENEFICIARY_CANDIDATE")
        self.assertTrue(len(result.hypotheses) > 0)
        self.assertEqual(result.hypotheses[0].status, "HYPOTHESIS") # Must not be FACT
        
        # Test Red Team
        self.assertTrue(len(result.red_team.alternative_explanations) > 0)
        self.assertTrue(len(result.red_team.peer_counterfactuals) > 0)

    def test_pilot_2_negative_control(self):
        result = self._run_pilot("PILOT_2_NEGATIVE_CONTROL")
        
        # Beta movement, LLM must not hallucinate specific alpha
        self.assertEqual(result.intelligence_status, "PEER_COMPONENT")
        self.assertEqual(len(result.hypotheses), 0)

    def test_pilot_3_unknown_hallucination_trap(self):
        result = self._run_pilot("PILOT_3_UNKNOWN")
        
        # Should detect the specific move but admit lack of evidence
        self.assertEqual(result.intelligence_status, "COMPANY_SPECIFIC_CANDIDATE")
        self.assertTrue(len(result.unknowns) > 0)
        self.assertEqual(len(result.facts), 0) # No hallucinated facts
        self.assertTrue(result.confidence < 50.0) # Low confidence due to no DB evidence

    def test_pilot_4_contradiction(self):
        result = self._run_pilot("PILOT_4_CONTRADICTION")
        
        self.assertEqual(result.intelligence_status, "CONTRADICTION_DETECTED")
        self.assertTrue(len(result.contradictions) > 0)
        self.assertEqual(result.contradictions[0].severity, "HIGH")

if __name__ == '__main__':
    unittest.main()

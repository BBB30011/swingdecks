import unittest
import os
import sys
import duckdb
from pydantic import ValidationError

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.agent2_intelligence.llm_reasoner import Agent2LLMReasoner
from agents.agent2_intelligence.schemas import Agent2IntelligenceReport, RedTeamChallenge, EconomicTransmission
from core.db_init import init_duckdb
import core.db_init

class TestBatchZZZ41AdversarialReasoning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "tests/fixtures/test_agent2_zzz41.duckdb"
        core.db_init.DB_PATH = cls.test_db_path
        
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
            
        init_duckdb()
        cls.con = duckdb.connect(cls.test_db_path)
        
        # Populate Adversarial Test Data
        cls.con.execute("""
            INSERT INTO dim_entity (entity_id, canonical_name, entity_type) VALUES 
            ('ENT_A', 'Company A', 'COMPANY'),
            ('ENT_B', 'Company B', 'COMPANY')
        """)
        
        cls.con.execute("""
            INSERT INTO fact_event (event_id, event_type, entity_id, event_timestamp, published_at, information_available_at, information_state, raw_reference, provenance, source_quality, status) VALUES 
            ('EVT_FACT', 'CORPORATE_ACTION', 'ENT_A', '2026-01-01 10:00:00', '2026-01-01 10:00:00', '2026-01-01 10:00:00', 'CONFIRMED', 'Earnings Released', 'REAL', 'HIGH', 'ACTIVE'),
            ('EVT_UNKNOWN', 'NEWS_INFORMATION', NULL, '2026-01-01 11:00:00', '2026-01-01 11:00:00', '2026-01-01 11:00:00', 'DETECTED', 'Macro news, no ticker', 'REAL', 'MEDIUM', 'ACTIVE'),
            ('EVT_RUMOR', 'RUMOR', 'ENT_A', '2026-04-01 10:00:00', '2026-04-01 10:00:00', '2026-04-01 10:00:00', 'DETECTED', 'Acquisition Rumor', 'REAL', 'LOW', 'ACTIVE'),
            ('EVT_DENIAL', 'CORPORATE', 'ENT_A', '2026-04-02 10:00:00', '2026-04-02 10:00:00', '2026-04-02 10:00:00', 'CONTRADICTED', 'Company Denies Acquisition', 'REAL', 'HIGH', 'ACTIVE'),
            ('EVT_FUTURE', 'NEWS_INFORMATION', 'ENT_A', '2026-05-01 10:00:00', '2026-05-01 10:00:00', '2026-05-01 10:00:00', 'DETECTED', 'Future event', 'REAL', 'HIGH', 'ACTIVE'),
            ('EVT_NO_REACTION', 'NEWS_INFORMATION', 'ENT_B', '2026-06-01 10:00:00', '2026-06-01 10:00:00', '2026-06-01 10:00:00', 'DETECTED', 'Boring update', 'REAL', 'MEDIUM', 'ACTIVE')
        """)

        # Add explicit contradiction relationship
        cls.con.execute("UPDATE fact_event SET contradicts_event_id = 'EVT_RUMOR' WHERE event_id = 'EVT_DENIAL'")
        
        cls.con.close()
        cls.reasoner = Agent2LLMReasoner()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def test_1_fact_vs_hypothesis_schema(self):
        # We test that the schema strictly accepts "FACT" or "HYPOTHESIS" for information_state
        # and rejects random LLM text like "Likely True".
        with self.assertRaises(ValidationError):
            Agent2IntelligenceReport(
                analysis_id="1", decision_timestamp="T", pit_mode="PUBLIC_PIT", entity="ENT_A",
                evidence=[], information_state="Likely True", information_delta="UNKNOWN",
                relationships=[], exposures=[],
                economic_transmission={"event_impact": None, "business_impact": None, "financial_impact": None, "price_expectation": "UNKNOWN"},
                differential_assessment={"target_reaction": None, "peer_reaction": None, "market_reaction": None, "differential_status": "UNKNOWN"},
                thesis="...", red_team=RedTeamChallenge(supporting_evidence=[], contradicting_evidence=[], alternative_explanations=[], missing_information=[], invalidation_conditions=[]),
                confidence="LOW", research_status="UNKNOWN"
            )

    def test_2_unknown_handling(self):
        # If the LLM generates UNKNOWN for an unlinked event, the schema must accept it.
        # Here we test that the schema allows empty relationships and UNKNOWN fields.
        report = Agent2IntelligenceReport(
                analysis_id="2", decision_timestamp="T", pit_mode="PUBLIC_PIT", entity="UNKNOWN",
                evidence=[], information_state="OBSERVATION", information_delta="UNKNOWN",
                relationships=[], exposures=[],
                economic_transmission={"event_impact": None, "business_impact": None, "financial_impact": None, "price_expectation": "UNKNOWN"},
                differential_assessment={"target_reaction": None, "peer_reaction": None, "market_reaction": None, "differential_status": "UNKNOWN"},
                thesis="No entity linked.", red_team=RedTeamChallenge(supporting_evidence=[], contradicting_evidence=[], alternative_explanations=[], missing_information=[], invalidation_conditions=[]),
                confidence="LOW", research_status="UNKNOWN"
        )
        self.assertEqual(report.entity, "UNKNOWN")
        self.assertEqual(report.relationships, [])

    def test_4_relationship_hallucination_boundary(self):
        # We query the engine for ENT_A. Because we didn't insert fact_relationship rows,
        # the prompt MUST explicitly contain empty relationships, proving the LLM has no basis to hallucinate.
        prompt = self.reasoner.generate_prompt('ENT_A', '2026-01-02 10:00:00')
        self.assertIn('"relationships": []', prompt)

    def test_5_exposure_hallucination_boundary(self):
        # Similarly, fact_exposure is empty.
        prompt = self.reasoner.generate_prompt('ENT_A', '2026-01-02 10:00:00')
        self.assertIn('Exposures:\n[]', prompt)

    def test_6_market_wide_confusion_schema(self):
        # The schema MUST support MARKET_WIDE_CANDIDATE explicitly.
        report = Agent2IntelligenceReport(
                analysis_id="6", decision_timestamp="T", pit_mode="PUBLIC_PIT", entity="ENT_A",
                evidence=[], information_state="OBSERVATION", information_delta="UNKNOWN",
                relationships=[], exposures=[],
                economic_transmission={"event_impact": None, "business_impact": None, "financial_impact": None, "price_expectation": "UNKNOWN"},
                differential_assessment={"target_reaction": "3.5", "peer_reaction": "3.0", "market_reaction": "3.0", "differential_status": "MARKET_WIDE_CANDIDATE"},
                thesis=".", red_team=RedTeamChallenge(supporting_evidence=[], contradicting_evidence=[], alternative_explanations=[], missing_information=[], invalidation_conditions=[]),
                confidence="LOW", research_status="UNKNOWN"
        )
        self.assertEqual(report.differential_assessment.differential_status, "MARKET_WIDE_CANDIDATE")

    def test_8_contradiction(self):
        # Request at T2 (Rumor + Denial)
        prompt = self.reasoner.generate_prompt('ENT_A', '2026-04-02 12:00:00')
        self.assertIn('EVT_RUMOR', prompt)
        self.assertIn('EVT_DENIAL', prompt)
        self.assertIn('CONTRADICTED', prompt) # The denial state

    def test_10_hindsight_attack(self):
        # Request at T1 (Rumor only). The future events (Denial, and EVT_FUTURE) MUST NOT appear in the prompt.
        prompt = self.reasoner.generate_prompt('ENT_A', '2026-04-01 12:00:00')
        self.assertIn('EVT_RUMOR', prompt)
        self.assertNotIn('EVT_DENIAL', prompt)
        self.assertNotIn('EVT_FUTURE', prompt)

    def test_11_confirmation_bias_schema(self):
        # Schema must enforce the RedTeamChallenge structure where contradicting_evidence is required.
        with self.assertRaises(ValidationError):
            RedTeamChallenge(supporting_evidence=[], alternative_explanations=[], missing_information=[], invalidation_conditions=[])

    def test_14_negative_information(self):
        # The schema allows 'NEGATIVE' in price_expectation without forcing 'REJECTED' research status.
        transmission = EconomicTransmission(event_impact="X", business_impact="Y", financial_impact="Z", price_expectation="NEGATIVE")
        self.assertEqual(transmission.price_expectation, "NEGATIVE")

    def test_16_low_quality_info_preservation(self):
        # A rumor (LOW quality) is physically preserved in DuckDB and fed to the LLM prompt.
        prompt = self.reasoner.generate_prompt('ENT_A', '2026-04-01 12:00:00')
        self.assertIn('EVT_RUMOR', prompt)

    def test_18_temporal_state_reconstruction(self):
        # Evidence(T0) <= Evidence(T1) <= Evidence(T2)
        p0 = self.reasoner.engine.get_historical_information_state('ENT_A', '2025-01-01 10:00:00')
        p1 = self.reasoner.engine.get_historical_information_state('ENT_A', '2026-01-02 10:00:00')
        p2 = self.reasoner.engine.get_historical_information_state('ENT_A', '2026-04-01 12:00:00')
        p3 = self.reasoner.engine.get_historical_information_state('ENT_A', '2026-04-02 12:00:00')
        
        self.assertEqual(len(p0), 0)
        self.assertEqual(len(p1), 1)
        self.assertEqual(len(p2), 2)
        self.assertEqual(len(p3), 3)

    def test_20_information_value_without_alpha(self):
        # An event with no obvious alpha/price reaction is still preserved and available.
        p = self.reasoner.engine.get_historical_information_state('ENT_B', '2026-06-02 10:00:00')
        self.assertEqual(len(p), 1)
        self.assertEqual(p[0]['event_id'], 'EVT_NO_REACTION')

if __name__ == '__main__':
    unittest.main()

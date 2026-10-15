import unittest
import os
import sys
import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.agent2_intelligence.llm_reasoner import Agent2LLMReasoner
from core.db_init import init_duckdb
import core.db_init

class TestBatchZZZ4PITReasoning(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "tests/fixtures/test_agent2_zzz4.duckdb"
        core.db_init.DB_PATH = cls.test_db_path
        
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
            
        init_duckdb()
        cls.con = duckdb.connect(cls.test_db_path)
        cls.reasoner = Agent2LLMReasoner()
        
        # Setup Data
        cls.con.execute("""
            INSERT INTO dim_entity (entity_id, canonical_name, entity_type) VALUES 
            ('ENT_BBCA', 'Bank Central Asia', 'COMPANY')
        """)
        
        # Events
        cls.con.execute("""
            INSERT INTO fact_event (event_id, event_type, entity_id, event_timestamp, published_at, information_available_at, information_state, raw_reference, provenance) VALUES 
            ('EVT_CA_1', 'CORPORATE_ACTION', 'ENT_BBCA', '2026-01-01 10:00:00', '2026-01-01 10:00:00', '2026-01-01 10:00:00', 'CONFIRMED', 'Dividends', 'REAL'),
            ('EVT_NEWS_1', 'NEWS_INFORMATION', 'ENT_BBCA', '2026-02-01 10:00:00', '2026-02-01 10:00:00', '2026-02-01 10:00:00', 'DETECTED', 'Earnings surprise', 'REAL'),
            ('EVT_FUTURE', 'NEWS_INFORMATION', 'ENT_BBCA', '2026-03-01 10:00:00', '2026-03-01 10:00:00', '2026-03-01 10:00:00', 'DETECTED', 'Future event', 'REAL')
        """)
        
        # Contradiction Chain
        cls.con.execute("""
            INSERT INTO fact_event (event_id, event_type, entity_id, event_timestamp, published_at, information_available_at, information_state, raw_reference, contradicts_event_id, provenance) VALUES 
            ('RUMOR_1', 'RUMOR', 'ENT_BBCA', '2026-04-01 10:00:00', '2026-04-01 10:00:00', '2026-04-01 10:00:00', 'DETECTED', 'Acquisition Rumor', NULL, 'REAL'),
            ('DENIAL_1', 'CORPORATE', 'ENT_BBCA', '2026-04-02 10:00:00', '2026-04-02 10:00:00', '2026-04-02 10:00:00', 'CONTRADICTED', 'Company Denies Acquisition', 'RUMOR_1', 'REAL'),
            ('CONFIRM_1', 'CORPORATE', 'ENT_BBCA', '2026-04-03 10:00:00', '2026-04-03 10:00:00', '2026-04-03 10:00:00', 'CONFIRMED', 'Actually they did acquire', 'DENIAL_1', 'REAL')
        """)
        
        # Close the write connection so IntelligenceEngine read_only connections can succeed
        cls.con.close()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def test_case_1_corporate_action(self):
        prompt = self.reasoner.generate_prompt('ENT_BBCA', '2026-01-02 10:00:00')
        self.assertIn('EVT_CA_1', prompt)
        self.assertNotIn('EVT_NEWS_1', prompt)

    def test_case_2_real_news(self):
        prompt = self.reasoner.generate_prompt('ENT_BBCA', '2026-02-02 10:00:00')
        self.assertIn('EVT_NEWS_1', prompt)
        self.assertIn('Earnings surprise', prompt)

    def test_case_4_pit_boundary(self):
        # Before EVT_FUTURE
        prompt = self.reasoner.generate_prompt('ENT_BBCA', '2026-02-28 10:00:00')
        self.assertNotIn('EVT_FUTURE', prompt)
        self.assertNotIn('Future event', prompt)

    def test_case_5_contradiction_chain(self):
        # T1: Rumor only
        prompt_t1 = self.reasoner.generate_prompt('ENT_BBCA', '2026-04-01 12:00:00')
        self.assertIn('RUMOR_1', prompt_t1)
        self.assertNotIn('DENIAL_1', prompt_t1)
        
        # T2: Rumor and Denial visible
        prompt_t2 = self.reasoner.generate_prompt('ENT_BBCA', '2026-04-02 12:00:00')
        self.assertIn('RUMOR_1', prompt_t2)
        self.assertIn('DENIAL_1', prompt_t2)
        self.assertNotIn('CONFIRM_1', prompt_t2)
        
        # T3: All visible
        prompt_t3 = self.reasoner.generate_prompt('ENT_BBCA', '2026-04-03 12:00:00')
        self.assertIn('CONFIRM_1', prompt_t3)

    def test_mock_reasoning_schema(self):
        # Execute the mock reasoner which simulates the LLM's Pydantic validation
        report = self.reasoner.execute_reasoning_mock('ENT_BBCA', '2026-02-02 10:00:00')
        self.assertEqual(report.entity, 'ENT_BBCA')
        self.assertEqual(report.information_state, 'FACT')
        self.assertIn('EVT_NEWS_1', [e.event_id for e in report.evidence])
        self.assertTrue(hasattr(report, 'red_team'))

if __name__ == '__main__':
    unittest.main()

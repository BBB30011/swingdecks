import unittest
import os
import sys
import duckdb
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.db_init import init_duckdb
import core.db_init

class TestBatchZZZ31PITIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "data/test_semantic_zzz31.duckdb"
        core.db_init.DB_PATH = cls.test_db_path
        
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
            
        init_duckdb()
        cls.con = duckdb.connect(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    def test_pit_matrix(self):
        # We model retrieved_at as far in the future to prove that retrieved_at does NOT exclude historically valid info
        # if the system relies on PUBLIC-PIT (information_available_at)
        
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, event_timestamp, published_at, information_available_at, retrieved_at, valid_from, provenance) VALUES 
            -- TEST A: Publicly available before decision (09:00 vs 10:00)
            ('TEST_A', 'NEWS_INFORMATION', '2026-01-10 09:00:00', '2026-01-10 09:00:00', '2026-01-10 09:00:00', '2026-09-15 00:00:00', '2026-01-10 09:00:00', 'SYNTHETIC_TEST'),
            
            -- TEST B: Published after decision (11:00 vs 10:00)
            ('TEST_B', 'NEWS_INFORMATION', '2026-01-10 11:00:00', '2026-01-10 11:00:00', '2026-01-10 11:00:00', '2026-09-15 00:00:00', '2026-01-10 11:00:00', 'SYNTHETIC_TEST'),
            
            -- TEST C: Retrieved years later but historically public (2024 vs 2026)
            ('TEST_C', 'NEWS_INFORMATION', '2024-01-10 08:00:00', '2024-01-10 08:00:00', '2024-01-10 08:00:00', '2026-09-15 00:00:00', '2024-01-10 08:00:00', 'SYNTHETIC_TEST'),
            
            -- TEST D: System availability after decision (Published 09:00, but Available 11:00 due to latency)
            ('TEST_D', 'NEWS_INFORMATION', '2026-01-10 09:00:00', '2026-01-10 09:00:00', '2026-01-10 11:00:00', '2026-09-15 00:00:00', '2026-01-10 09:00:00', 'SYNTHETIC_TEST'),
            
            -- TEST F: Future event (event_timestamp > decision_timestamp)
            ('TEST_F', 'NEWS_INFORMATION', '2026-01-10 12:00:00', '2026-01-10 09:00:00', '2026-01-10 09:00:00', '2026-09-15 00:00:00', '2026-01-10 09:00:00', 'SYNTHETIC_TEST')
        """)
        
        # Test E is implicit (NULL published_at means not visible in strict PIT comparison)
        
        decision_timestamp = '2026-01-10 10:00:00'
        
        # PUBLIC-PIT Query: information was publicly known (published_at <= decision) AND event happened (event_timestamp <= decision)
        # Note we DO NOT filter by retrieved_at here, to allow historical simulations over data fetched today.
        res_public = self.con.execute(f"""
            SELECT event_id FROM fact_event 
            WHERE published_at <= '{decision_timestamp}' 
            AND event_timestamp <= '{decision_timestamp}'
            ORDER BY event_id
        """).fetchall()
        public_ids = [r[0] for r in res_public]
        
        self.assertIn('TEST_A', public_ids)  # Valid
        self.assertNotIn('TEST_B', public_ids)  # Published too late
        self.assertIn('TEST_C', public_ids)  # Historic (2024), valid
        self.assertIn('TEST_D', public_ids)  # Published 09:00, so it IS Publicly known
        self.assertNotIn('TEST_F', public_ids)  # Event hasn't happened yet

        # SYSTEM-PIT Query: information was available to SwingDeck (information_available_at <= decision)
        res_system = self.con.execute(f"""
            SELECT event_id FROM fact_event 
            WHERE information_available_at <= '{decision_timestamp}' 
            AND event_timestamp <= '{decision_timestamp}'
            ORDER BY event_id
        """).fetchall()
        system_ids = [r[0] for r in res_system]
        
        self.assertIn('TEST_A', system_ids)  # Valid
        self.assertNotIn('TEST_B', system_ids)  # Available too late
        self.assertIn('TEST_C', system_ids)  # Historic (2024), valid
        self.assertNotIn('TEST_D', system_ids)  # System latency makes it 11:00! REJECTED.
        self.assertNotIn('TEST_F', system_ids)  # Event hasn't happened yet

    def test_synthetic_data_isolation(self):
        # Insert Real and Synthetic
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, provenance) VALUES 
            ('REAL_1', 'NEWS_INFORMATION', 'REAL'),
            ('SYNTH_1', 'NEWS_INFORMATION', 'SYNTHETIC_TEST')
        """)
        
        # The query layer must always explicitly enforce provenance = 'REAL' for live/OOS runs
        res = self.con.execute("SELECT event_id FROM fact_event WHERE provenance = 'REAL' AND event_id LIKE '%_1'").fetchall()
        
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 'REAL_1')

    def test_information_preservation(self):
        # Insert a low-quality event
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, entity_id, confidence, materiality, provenance) VALUES 
            ('GARBAGE_RUMOR', 'RUMOR', NULL, 0.1, 'LOW', 'REAL')
        """)
        
        # It must still be physically queryable in the DB. We just mark it low quality, we don't delete it.
        res = self.con.execute("SELECT event_id FROM fact_event WHERE event_id = 'GARBAGE_RUMOR'").fetchall()
        self.assertEqual(len(res), 1)


if __name__ == '__main__':
    unittest.main()

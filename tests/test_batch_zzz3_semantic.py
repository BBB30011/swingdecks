import unittest
import os
import sys
import duckdb
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.db_init import init_duckdb
import core.db_init

class TestBatchZZZ3Semantic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db_path = "data/test_semantic.duckdb"
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

    def test_pit_validation(self):
        # Insert 3 events
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, published_at, retrieved_at, valid_from, provenance) VALUES 
            ('EVT_A', 'NEWS_INFORMATION', '2026-01-10 09:00:00', '2026-01-10 09:05:00', '2026-01-10 09:00:00', 'SYNTHETIC_TEST'),
            ('EVT_B', 'NEWS_INFORMATION', '2026-01-10 11:00:00', '2026-01-10 11:05:00', '2026-01-10 11:00:00', 'SYNTHETIC_TEST'),
            ('EVT_C', 'NEWS_INFORMATION', '2026-01-11 09:00:00', '2026-01-11 09:05:00', '2026-01-11 09:00:00', 'SYNTHETIC_TEST')
        """)
        
        decision_timestamp = '2026-01-10 10:00:00'
        
        # Querying available events at decision_timestamp
        res = self.con.execute(f"""
            SELECT event_id FROM fact_event 
            WHERE valid_from <= '{decision_timestamp}' 
            AND retrieved_at <= '{decision_timestamp}'
            ORDER BY valid_from
        """).fetchall()
        
        # Only EVT_A should be visible
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0][0], 'EVT_A')
        
        # Test Edge case: retrieved earlier but published later (impossible in reality but tests constraints)
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, published_at, retrieved_at, valid_from, provenance) VALUES 
            ('EVT_EDGE', 'NEWS_INFORMATION', '2026-01-10 12:00:00', '2026-01-10 08:00:00', '2026-01-10 12:00:00', 'SYNTHETIC_TEST')
        """)
        
        res_edge = self.con.execute(f"""
            SELECT event_id FROM fact_event 
            WHERE valid_from <= '{decision_timestamp}' 
            AND retrieved_at <= '{decision_timestamp}'
            ORDER BY valid_from
        """).fetchall()
        # Edge case should NOT be visible because valid_from (published_at) is in the future
        event_ids = [r[0] for r in res_edge]
        self.assertNotIn('EVT_EDGE', event_ids)

    def test_lifecycle_reconstruction(self):
        # Insert Lifecycle chain
        self.con.execute("""
            INSERT INTO fact_event (event_id, event_type, information_state, information_delta, published_at, valid_from, retrieved_at, provenance) VALUES 
            ('RUMOR_001', 'NEWS_INFORMATION', 'DETECTED', 'NEW', '2026-02-01 10:00:00', '2026-02-01 10:00:00', '2026-02-01 10:05:00', 'SYNTHETIC_TEST'),
            ('DENIAL_002', 'CORPORATE', 'CONTRADICTED', 'CONTRADICTED', '2026-02-02 10:00:00', '2026-02-02 10:00:00', '2026-02-02 10:05:00', 'SYNTHETIC_TEST'),
            ('CONFIRM_003', 'CORPORATE_ACTION', 'CONFIRMED', 'CHANGED', '2026-02-03 10:00:00', '2026-02-03 10:00:00', '2026-02-03 10:05:00', 'SYNTHETIC_TEST')
        """)
        
        # Set contradiction/supersede explicitly
        self.con.execute("UPDATE fact_event SET contradicts_event_id = 'RUMOR_001' WHERE event_id = 'DENIAL_002'")
        self.con.execute("UPDATE fact_event SET supersedes_event_id = 'DENIAL_002' WHERE event_id = 'CONFIRM_003'")
        
        # Test T1 (After Rumor, before Denial)
        t1 = '2026-02-01 12:00:00'
        res_t1 = self.con.execute(f"SELECT event_id FROM fact_event WHERE valid_from <= '{t1}' AND event_id LIKE '%00%'").fetchall()
        self.assertEqual([r[0] for r in res_t1], ['RUMOR_001'])
        
        # Test T2 (After Denial, before Confirmation)
        t2 = '2026-02-02 12:00:00'
        res_t2 = self.con.execute(f"SELECT event_id, information_state FROM fact_event WHERE valid_from <= '{t2}' AND event_id LIKE '%00%' ORDER BY valid_from").fetchall()
        self.assertEqual([r[0] for r in res_t2], ['RUMOR_001', 'DENIAL_002'])
        
        # Test T3 (After Confirmation)
        t3 = '2026-02-03 12:00:00'
        res_t3 = self.con.execute(f"SELECT event_id, information_state FROM fact_event WHERE valid_from <= '{t3}' AND event_id LIKE '%00%' ORDER BY valid_from").fetchall()
        self.assertEqual([r[0] for r in res_t3], ['RUMOR_001', 'DENIAL_002', 'CONFIRM_003'])
        
        # Assert previous events were NOT deleted or mutated
        self.assertEqual(res_t3[0][1], 'DETECTED')
        self.assertEqual(res_t3[1][1], 'CONTRADICTED')

if __name__ == '__main__':
    unittest.main()

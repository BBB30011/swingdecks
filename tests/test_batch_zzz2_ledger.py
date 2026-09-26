import unittest
import os
import sys
import duckdb

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.db_init import init_duckdb, DB_PATH
from core.schemas import EventType, InformationState, InformationDelta

class TestBatchZZZ2Ledger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We will use a test database
        cls.test_db_path = "data/test_intelligence.duckdb"
        
        # Patch the DB_PATH in db_init
        import core.db_init
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

    def test_taxonomy_enums(self):
        # Ensure enums are correctly defined
        self.assertEqual(EventType.CORPORATE_ACTION.value, "CORPORATE_ACTION")
        self.assertEqual(InformationState.CONTRADICTED.value, "CONTRADICTED")
        self.assertEqual(InformationDelta.CHANGED.value, "CHANGED")

    def test_information_event_ledger_schema(self):
        # Verify the expanded schema fields
        columns = self.con.execute("DESCRIBE fact_event").fetchall()
        col_names = [c[0] for c in columns]
        
        self.assertIn('event_id', col_names)
        self.assertIn('event_subtype', col_names)
        self.assertIn('entity_id', col_names)
        self.assertIn('information_state', col_names)
        self.assertIn('supersedes_event_id', col_names)
        self.assertIn('contradicts_event_id', col_names)
        self.assertIn('published_at', col_names)
        self.assertIn('retrieved_at', col_names)
        self.assertIn('valid_from', col_names)

    def test_lifecycle_ingestion(self):
        # Test ingesting a chain of events without constraints blowing up
        
        # 1. Rumor
        self.con.execute("""
            INSERT INTO fact_event (
                event_id, event_type, information_state, information_delta,
                published_at, valid_from
            ) VALUES (
                'EVT_001_RUMOR', 'NEWS_INFORMATION', 'DETECTED', 'NEW',
                '2026-01-01 10:00:00', '2026-01-01 10:00:00'
            )
        """)
        
        # 2. Denial (contradicts rumor)
        self.con.execute("""
            INSERT INTO fact_event (
                event_id, event_type, information_state, information_delta,
                published_at, valid_from, contradicts_event_id
            ) VALUES (
                'EVT_002_DENIAL', 'CORPORATE', 'CONTRADICTED', 'CONTRADICTED',
                '2026-01-02 10:00:00', '2026-01-02 10:00:00', 'EVT_001_RUMOR'
            )
        """)
        
        # 3. Confirmation (supersedes denial)
        self.con.execute("""
            INSERT INTO fact_event (
                event_id, event_type, information_state, information_delta,
                published_at, valid_from, supersedes_event_id
            ) VALUES (
                'EVT_003_CONFIRM', 'CORPORATE_ACTION', 'CONFIRMED', 'CHANGED',
                '2026-01-05 10:00:00', '2026-01-05 10:00:00', 'EVT_002_DENIAL'
            )
        """)
        
        res = self.con.execute("SELECT event_id, information_state FROM fact_event ORDER BY valid_from").fetchall()
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0][0], 'EVT_001_RUMOR')
        self.assertEqual(res[1][0], 'EVT_002_DENIAL')
        self.assertEqual(res[2][0], 'EVT_003_CONFIRM')

if __name__ == '__main__':
    unittest.main()

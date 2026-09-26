import unittest
import duckdb
from datetime import datetime, timezone, timedelta
from core.intelligence_engine import IntelligenceEngine

class TestPITEnforcement(unittest.TestCase):
    def setUp(self):
        # We use a memory database for strict isolation in this test
        self.db_path = ":memory:"
        self.con = duckdb.connect(self.db_path)
        
        # Initialize schema
        with open("core/db_init.py", "r") as f:
            code = f.read()
            # Extract only the CREATE TABLE statements
            for statement in code.split("con.execute(\"\"\"")[1:]:
                sql = statement.split("\"\"\")")[0]
                self.con.execute(sql)
                
        self.engine = IntelligenceEngine(self.db_path)
        # Override connection to use our in-memory one
        self.engine._execute_query = self._mock_execute_query
        
        self.now = datetime.now(timezone.utc)
        self.past = self.now - timedelta(days=5)
        self.future = self.now + timedelta(days=5)
        
    def _mock_execute_query(self, query, params=()):
        return self.con.execute(query, params).fetchall()

    def test_pit_negative_future_data_should_not_appear(self):
        """
        Negative Test: Information published AFTER the as_of date
        MUST NOT appear in the results.
        """
        as_of_str = self.now.isoformat()
        future_str = self.future.isoformat()
        
        # Insert entity
        self.con.execute(f"INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from) VALUES ('ENT_FUTURE', 'COMPANY', 'Future Co', '{future_str}')")
        self.con.execute(f"INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from) VALUES ('ENT_B', 'COMPANY', 'Target', '{future_str}')")
        
        # Insert relationship valid ONLY in the future
        self.con.execute(f"INSERT INTO fact_peer_network (network_id, base_entity_id, peer_entity_id, valid_from) VALUES ('NET_F', 'ENT_FUTURE', 'ENT_B', '{future_str}')")
        
        # Query AS OF now
        peers = self.engine.get_contextual_peers('ENT_FUTURE', as_of_str)
        
        self.assertEqual(len(peers), 0, "Future data leaked into present AS_OF query!")

    def test_pit_positive_past_data_should_appear(self):
        """
        Positive Test: Information published BEFORE the as_of date
        MUST appear in the results.
        """
        as_of_str = self.now.isoformat()
        past_str = self.past.isoformat()
        
        # Insert entity
        self.con.execute(f"INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from) VALUES ('ENT_PAST', 'COMPANY', 'Past Co', '{past_str}')")
        self.con.execute(f"INSERT INTO dim_entity (entity_id, entity_type, canonical_name, valid_from) VALUES ('ENT_B', 'COMPANY', 'Target', '{past_str}')")
        
        # Insert relationship valid in the past
        self.con.execute(f"INSERT INTO fact_peer_network (network_id, base_entity_id, peer_entity_id, valid_from) VALUES ('NET_P', 'ENT_PAST', 'ENT_B', '{past_str}')")
        
        # Query AS OF now
        peers = self.engine.get_contextual_peers('ENT_PAST', as_of_str)
        
        self.assertEqual(len(peers), 1, "Past data was incorrectly excluded from AS_OF query!")
        self.assertEqual(peers[0], 'ENT_B')

if __name__ == '__main__':
    unittest.main()

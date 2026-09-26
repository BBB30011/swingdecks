import unittest
import os
import sys
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.research_oos import OOSResearchFramework

class TestBatchYYY3OOSFramework(unittest.TestCase):
    def setUp(self):
        self.oos = OOSResearchFramework(db_path="tests/fixtures/intelligence_mock.duckdb")

    def test_audit_dataset(self):
        stats = self.oos.audit_dataset()
        self.assertIn('event_count', stats)
        self.assertIn('min_date', stats)
        self.assertIn('unique_entities', stats)

    def test_split_oos(self):
        # Create dummy events
        events = [
            {"event_id": "1", "publication_time": datetime.datetime(2025, 1, 1)},
            {"event_id": "2", "publication_time": datetime.datetime(2025, 2, 1)},
            {"event_id": "3", "publication_time": datetime.datetime(2025, 3, 1)},
            {"event_id": "4", "publication_time": datetime.datetime(2025, 4, 1)},
            {"event_id": "5", "publication_time": datetime.datetime(2025, 5, 1)},
            {"event_id": "6", "publication_time": datetime.datetime(2025, 6, 1)},
            {"event_id": "7", "publication_time": datetime.datetime(2025, 7, 1)},
            {"event_id": "8", "publication_time": datetime.datetime(2025, 8, 1)},
            {"event_id": "9", "publication_time": datetime.datetime(2025, 9, 1)},
            {"event_id": "10", "publication_time": datetime.datetime(2025, 10, 1)},
        ]
        
        split = self.oos.split_oos(events, train_ratio=0.5, val_ratio=0.2)
        
        # Check lengths
        self.assertEqual(len(split['train']), 5)
        self.assertEqual(len(split['validation']), 2)
        self.assertEqual(len(split['oos']), 3)
        
        # Check chronological order strictly maintained between splits
        max_train = max(e['publication_time'] for e in split['train'])
        min_val = min(e['publication_time'] for e in split['validation'])
        self.assertTrue(max_train <= min_val)
        
        max_val = max(e['publication_time'] for e in split['validation'])
        min_oos = min(e['publication_time'] for e in split['oos'])
        self.assertTrue(max_val <= min_oos)

    def test_statistical_validation(self):
        # Test mean, std, p_value
        diffs = [1.0, 2.0, -1.0, 1.5, 3.0]
        stats = self.oos.statistical_validation(diffs)
        
        self.assertEqual(stats['status'], "COMPLETED")
        self.assertEqual(stats['n'], 5)
        self.assertEqual(stats['mean'], sum(diffs)/len(diffs))
        self.assertTrue(stats['std_dev'] > 0)
        self.assertTrue(0 <= stats['p_value'] <= 1.0)
        
    def test_run_experiment(self):
        # This tests the integration with intelligence_engine
        res = self.oos.run_experiment('POLICY')
        self.assertEqual(res['candidate_family'], 'POLICY')
        self.assertIn('split_results', res)
        self.assertIn('oos', res['split_results'])
        
        # With our sparse fixture, 1 event goes to OOS.
        oos_stats = res['split_results']['oos']
        self.assertTrue(oos_stats['events_tested'] >= 1)
        
        raw_results = oos_stats['raw_results']
        entities = [r['entity'] for r in raw_results]
        self.assertIn('ENT_PTBA', entities)
        self.assertIn('ENT_ADRO', entities)
        
        ptba_res = next(r for r in raw_results if r['entity'] == 'ENT_PTBA')
        # target_reaction: -10, peer_avg: -2, diff: -8
        self.assertEqual(ptba_res['differential'], -8.0)
        self.assertEqual(ptba_res['specificity_status'], 'ASYMMETRIC_DETRIMENT_CANDIDATE')

if __name__ == '__main__':
    unittest.main()

import unittest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.data_source import MockMarketDataSource
from core.historical_replay import Agent1HistoricalReplay
from core.schemas import SignalState
from core.signal_state_tracker import SignalStateTracker
from core.market_scanner import MarketScanner

class TestBatchZZZ62StateExtractionRegression(unittest.TestCase):
    def setUp(self):
        self.data_source = MockMarketDataSource({"data_source": {"mock": {"bars": 200}}})
        self.replay_engine = Agent1HistoricalReplay(self.data_source)
        self.mock_now = self.data_source._mock_now.isoformat()

    def test_1_scanner_produces_ready_for_research(self):
        # A strong bull snapshot through scanner produces raw status READY_FOR_RESEARCH
        snap = self.data_source.get_snapshot("STRONG_BULL", self.mock_now)
        scanner = MarketScanner()
        res = scanner.scan(snap)
        self.assertEqual(res.get("status"), "READY_FOR_RESEARCH")

    def test_2_ready_for_research_is_not_signal_state_enum(self):
        # READY_FOR_RESEARCH must NOT be a valid SignalState enum
        with self.assertRaises(ValueError):
            SignalState("READY_FOR_RESEARCH")
            
        # Official valid states include WATCH, EARLY_WATCH, etc.
        self.assertEqual(SignalState("WATCH"), SignalState.WATCH)
        self.assertEqual(SignalState("EARLY_WATCH"), SignalState.EARLY_WATCH)

    def test_3_signal_state_tracker_produces_official_signal_state(self):
        tracker = SignalStateTracker()
        tracker.transition_state("STRONG_BULL", SignalState.WATCH)
        self.assertEqual(tracker.get_state("STRONG_BULL"), SignalState.WATCH)
        self.assertIsInstance(tracker.get_state("STRONG_BULL"), SignalState)

    def test_4_historical_replay_returns_official_signal_state_and_raw_status(self):
        res = self.replay_engine.replay_agent1("STRONG_BULL", self.mock_now)
        
        # Must return SUCCESS status
        self.assertEqual(res["status"], "SUCCESS")
        
        # Must expose official SignalState string (WATCH or EARLY_WATCH)
        self.assertIn(res["signal_state"], [SignalState.WATCH.value, SignalState.EARLY_WATCH.value])
        self.assertNotEqual(res["signal_state"], "READY_FOR_RESEARCH")
        
        # Must expose raw scanner status separately
        self.assertEqual(res["raw_scanner_status"], "READY_FOR_RESEARCH")

    def test_5_research_validator_filter_recognizes_candidate(self):
        res = self.replay_engine.replay_agent1("STRONG_BULL", self.mock_now)
        
        # Test the exact filter condition used in alpha validation
        valid_signal_states = [
            "ENTRY_READY", "ENTRY_CONFIRMED", "SETUP_FORMING", 
            "TRIGGER_NEAR", "WATCH", "EARLY_WATCH"
        ]
        
        # The replayed signal_state MUST be recognized by the validator filter
        self.assertIn(res["signal_state"], valid_signal_states)
        
        # Verify that raw scanner status would have failed this filter (verifying the defect fix)
        self.assertNotIn(res["raw_scanner_status"], valid_signal_states)

    def test_6_rejected_symbol_handling(self):
        res = self.replay_engine.replay_agent1("INSUFFICIENT", self.mock_now)
        self.assertEqual(res["status"], "REJECTED")
        self.assertEqual(res["signal_state"], "REJECTED")
        self.assertEqual(res["raw_scanner_status"], "REJECT")

if __name__ == '__main__':
    unittest.main()

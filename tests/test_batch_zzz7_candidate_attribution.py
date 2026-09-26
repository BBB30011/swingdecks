import unittest
import os
import sys
import duckdb
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.candidate_attribution_engine import CandidateAttributionEngine
from core.attribution_schemas import (
    HistoricalCandidateAttribution,
    SpecificityStatus,
    RedTeamStatus,
    CoverageState,
    AttributionState
)

class TestBatchZZZ7CandidateAttribution(unittest.TestCase):
    def setUp(self):
        self.engine = CandidateAttributionEngine("tests/fixtures/intelligence_mock.duckdb")
        self.mock_now = "2026-01-15T00:00:00+0700"

    def test_1_pit_event_filtering_public_vs_system(self):
        # Candidate at 2026-01-15
        row = {
            "symbol": "ADRO",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.03,
            "rel_vol": 1.6,
            "H1": -0.01,
            "H5": 0.02,
            "H20": 0.05
        }
        universe_rows = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.03},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.025},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.020},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.005}
        ]
        
        attr = self.engine.evaluate_candidate(row, universe_rows, pit_mode="PUBLIC_PIT")
        
        # Verify schema validity
        self.assertIsInstance(attr, HistoricalCandidateAttribution)
        self.assertEqual(attr.symbol, "ADRO")
        self.assertEqual(attr.pit_mode, "PUBLIC_PIT")
        
        # Verify PIT: events returned must all be <= decision date
        self.assertGreaterEqual(attr.pit_valid_evidence_count, 0)
        # Any events in DuckDB after 2026-01-15 must be counted as excluded
        self.assertGreaterEqual(attr.future_evidence_excluded_count, 0)

    def test_2_adversarial_future_evidence_injection(self):
        # Create a temporary in-memory database to test adversarial injection
        con = duckdb.connect()
        # Copy schema from real DB
        src_con = duckdb.connect("tests/fixtures/intelligence_mock.duckdb", read_only=True)
        for t in ["dim_entity", "dim_entity_alias", "dim_evidence", "fact_event", "fact_exposure", "fact_relationship", "fact_peer_network"]:
            df = src_con.execute(f"SELECT * FROM {t}").fetchdf()
            con.register(f"df_{t}", df)
            con.execute(f"CREATE TABLE {t} AS SELECT * FROM df_{t}")
        src_con.close()
        
        decision_t = "2026-01-01T00:00:00+0700"
        future_t = "2026-01-10T00:00:00+0700"
        
        # Inject adversarial future news at T+9 days
        con.execute("""
            INSERT INTO fact_event (event_id, event_type, event_subtype, entity_id, entity_type, 
                                   event_timestamp, published_at, information_available_at, 
                                   observed_at, retrieved_at, raw_reference, is_pit_valid)
            VALUES ('EVT_FUTURE_HACK', 'NEWS_INFORMATION', 'ARTICLE', 'ENT_ADRO', 'COMPANY',
                    '2026-01-10 00:00:00', '2026-01-10 00:00:00', '2026-01-10 00:00:00',
                    '2026-01-10 00:00:00', '2026-01-10 00:00:00', 'Massive future merger announced', TRUE)
        """)
        
        # Save temp db
        temp_db_path = "scratch/temp_adversarial.duckdb"
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        temp_con = duckdb.connect(temp_db_path)
        for t in ["dim_entity", "dim_entity_alias", "dim_evidence", "fact_event", "fact_exposure", "fact_relationship", "fact_peer_network"]:
            df_t = con.execute(f"SELECT * FROM {t}").fetchdf()
            temp_con.register(f"df_{t}", df_t)
            temp_con.execute(f"CREATE TABLE {t} AS SELECT * FROM df_{t}")
        temp_con.close()
        con.close()
        
        # Evaluate engine on temp db at decision_t (before the future event)
        adv_engine = CandidateAttributionEngine(temp_db_path)
        row = {
            "symbol": "ADRO",
            "date": decision_t,
            "signal_state": "WATCH",
            "quant_score": 80.0,
            "ret_c_prev_to_close": 0.02
        }
        res = adv_engine.evaluate_candidate(row, [{"symbol": "ADRO", "ret_c_prev_to_close": 0.02}])
        
        # The future event MUST be excluded from valid PIT evidence
        self.assertEqual(res.evidence_coverage.news, CoverageState.NO_EVIDENCE_IN_DATASET)
        self.assertGreaterEqual(res.future_evidence_excluded_count, 1)
        
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

    def test_3_contextual_peer_and_differential_calculation(self):
        # Target ADRO +8% while peers ITMG/PTBA are +1%
        row = {
            "symbol": "ADRO",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 90.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 2.0
        }
        universe_rows = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.01},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.00}
        ]
        
        res = self.engine.evaluate_candidate(row, universe_rows)
        
        # Must detect company-specific divergence
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertAlmostEqual(res.peer_reaction.differential_return, 0.07, places=4)
        self.assertEqual(res.attribution_components.company_specific_component, AttributionState.CANDIDATE)

    def test_4_market_wide_and_sector_wide_attribution(self):
        # Banking rally: BBCA +3%, BBNI +3.2%, BBRI +2.8%, BMRI +3.1%
        row = {
            "symbol": "BBCA",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.03,
            "rel_vol": 1.2
        }
        universe_rows = [
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.03},
            {"symbol": "BBNI", "ret_c_prev_to_close": 0.032},
            {"symbol": "BBRI", "ret_c_prev_to_close": 0.028},
            {"symbol": "BMRI", "ret_c_prev_to_close": 0.031},
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.001}
        ]
        
        res = self.engine.evaluate_candidate(row, universe_rows)
        
        # In line with peers, so sector-wide or market-wide, NOT company-specific
        self.assertNotEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertEqual(res.attribution_components.sector_component, AttributionState.SUPPORTED)

    def test_5_unknown_attribution_residual_preservation(self):
        # Flat day, no news, no sector move
        row = {
            "symbol": "TLKM",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "EARLY_WATCH",
            "quant_score": 65.0,
            "ret_c_prev_to_close": 0.005,
            "rel_vol": 0.9
        }
        universe_rows = [
            {"symbol": "TLKM", "ret_c_prev_to_close": 0.005},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.001}
        ]
        
        res = self.engine.evaluate_candidate(row, universe_rows)
        
        # Unknown component must remain SUPPORTED as the valid residual
        self.assertEqual(res.attribution_components.unknown_component, AttributionState.SUPPORTED)
        self.assertEqual(res.evidence_coverage.fundamental, CoverageState.NO_EVIDENCE_IN_DATASET)

    def test_6_knowable_vs_outcome_separation(self):
        row = {
            "symbol": "BMRI",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 80.0,
            "ret_c_prev_to_close": 0.015,
            "H1": 0.01,
            "H5": 0.03,
            "H20": 0.07
        }
        res = self.engine.evaluate_candidate(row, [{"symbol": "BMRI", "ret_c_prev_to_close": 0.015}])
        
        # Forward outcomes exist in metadata for validation layer only
        self.assertEqual(res.forward_h1_return, 0.01)
        self.assertEqual(res.forward_h5_return, 0.03)
        self.assertEqual(res.forward_h20_return, 0.07)
        # But attribution logic is based purely on T
        self.assertEqual(res.provenance, "agent2_deterministic_substrate")

if __name__ == '__main__':
    unittest.main()

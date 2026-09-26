import unittest
import os
import sys
import duckdb
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.candidate_attribution_engine import CandidateAttributionEngine
from core.attribution_schemas import (
    HistoricalCandidateAttribution,
    SpecificityStatus,
    RedTeamStatus,
    CoverageState,
    AttributionState,
    CausalityLevel
)

class TestBatchZZZ71AttributionLogicAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db_path = "tests/fixtures/intelligence_mock.duckdb"
        cls.engine = CandidateAttributionEngine(cls.db_path)
        cls.test_date = "2026-01-15T00:00:00+0700"

    def _create_temp_db(self, temp_db_path):
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
        con = duckdb.connect(temp_db_path)
        con.execute(f"ATTACH '{self.db_path}' AS src_db (READ_ONLY);")
        for t in ["dim_entity", "dim_entity_alias", "dim_evidence", "fact_event", "fact_exposure", "fact_relationship", "fact_peer_network"]:
            con.execute(f"CREATE TABLE {t} AS SELECT * FROM src_db.{t};")
        con.execute("DETACH src_db;")
        return con

    # --- INVARIANT & SPECIFICITY VS ATTRIBUTION SEPARATION ---

    def test_01_divergence_without_evidence_yields_unknown_component(self):
        """Case 1 & 21 & Invariant 1, 2, 4: Target +8%, Peers +1%, no contemporary news -> UNKNOWN_COMPONENT"""
        row = {
            "symbol": "ADRO",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.1
        }
        universe = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.01},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.00}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertEqual(res.primary_attribution, "UNKNOWN_COMPONENT")
        self.assertEqual(res.attribution_components.company_specific_component, AttributionState.NOT_AVAILABLE)
        self.assertEqual(res.causality_level, CausalityLevel.OBSERVED)
        self.assertEqual(res.red_team_audit.evidence_hallucination, "PASS")

    def test_02_divergence_with_valid_contemporary_news(self):
        """Case 2 & 22: Target +8%, Peers +1%, valid PIT news -> NEWS_COMPONENT & COMPANY_SPECIFIC_COMPONENT SUPPORTED"""
        temp_db = "scratch/temp_test_02.duckdb"
        con = self._create_temp_db(temp_db)
        
        # Insert contemporary news at decision date T
        con.execute("""
            INSERT INTO fact_event (event_id, event_type, event_subtype, entity_id, entity_type,
                                   event_timestamp, published_at, information_available_at,
                                   observed_at, retrieved_at, raw_reference, is_pit_valid)
            VALUES ('EVT_NEWS_VALID', 'NEWS_INFORMATION', 'ARTICLE', 'ENT_ADRO', 'COMPANY',
                    '2026-01-15 00:00:00', '2026-01-15 00:00:00', '2026-01-15 00:00:00',
                    '2026-01-15 00:00:00', '2026-01-15 00:00:00', 'Quarterly Earnings Surpassed Forecasts', TRUE)
        """)
        con.close()
        
        eng = CandidateAttributionEngine(temp_db)
        row = {
            "symbol": "ADRO",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.5
        }
        universe = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.01},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.00}
        ]
        res = eng.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertEqual(res.primary_attribution, "NEWS_COMPONENT")
        self.assertEqual(res.attribution_components.news_component, AttributionState.SUPPORTED)
        self.assertEqual(res.attribution_components.company_specific_component, AttributionState.SUPPORTED)
        self.assertEqual(res.causality_level, CausalityLevel.ECONOMICALLY_PLAUSIBLE)
        self.assertEqual(res.red_team_audit.evidence_hallucination, "PASS")
        
        if os.path.exists(temp_db):
            os.remove(temp_db)

    def test_03_divergence_with_future_news_excluded(self):
        """Case 3 & 17 & Invariant 3: Future news at T+5 is excluded from T"""
        temp_db = "scratch/temp_test_03.duckdb"
        con = self._create_temp_db(temp_db)
        
        # Insert future news at T+5 days
        con.execute("""
            INSERT INTO fact_event (event_id, event_type, event_subtype, entity_id, entity_type,
                                   event_timestamp, published_at, information_available_at,
                                   observed_at, retrieved_at, raw_reference, is_pit_valid)
            VALUES ('EVT_NEWS_FUTURE', 'NEWS_INFORMATION', 'ARTICLE', 'ENT_ADRO', 'COMPANY',
                    '2026-01-20 00:00:00', '2026-01-20 00:00:00', '2026-01-20 00:00:00',
                    '2026-01-20 00:00:00', '2026-01-20 00:00:00', 'Post-facto merger disclosure', TRUE)
        """)
        con.close()
        
        eng = CandidateAttributionEngine(temp_db)
        row = {
            "symbol": "ADRO",
            "date": "2026-01-15T00:00:00+0700",
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.0
        }
        universe = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.01}
        ]
        res = eng.evaluate_candidate(row, universe)
        self.assertGreaterEqual(res.future_evidence_excluded_count, 1)
        self.assertEqual(res.evidence_coverage.news, CoverageState.NO_EVIDENCE_IN_DATASET)
        self.assertEqual(res.primary_attribution, "UNKNOWN_COMPONENT")
        
        if os.path.exists(temp_db):
            os.remove(temp_db)

    def test_04_divergence_during_broad_market_rally(self):
        """Case 4 & 7: Target +8%, Peers +1%, Market +6% -> Specificity COMPANY_SPECIFIC_CANDIDATE, Attribution MARKET_COMPONENT"""
        row = {
            "symbol": "ADRO",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.0
        }
        universe = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.01},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.06},
            {"symbol": "BBRI", "ret_c_prev_to_close": 0.06},
            {"symbol": "BMRI", "ret_c_prev_to_close": 0.06},
            {"symbol": "BBNI", "ret_c_prev_to_close": 0.06}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertEqual(res.primary_attribution, "MARKET_COMPONENT")
        self.assertEqual(res.causality_level, CausalityLevel.CORRELATED)

    def test_05_divergence_during_sector_wide_rally(self):
        """Case 5 & 23: Target +8%, Peers +7%, Market +1% -> SECTOR_WIDE specificity, SECTOR_COMPONENT attribution"""
        row = {
            "symbol": "ADRO",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.2
        }
        universe = [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.07},
            {"symbol": "PTBA", "ret_c_prev_to_close": 0.075},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.01}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.SECTOR_WIDE)
        self.assertEqual(res.primary_attribution, "SECTOR_COMPONENT")

    def test_06_target_underperforms_peers(self):
        """Case 6: Target -3%, Peers +4% -> COMPANY_SPECIFIC_CANDIDATE (negative divergence)"""
        row = {
            "symbol": "BBCA",
            "date": self.test_date,
            "signal_state": "EARLY_WATCH",
            "quant_score": 60.0,
            "ret_c_prev_to_close": -0.03,
            "rel_vol": 1.0
        }
        universe = [
            {"symbol": "BBCA", "ret_c_prev_to_close": -0.03},
            {"symbol": "BBNI", "ret_c_prev_to_close": 0.04},
            {"symbol": "BBRI", "ret_c_prev_to_close": 0.04},
            {"symbol": "BMRI", "ret_c_prev_to_close": 0.04}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertAlmostEqual(res.peer_reaction.differential_return, -0.07, places=3)

    def test_08_commodity_and_macro_confounding(self):
        """Case 8: Gold/Nickel target with high market mean triggers confounding check"""
        row = {
            "symbol": "ANTM",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.07,
            "rel_vol": 1.1
        }
        universe = [
            {"symbol": "ANTM", "ret_c_prev_to_close": 0.07},
            {"symbol": "INCO", "ret_c_prev_to_close": 0.01},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.04},
            {"symbol": "BBRI", "ret_c_prev_to_close": 0.04},
            {"symbol": "BMRI", "ret_c_prev_to_close": 0.04},
            {"symbol": "BBNI", "ret_c_prev_to_close": 0.04}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE)
        self.assertEqual(res.red_team_audit.alternative_explanation, "WEAK")
        self.assertTrue(any("Confounding" in r for r in res.red_team_audit.reasons))

    # --- RED TEAM ADVERSARIAL CHECKS ---

    def test_09_ownership_claim_without_evidence_flagged(self):
        """Case 9 & Invariant 2: Ownership/fundamentals without records remain NO_EVIDENCE_IN_DATASET"""
        row = {
            "symbol": "TLKM",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 75.0,
            "ret_c_prev_to_close": 0.01
        }
        res = self.engine.evaluate_candidate(row, [{"symbol": "TLKM", "ret_c_prev_to_close": 0.01}])
        self.assertEqual(res.evidence_coverage.ownership, CoverageState.NO_EVIDENCE_IN_DATASET)
        self.assertEqual(res.evidence_coverage.fundamental, CoverageState.NO_EVIDENCE_IN_DATASET)
        self.assertEqual(res.evidence_coverage.policy, CoverageState.NO_EVIDENCE_IN_DATASET)
        self.assertEqual(res.evidence_coverage.relationship, CoverageState.NOT_AVAILABLE)

    def test_13_contradictory_evidence_tracking(self):
        """Case 13: Contradictory evidence in DuckDB event graph increments counter"""
        temp_db = "scratch/temp_test_13.duckdb"
        con = self._create_temp_db(temp_db)
        
        con.execute("""
            INSERT INTO fact_event (event_id, event_type, event_subtype, entity_id, entity_type,
                                   event_timestamp, published_at, information_available_at,
                                   observed_at, retrieved_at, raw_reference, supersedes_event_id, contradicts_event_id, is_pit_valid)
            VALUES ('EVT_CONTRADICT', 'NEWS_INFORMATION', 'ARTICLE', 'ENT_BBCA', 'COMPANY',
                    '2026-01-15 00:00:00', '2026-01-15 00:00:00', '2026-01-15 00:00:00',
                    '2026-01-15 00:00:00', '2026-01-15 00:00:00', 'Denial of acquisition rumors', NULL, 'EVT_PRIOR', TRUE)
        """)
        con.close()
        
        eng = CandidateAttributionEngine(temp_db)
        row = {"symbol": "BBCA", "date": "2026-01-15T00:00:00+0700", "signal_state": "WATCH", "quant_score": 80.0, "ret_c_prev_to_close": 0.01}
        res = eng.evaluate_candidate(row, [{"symbol": "BBCA", "ret_c_prev_to_close": 0.01}])
        self.assertGreaterEqual(res.contradictory_evidence_count, 1)
        
        if os.path.exists(temp_db):
            os.remove(temp_db)

    def test_14_future_ownership_relationship_exposure_injections(self):
        """Case 14, 15, 16: Future relationship valid_from > T is excluded at T"""
        temp_db = "scratch/temp_test_14.duckdb"
        con = self._create_temp_db(temp_db)
        
        # Inject future relationship valid from 2026-06-01
        con.execute("""
            INSERT INTO fact_relationship (relationship_id, entity_a_id, entity_b_id, relationship_type,
                                          valid_from, valid_to, observed_at, confidence, pit_status)
            VALUES ('REL_FUTURE_01', 'ENT_TLKM', 'ENT_BBCA', 'PARTNERSHIP',
                    '2026-06-01 00:00:00', NULL, '2026-01-15 00:00:00', 0.95, 'VALID')
        """)
        con.close()
        
        eng = CandidateAttributionEngine(temp_db)
        # Query on 2026-01-15
        row = {"symbol": "TLKM", "date": "2026-01-15T00:00:00+0700", "signal_state": "WATCH", "quant_score": 75.0, "ret_c_prev_to_close": 0.01}
        res = eng.evaluate_candidate(row, [{"symbol": "TLKM", "ret_c_prev_to_close": 0.01}])
        self.assertEqual(res.relationship_status, CoverageState.NOT_AVAILABLE)
        
        if os.path.exists(temp_db):
            os.remove(temp_db)

    def test_24_market_wide_with_large_target_return(self):
        """Case 24: Target +8%, Market +7% across entire multi-sector universe -> Specificity MARKET_WIDE, Attribution MARKET_COMPONENT"""
        row = {
            "symbol": "TLKM",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.2
        }
        universe = [
            {"symbol": "TLKM", "ret_c_prev_to_close": 0.08},
            {"symbol": "BBCA", "ret_c_prev_to_close": 0.075},
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.078},
            {"symbol": "ASII", "ret_c_prev_to_close": 0.072}
        ]
        res = self.engine.evaluate_candidate(row, universe)
        self.assertEqual(res.specificity_status, SpecificityStatus.MARKET_WIDE)
        self.assertEqual(res.primary_attribution, "MARKET_COMPONENT")

    def test_25_missing_peer_data_fallback(self):
        """Case 25 & 26: Candidate with no peers or single universe falls back gracefully"""
        row = {
            "symbol": "TLKM",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 70.0,
            "ret_c_prev_to_close": 0.01
        }
        res = self.engine.evaluate_candidate(row, [{"symbol": "TLKM", "ret_c_prev_to_close": 0.01}])
        self.assertEqual(res.peer_reaction.peer_count, 0)
        self.assertIn(res.specificity_status, [SpecificityStatus.UNKNOWN, SpecificityStatus.MARKET_WIDE, SpecificityStatus.COMPANY_SPECIFIC_CANDIDATE])

    def test_27_unknown_entity_handling(self):
        """Case 27: Unknown entity symbol produces safe UNKNOWN entity_status without crashing"""
        row = {
            "symbol": "XYZW",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 50.0,
            "ret_c_prev_to_close": 0.01
        }
        res = self.engine.evaluate_candidate(row, [{"symbol": "XYZW", "ret_c_prev_to_close": 0.01}])
        self.assertEqual(res.entity_status, CoverageState.NOT_AVAILABLE)
        self.assertEqual(res.primary_attribution, "UNKNOWN_COMPONENT")

    def test_30_red_team_rejection_and_downgrade(self):
        """Invariant 9 & 10: Red Team 4-dimension audit properly aggregates status and prevents overclaiming"""
        # When primary attribution is UNKNOWN_COMPONENT, Red Team status is WEAK with INSUFFICIENT_EVIDENCE
        row = {
            "symbol": "ADRO",
            "date": self.test_date,
            "signal_state": "WATCH",
            "quant_score": 85.0,
            "ret_c_prev_to_close": 0.08,
            "rel_vol": 1.0
        }
        res = self.engine.evaluate_candidate(row, [
            {"symbol": "ADRO", "ret_c_prev_to_close": 0.08},
            {"symbol": "ITMG", "ret_c_prev_to_close": 0.01}
        ])
        self.assertEqual(res.red_team_status, RedTeamStatus.WEAK)
        self.assertEqual(res.red_team_audit.alternative_explanation, "INSUFFICIENT_EVIDENCE")
        self.assertEqual(res.red_team_audit.evidence_hallucination, "PASS")

if __name__ == '__main__':
    unittest.main()

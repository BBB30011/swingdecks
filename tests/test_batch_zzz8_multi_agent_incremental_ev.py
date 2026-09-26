import unittest
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.multi_agent_experiment_engine import MultiAgentExperimentEngine

class TestBatchZZZ8MultiAgentIncrementalEV(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        df62 = pd.read_parquet("gates/evidence/zzz62_observations.parquet")
        df71 = pd.read_parquet("gates/evidence/zzz71_candidate_attributions.parquet")
        merge_cols = [c for c in df71.columns if c not in df62.columns or c in ["symbol", "date"]]
        cls.df_merged = pd.merge(df62, df71[merge_cols], on=["symbol", "date"], how="inner")
        cls.engine = MultiAgentExperimentEngine(cls.df_merged, random_seed=42)
        cls.df_evaluated = cls.engine.evaluate_layers()
        cls.metrics = cls.engine.compute_layer_metrics()
        cls.incremental = cls.engine.compute_incremental_ev(cls.metrics)

    def test_01_layer_isolation_and_selection_monotony(self):
        """Test that selection counts monotonically narrow across the funnel: Baseline >= A >= B >= C >= D >= E"""
        n_base = self.metrics["Baseline"]["n"]
        n_a = self.metrics["Layer_A"]["n"]
        n_b = self.metrics["Layer_B"]["n"]
        n_c = self.metrics["Layer_C"]["n"]
        n_d = self.metrics["Layer_D"]["n"]
        n_e = self.metrics["Layer_E"]["n"]
        
        self.assertEqual(n_base, 1242)
        self.assertGreaterEqual(n_base, n_a)
        self.assertGreaterEqual(n_a, n_b)
        self.assertGreaterEqual(n_b, n_c)
        self.assertGreaterEqual(n_c, n_d)
        self.assertGreaterEqual(n_d, n_e)
        self.assertEqual(n_e, 73)

    def test_02_baseline_reproducibility(self):
        """Test that Layer 0 reproduces exact 1,242 signals matching ZZZ.6.2 and ZZZ.7.1"""
        sel_base = self.df_evaluated["sel_baseline"]
        self.assertEqual(int(sel_base.sum()), 1242)
        # All controls must be unselected
        ctrl_count = int((~sel_base).sum())
        self.assertEqual(ctrl_count, 1758)

    def test_03_no_future_data_leakage(self):
        """Test that selection masks do not depend on forward returns (H1..H20)"""
        # Scramble forward returns in a test copy and verify selection masks are identical
        scrambled_df = self.df_merged.copy()
        for h in ["H1", "H3", "H5", "H10", "H20"]:
            scrambled_df[h] = np.random.permutation(scrambled_df[h].values)
            
        test_engine = MultiAgentExperimentEngine(scrambled_df, random_seed=42)
        eval_scrambled = test_engine.evaluate_layers()
        
        for col in ["sel_baseline", "sel_layer_a", "sel_layer_b", "sel_layer_c", "sel_layer_d", "sel_layer_e"]:
            pd.testing.assert_series_equal(self.df_evaluated[col], eval_scrambled[col])

    def test_04_peer_context_boundary(self):
        """Test that Layer A correctly filters solitary tickers without contextual peers (TLKM)"""
        tlkm_df = self.df_evaluated[self.df_evaluated["symbol"] == "TLKM"]
        tlkm_signals = tlkm_df[tlkm_df["sel_baseline"]]
        # TLKM has peer_count == 0 in 12-pilot universe
        self.assertTrue((tlkm_signals["peer_count"] == 0).all())
        self.assertEqual(int(tlkm_signals["sel_layer_a"].sum()), 0)

    def test_05_differential_intelligence_filtering(self):
        """Test that Layer B selects strictly SECTOR_WIDE alignment and rejects isolated divergence"""
        layer_b_df = self.df_evaluated[self.df_evaluated["sel_layer_b"]]
        self.assertTrue((layer_b_df["specificity_status"] == "SECTOR_WIDE").all())
        self.assertFalse((layer_b_df["specificity_status"] == "COMPANY_SPECIFIC_CANDIDATE").any())
        self.assertEqual(len(layer_b_df), 252)

    def test_06_red_team_gating(self):
        """Test that Layer C enforces zero time leakage and zero logic contradictions"""
        layer_c_df = self.df_evaluated[self.df_evaluated["sel_layer_c"]]
        self.assertTrue((layer_c_df["red_team_time_leakage"] == "PASS").all())
        self.assertTrue((layer_c_df["red_team_logic_consistency"] == "PASS").all())
        self.assertTrue((layer_c_df["red_team_evidence_hallucination"] != "FAIL").all())

    def test_07_agent3_risk_reward_gating(self):
        """Test that Layer D and E enforce Agent 3 risk state and Opportunity Ranking"""
        layer_d_df = self.df_evaluated[self.df_evaluated["sel_layer_d"]]
        layer_e_df = self.df_evaluated[self.df_evaluated["sel_layer_e"]]
        self.assertTrue((layer_d_df["agent3_action"] == "BUY").all())
        self.assertTrue((layer_e_df["opportunity_score"] >= 60.0).all())
        self.assertEqual(len(layer_e_df), 73)

    def test_08_incremental_ev_calculation(self):
        """Test that Incremental EV matches step-by-step and full difference formulas"""
        full_ev = self.incremental["full_incremental_ev"]
        base_h5 = self.metrics["Baseline"]["horizons"]["H5"]["mean"]
        e_h5 = self.metrics["Layer_E"]["horizons"]["H5"]["mean"]
        self.assertAlmostEqual(full_ev["H5"], e_h5 - base_h5, places=6)
        self.assertGreater(full_ev["H5"], 0.01) # Positive incremental EV > +1.0%

    def test_09_bootstrap_validation_robustness(self):
        """Test that bootstrap validation produces valid non-null confidence intervals and p-values"""
        boot = self.engine.run_bootstrap_validation(n_iterations=500)
        for h in ["H1", "H3", "H5", "H10", "H20"]:
            res = boot["iid_bootstrap"][h]
            self.assertFalse(np.isnan(res["ci_lower"]))
            self.assertFalse(np.isnan(res["ci_upper"]))
            self.assertLessEqual(res["ci_lower"], res["ci_upper"])
            self.assertGreaterEqual(res["p_value"], 0.0)
            self.assertLessEqual(res["p_value"], 1.0)

if __name__ == '__main__':
    unittest.main()

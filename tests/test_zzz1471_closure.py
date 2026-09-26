"""
tests/test_zzz1471_closure.py

Targeted unit test suite for Batch ZZZ.14.7.1:
One-Shot Numerical, Estimand & Inference Closure Gate.
Contains 30 comprehensive automated tests validating:
1. Exact observation matrix population (N=1,760, N_treat=161, N_ctrl=1,599).
2. X_PRE_T vs Y_OUTCOME strict partition boundary.
3. Estimator identities for Effects A, B, and C.
4. Primary Estimand (ATT_INFO_161_REGRESSION_BETA) selection.
5. Standard errors, properly centered confidence intervals, and p-values.
6. Support distance distribution (d_min) and BROAD_SUPPORT_SCREEN_PASS.
7. Coverage adjustment non-attenuation (COVERAGE_EFFECT_SURVIVAL).
8. Placebo reconciliation under both regression and difference-in-means estimators.
9. 65.2% Information Enrichment vs Genuine Semantic Novelty decomposition.
10. Temporal partitions (Dev, Val, OOS) directional consistency.
11. 20 Targeted Red Team attacks (100% PASS).
12. Single-Source-of-Truth Canonical Inference JSON schema.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz1471_closure_engine import ZZZ1471ClosureEngine


@pytest.fixture(scope="module")
def closure_engine():
    return ZZZ1471ClosureEngine()


@pytest.fixture(scope="module")
def closure_execution(closure_engine):
    manifest = closure_engine.run_full_closure_gate()
    json_path = manifest["canonical_inference_json"]
    with open(json_path, "r") as f:
        canon_json = json.load(f)
    return manifest, canon_json


# 1. Exact Population Shape (N=1,760)
def test_observation_matrix_shape(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, summary = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert len(df_obs) == 1760
    assert summary["total_observations"] == 1760


# 2. Exact Contradiction Population (N=161)
def test_contradiction_treatment_count(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, summary = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert summary["treatment_count"] == 161
    assert int(df_obs["contradiction_indicator"].sum()) == 161


# 3. Exact Non-Contradiction Population (N=1,599)
def test_control_population_count(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, summary = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert summary["control_count"] == 1599
    assert int((1 - df_obs["contradiction_indicator"]).sum()) == 1599


# 4. Strict Partition Integrity
def test_partition_integrity(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    _, summary = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert summary["partition_integrity"] == "STRICT_X_PRE_T_VS_Y_OUTCOME_SEPARATION"


# 5. Effect A Numerical Identity (Model 4 Beta = -2.8622 pp)
def test_effect_a_numerical_identity(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_a = df_recon[df_recon["effect_id"] == "EFFECT_A_NESTED_MODEL_4_BETA"].iloc[0]
    assert np.isclose(eff_a["effect_pp"], -2.8622, atol=0.001)
    assert eff_a["status"] == "PRIMARY_CANONICAL_ESTIMAND"


# 6. Effect B Numerical Identity (Diff in Means = -2.7462 pp)
def test_effect_b_numerical_identity(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_b = df_recon[df_recon["effect_id"] == "EFFECT_B_UNADJUSTED_DIFF_IN_MEANS"].iloc[0]
    assert np.isclose(eff_b["effect_pp"], -2.7462, atol=0.001)


# 7. Effect C Numerical Identity (Coverage Adjusted Beta = -2.7988 pp)
def test_effect_c_numerical_identity(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_c = df_recon[df_recon["effect_id"] == "EFFECT_C_COVERAGE_ADJUSTED_BETA"].iloc[0]
    assert np.isclose(eff_c["effect_pp"], -2.7988, atol=0.001)


# 8. Primary Estimand Standard Error Date Clustering (SE = 0.1522 pp)
def test_primary_estimand_se_date_clustered(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_a = df_recon[df_recon["effect_id"] == "EFFECT_A_NESTED_MODEL_4_BETA"].iloc[0]
    assert np.isclose(eff_a["se_date_clustered"], 0.1522, atol=0.001)


# 9. Confidence Interval Proper Centering
def test_confidence_interval_properly_centered(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_a = df_recon[df_recon["effect_id"] == "EFFECT_A_NESTED_MODEL_4_BETA"].iloc[0]
    ci95 = eff_a["ci95_date_clustered"]
    midpoint = (ci95[0] + ci95[1]) / 2.0
    assert np.isclose(midpoint, eff_a["effect_pp"], atol=0.001)
    assert ci95[0] < eff_a["effect_pp"] < ci95[1]


# 10. Primary Estimand P-Value
def test_primary_estimand_p_value(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_recon, _ = closure_engine.reconcile_three_effects(df_obs)
    eff_a = df_recon[df_recon["effect_id"] == "EFFECT_A_NESTED_MODEL_4_BETA"].iloc[0]
    assert eff_a["p_value"] < 0.0001


# 11. Support Distance (d_min) Distribution Bounds
def test_support_distance_distribution(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    _, summary = closure_engine.compute_support_and_attenuation(df_obs)
    assert summary["min"] >= 0.40
    assert summary["max"] <= 2.20
    assert summary["max"] <= summary["caliper_screen"]
    assert summary["pass_rate_pct"] == 100.0


# 12. Support Classification Status
def test_support_classification_status(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    _, summary = closure_engine.compute_support_and_attenuation(df_obs)
    assert summary["common_support_classification"] == "BROAD_SUPPORT_SCREEN_PASS"


# 13. Coverage Effect Survival (Non-Attenuation)
def test_coverage_effect_survival(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    _, summary = closure_engine.compute_support_and_attenuation(df_obs)
    assert "PASS" in summary["coverage_effect_survival"]
    assert summary["adjusted_effect_pp"] < summary["unadjusted_effect_pp"]


# 14. Placebos Under Difference-in-Means
def test_placebos_under_diff_in_means(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_placebo, _ = closure_engine.reconcile_placebos_and_novelty(df_obs)
    for _, row in df_placebo.iterrows():
        if row["probe_id"] == "P7_FUTURE_EVIDENCE_SENTINEL":
            assert row["diff_in_means_effect_pp"] == 0.0
        else:
            assert abs(row["diff_in_means_effect_pp"]) < 0.35


# 15. Placebos Under Model 4 Regression
def test_placebos_under_regression(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_placebo, _ = closure_engine.reconcile_placebos_and_novelty(df_obs)
    for _, row in df_placebo.iterrows():
        if row["probe_id"] == "P7_FUTURE_EVIDENCE_SENTINEL":
            assert row["model_4_regression_beta_pp"] == 0.0
        else:
            assert abs(row["model_4_regression_beta_pp"]) < 0.35


# 16. Placebo P7 Strict Blocking Under Both Estimators
def test_placebo_p7_strict_blocking_both(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_placebo, _ = closure_engine.reconcile_placebos_and_novelty(df_obs)
    p7 = df_placebo[df_placebo["probe_id"] == "P7_FUTURE_EVIDENCE_SENTINEL"].iloc[0]
    assert p7["diff_in_means_effect_pp"] == 0.0
    assert p7["model_4_regression_beta_pp"] == 0.0
    assert p7["status"] == "STRICTLY_BLOCKED"


# 17. Information Enrichment Denominator (1,147 / 1,760 = 65.17%)
def test_information_enrichment_denominator(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    _, summary = closure_engine.reconcile_placebos_and_novelty(df_obs)
    assert summary["information_enrichment_numerator"] == 1147
    assert summary["information_enrichment_denominator"] == 1760
    assert np.isclose(summary["information_enrichment_pct"], 65.17, atol=0.05)


# 18. Genuine Qualitative Novelty Separation
def test_genuine_qualitative_novelty_separation(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    _, summary = closure_engine.reconcile_placebos_and_novelty(df_obs)
    assert summary["genuine_novel_semantic_pct"] == 18.18
    assert summary["operational_refinement_pct"] == 38.58
    assert summary["deterministic_confirmation_pct"] == 32.39
    assert "ENRICHMENT_IS_NOT_NOVELTY" in summary["novelty_reconciliation_verdict"]


# 19. Temporal Partitions Completeness
def test_temporal_partitions_completeness(closure_execution):
    _, canon_json = closure_execution
    partitions = canon_json["temporal_generalization"]
    assert len(partitions) == 3
    total_n = sum(p["total_setups"] for p in partitions)
    assert total_n == 1760


# 20. Temporal Partitions Directional Consistency
def test_temporal_partitions_directional_consistency(closure_execution):
    _, canon_json = closure_execution
    partitions = canon_json["temporal_generalization"]
    for p in partitions:
        assert p["effect_pp"] < -2.0
        assert p["status"] == "CONSISTENT"


# 21. 20 Red Team Attacks Execution & 100% Pass Rate
def test_20_red_team_attacks_pass(closure_engine):
    df_red = closure_engine.execute_20_targeted_red_team_attacks()
    assert len(df_red) == 20
    assert (df_red["status"] == "PASS").all()


# 22. Red Team Attack 1: Beta Substitution
def test_red_team_attack_01(closure_engine):
    df_red = closure_engine.execute_20_targeted_red_team_attacks()
    att = df_red[df_red["attack_id"] == "ATTACK_01_BETA_SUBSTITUTION"].iloc[0]
    assert att["status"] == "PASS"


# 23. Red Team Attack 3: CI Substitution
def test_red_team_attack_03(closure_engine):
    df_red = closure_engine.execute_20_targeted_red_team_attacks()
    att = df_red[df_red["attack_id"] == "ATTACK_03_CI_SUBSTITUTION"].iloc[0]
    assert att["status"] == "PASS"


# 24. Red Team Attack 7: ATT / Regression Confusion
def test_red_team_attack_07(closure_engine):
    df_red = closure_engine.execute_20_targeted_red_team_attacks()
    att = df_red[df_red["attack_id"] == "ATTACK_07_ATT_REGRESSION_CONFUSION"].iloc[0]
    assert att["status"] == "PASS"


# 25. Red Team Attack 17: Semantic Novelty Inflation
def test_red_team_attack_17(closure_engine):
    df_red = closure_engine.execute_20_targeted_red_team_attacks()
    att = df_red[df_red["attack_id"] == "ATTACK_17_SEMANTIC_NOVELTY_INFLATION"].iloc[0]
    assert att["status"] == "PASS"


# 26. Canonical Inference JSON Schema Verification
def test_canonical_inference_json_schema(closure_execution):
    _, canon_json = closure_execution
    required_keys = [
        "gate_id", "title", "timestamp", "governance_lock",
        "reconciliation_of_effects", "primary_estimand", "alternative_estimands",
        "common_support_metrics", "placebo_reconciliation", "semantic_novelty_reconciliation",
        "temporal_generalization", "red_team_audit", "final_classifications"
    ]
    for k in required_keys:
        assert k in canon_json, f"Missing key in canonical inference json: {k}"


# 27. Primary Estimand Field Consistency in JSON
def test_primary_estimand_json_fields(closure_execution):
    _, canon_json = closure_execution
    prim = canon_json["primary_estimand"]
    assert prim["estimand_id"] == "ATT_INFO_161_REGRESSION_BETA"
    assert prim["canonical_effect_pp"] == -2.8622
    assert prim["canonical_se_date_clustered_pp"] == 0.1522
    assert prim["canonical_ci95_date_clustered_pp"] == [-3.1605, -2.5639]
    assert prim["canonical_p_value"] == 0.0


# 28. Final Classifications Closing Block Matching
def test_final_classifications_closing_block(closure_execution):
    _, canon_json = closure_execution
    fc = canon_json["final_classifications"]
    assert fc["DATASET"] == "DATASET_V2_20260915"
    assert fc["SETUP_POPULATION"] == "N_1760"
    assert fc["CANONICAL_CONTRADICTION_POPULATION"] == "N_161"
    assert fc["PRIMARY_OUTCOME"] == "H5_PEER_EXCESS"
    assert fc["PRIMARY_ESTIMAND"] == "ATT_INFO_161_REGRESSION_BETA"
    assert fc["PRIMARY_EFFECT"] == "-2.8622 pp"
    assert fc["PRIMARY_SE"] == "0.1522 pp"
    assert fc["PRIMARY_CI95"] == "[-3.1605, -2.5639] pp"
    assert fc["PRIMARY_P"] == "< 0.0001"
    assert fc["NUMERICAL_RECONCILIATION"] == "PASS"
    assert fc["ESTIMAND_IDENTITY"] == "EXACT"
    assert fc["INFERENCE_ROBUSTNESS"] == "ROBUST"
    assert fc["COMMON_SUPPORT_STATUS"] == "BROAD_SUPPORT_SCREEN_PASS"
    assert fc["COVERAGE_EFFECT_SURVIVAL"] == "PASS"
    assert fc["INFORMATION_NOVELTY"] == "OBSERVED"
    assert fc["INCREMENTAL_INFORMATION"] == "OBSERVED"
    assert fc["INCREMENTAL_DISCRIMINATION"] == "OBSERVED"
    assert fc["TEMPORAL_GENERALIZATION"] == "SUPPORTED"
    assert fc["CAUSALITY"] == "NOT_PROVEN"
    assert fc["STANDALONE_ALPHA"] == "NOT_PROVEN"
    assert fc["STRATEGY_OPTIMIZATION"] == "BLOCKED"
    assert fc["STRATEGY_READINESS"] == "NOT_READY"
    assert fc["REPRODUCIBILITY"] == "PASS"
    assert fc["RED_TEAM"] == "PASS"
    assert fc["SCIENTIFIC_FIREWALL"] == "PASS"
    assert fc["ZZZ_14_8_STATUS"] == "ELIGIBLE"
    assert fc["FINAL_CLASSIFICATION"] == "INCREMENTAL_DISCRIMINATION_OBSERVED_CAUSAL_ALPHA_NOT_PROVEN"


# 29. Zero NaN Values in Canonical Observation Matrix
def test_zero_nan_in_observation_matrix(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs, _ = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert not df_obs.isna().any().any()


# 30. Dual-Run Cryptographic Reproducibility
def test_dual_run_reproducibility(closure_engine):
    df_ladder = closure_engine.load_canonical_data()
    df_obs1, s1 = closure_engine.build_canonical_observation_matrix(df_ladder)
    df_obs2, s2 = closure_engine.build_canonical_observation_matrix(df_ladder)
    assert s1["sha256_hash"] == s2["sha256_hash"]
    pd.testing.assert_frame_equal(df_obs1, df_obs2)

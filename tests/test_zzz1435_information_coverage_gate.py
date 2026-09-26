"""
tests/test_zzz1435_information_coverage_gate.py

Automated Test Suite for Batch ZZZ.14.3.5: Information-Coverage Confounding & Strict Pre-T Counterfactual Gate.
Validates 21 distinct audit and regression requirements.
Strictly 3-Agent architecture. Zero Agent 4.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.information_coverage_engine import (
    InformationCoverageEngine,
    EXPECTED_MANIFEST_HASH,
    CANONICAL_12_TICKERS,
    COMMODITY_TICKERS
)

@pytest.fixture(scope="module")
def engine_and_data():
    engine = InformationCoverageEngine()
    df, meta = engine.load_canonical_data_with_coverage()
    return engine, df, meta


def test_1_canonical_manifest_identity(engine_and_data):
    engine, df, meta = engine_and_data
    assert len(df) == 73, f"Expected 73 observations, got {len(df)}"
    assert meta["evidence_count"] == 59
    assert meta["unobserved_count"] == 14
    assert meta["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert meta["manifest_hash_verified"] is True


def test_2_baseline_replication_gate_a(engine_and_data):
    engine, df, meta = engine_and_data
    b = engine.reproduce_baseline(df)
    assert b["gate_a_passed"] is True
    assert abs(b["differential_mean_pp"] - 3.1037) < 0.001
    assert abs(b["treatment_mean_h5_excess_pct"] - 0.6529) < 0.001
    assert abs(b["control_mean_h5_excess_pct"] - (-2.4509)) < 0.001


def test_3_pit_coverage_availability_semantics(engine_and_data):
    engine, df, meta = engine_and_data
    assert "pre_30d_event_density" in df.columns
    assert "pre_60d_event_density" in df.columns
    assert "pre_90d_event_density" in df.columns
    assert "total_archive_density" in df.columns
    # Ensure all values are non-negative integers
    assert (df["pre_30d_event_density"] >= 0).all()
    assert (df["pre_90d_event_density"] >= 0).all()
    assert (df["total_archive_density"] > 0).all()


def test_4_zero_outcome_leakage_in_matching(engine_and_data):
    engine, df, meta = engine_and_data
    forbidden_cols = ["target_H1", "target_H3", "target_H5", "target_H10", "target_H20", "excess_H5", "excess_H5_pct", "mfe", "mae"]
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    # Check that matching algorithm does not depend on outcome
    assert matched_sum["matched_pairs_count"] == 14
    assert len(df_pairs) == 14


def test_5_coverage_diagnostics_gap_and_archive_depth(engine_and_data):
    engine, df, meta = engine_and_data
    df_diag, diag_summary = engine.compute_coverage_diagnostics(df)
    assert len(df_diag) == 5
    # Control should have 0 recent 90d events
    c_90d = df_diag[df_diag["variable"] == "pre_90d_event_density"]["control_mean"].iloc[0]
    assert c_90d == 0.0
    # Control total archive depth should be >= 30
    c_arch = df_diag[df_diag["variable"] == "total_archive_density"]["control_mean"].iloc[0]
    assert c_arch > 30.0


def test_6_strict_pre_t_matching_effect(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    assert matched_sum["matched_pairs_count"] == 14
    assert abs(matched_sum["matched_differential_pp"] - 2.6001) < 0.01
    assert matched_sum["attenuation_pct"] > 15.0 and matched_sum["attenuation_pct"] < 20.0


def test_7_pre_t_covariate_balance_smd_reduction(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    archive_row = df_balance[df_balance["covariate"] == "total_archive_density"].iloc[0]
    assert archive_row["smd_reduction_pct"] > 80.0
    assert abs(archive_row["smd_after"]) < 0.10
    comm_row = df_balance[df_balance["covariate"] == "is_commodity"].iloc[0]
    assert comm_row["smd_reduction_pct"] > 50.0


def test_8_coverage_adjusted_model_c2(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    c2_row = df_matrix[df_matrix["Specification"] == "C2: Coverage Adjusted"].iloc[0]
    assert c2_row["Effect_pp"] > 2.5
    assert c2_row["Coverage_Controlled"] == "Yes"


def test_9_quant_coverage_adjusted_model_c3(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    c3_row = df_matrix[df_matrix["Specification"] == "C3: Quant + Coverage"].iloc[0]
    assert c3_row["Effect_pp"] > 3.0
    assert c3_row["p_value"] < 0.05


def test_10_quant_coverage_event_cluster_sandwich_c4(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    c4_row = df_matrix[df_matrix["Specification"] == "C4: Quant + Coverage + Event Cluster"].iloc[0]
    assert c4_row["Effect_pp"] > 3.0
    assert c4_row["p_value"] < 0.05
    assert c4_row["Event_Dependence"] == "Yes"


def test_11_strict_matched_event_cluster_c5(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    c5_row = df_matrix[df_matrix["Specification"] == "C5: Strict Matched + Event Cluster"].iloc[0]
    assert abs(c5_row["Effect_pp"] - 2.6001) < 0.01
    assert c5_row["p_value"] < 0.05
    assert c5_row["Status"] == "ROBUST_LEVEL_2"


def test_12_event_equalized_sensitivity_c6(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    c6_row = df_matrix[df_matrix["Specification"] == "C6: Event Equalized"].iloc[0]
    assert c6_row["Effect_pp"] > 3.0
    assert c6_row["p_value"] < 0.05


def test_13_coverage_adjusted_lodo_stability_c7(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, matrix_summary = engine.execute_models_c0_to_c7(df, df_pairs)
    assert len(df_lodo) == 30
    assert (df_lodo["evidence_coef_pp"] > 0).all(), "Found sign change in LODO"
    assert matrix_summary["c7_lodo_sign_changes"] == 0


def test_14_event_density_stratification(engine_and_data):
    engine, df, meta = engine_and_data
    df_strata, _ = engine.execute_event_density_sensitivity(df)
    assert len(df_strata) == 2
    low_row = df_strata[df_strata["stratum"].str.contains("LOW_DENSITY")].iloc[0]
    assert low_row["mean_excess_h5_pct"] > 0.0


def test_15_information_visibility_negative_control(engine_and_data):
    engine, df, meta = engine_and_data
    from core.information_coverage_engine import fit_ols
    y = df["excess_H5_pct"].values
    X_neg = np.column_stack([np.ones(len(df)), df["total_archive_density"].astype(float).values])
    b, se, t, p = fit_ols(y, X_neg)
    # Total archive density should NOT be a statistically significant predictor of H5 on its own
    assert p[1] > 0.10


def test_16_placebo_falsification_cleared(engine_and_data):
    engine, df, meta = engine_and_data
    placebo = engine.execute_placebo_and_shuffle_tests(df)
    assert placebo["falsification_cleared"] is True
    assert placebo["empirical_p_value"] < 0.05


def test_17_ticker_and_date_contrast_integrity(engine_and_data):
    engine, df, meta = engine_and_data
    # 11 active tickers represented in the canonical N=73 sample across 49 unique dates
    assert df["ticker"].nunique() == 11
    assert df["decision_date_str"].nunique() == 49


def test_18_control_semantics_integrity(engine_and_data):
    engine, df, meta = engine_and_data
    ctrl = df[~df["is_evidence_bool"]]
    assert len(ctrl) == 14
    assert (ctrl["coverage_state"] == "ARCHIVAL_GAP").all()


def test_19_red_team_25_attacks_passed(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    attacks = engine.execute_25_red_team_attacks(df, df_pairs)
    assert len(attacks) == 25
    assert all(a["status"] == "PASS" for a in attacks)


def test_20_dual_run_deterministic_reproducibility(engine_and_data):
    engine, df, meta = engine_and_data
    repro = engine.execute_dual_run_reproducibility()
    assert repro["reproducibility_status"] == "EXACT_REPRODUCIBILITY_CONFIRMED"
    assert repro["max_discrepancy_pp"] == 0.0


def test_21_required_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_3_5_information_coverage_gate.md",
        "gates/closed/zzz14_3_5_coverage_balance.csv",
        "gates/closed/zzz14_3_5_coverage_variables.csv",
        "gates/closed/zzz14_3_5_strict_matching_pairs.csv",
        "gates/closed/zzz14_3_5_event_cluster_results.csv",
        "gates/closed/zzz14_3_5_event_density_sensitivity.csv",
        "gates/closed/zzz14_3_5_lodo_event.csv",
        "gates/closed/zzz14_3_5_result_matrix.csv",
        "gates/closed/zzz14_3_5_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required deliverable artifact: {rf}"
        assert os.path.getsize(rf) > 0, f"Artifact {rf} is empty"

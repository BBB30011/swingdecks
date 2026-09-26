"""
tests/test_zzz1436_strict_counterfactual_inference.py

Automated Test Suite for Batch ZZZ.14.3.6: Strict Information-Environment Counterfactual & Inference Reconciliation Gate.
Validates 25 distinct audit, statistical, and regression requirements.
Strictly 3-Agent architecture. Zero Agent 4.
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.strict_counterfactual_inference_engine import (
    StrictCounterfactualInferenceEngine,
    EXPECTED_MANIFEST_HASH,
    CANONICAL_12_TICKERS,
    COMMODITY_TICKERS
)

@pytest.fixture(scope="module")
def engine_and_data():
    engine = StrictCounterfactualInferenceEngine()
    df, meta = engine.load_canonical_data_with_strict_exclusion()
    return engine, df, meta


def test_1_canonical_manifest_identity(engine_and_data):
    engine, df, meta = engine_and_data
    assert len(df) == 73, f"Expected 73 observations, got {len(df)}"
    assert meta["evidence_count"] == 59
    assert meta["unobserved_count"] == 14
    assert meta["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert meta["manifest_hash_verified"] is True


def test_2_treatment_control_reconciliation(engine_and_data):
    engine, df, meta = engine_and_data
    assert df["is_evidence_bool"].sum() == 59
    assert (~df["is_evidence_bool"]).sum() == 14


def test_3_baseline_floating_point_reconciliation(engine_and_data):
    engine, df, meta = engine_and_data
    rec = engine.reconcile_baseline_arithmetic(df)
    assert rec["gate_a_reconciliation_passed"] is True
    assert rec["absolute_delta_pp"] < rec["comparison_tolerance_pp"]
    assert abs(rec["differential_exact_pp"] - 3.1037) < 0.0001


def test_4_explicit_comparison_tolerance(engine_and_data):
    engine, df, meta = engine_and_data
    rec = engine.reconcile_baseline_arithmetic(df)
    assert rec["comparison_tolerance_pp"] == 1e-4
    assert rec["relative_delta_pct"] < 0.01


def test_5_pit_firewall_availability(engine_and_data):
    engine, df, meta = engine_and_data
    assert (df["pre_30d_event_density"] >= 0).all()
    assert (df["pre_90d_event_density"] >= 0).all()
    assert (df["total_archive_density"] > 0).all()


def test_6_treatment_self_exclusion_verified(engine_and_data):
    engine, df, meta = engine_and_data
    df_diag, diag_summary = engine.compute_information_environment_diagnostics(df)
    treat = df[df["is_evidence_bool"]]
    # Pre-90d event count with exclusion drops to ~1.02, pre-30d to ~0.41
    assert abs(treat["pre_90d_event_density"].mean() - 1.0169) < 0.001
    assert abs(treat["pre_30d_event_density"].mean() - 0.4068) < 0.001


def test_7_event_density_pit_bounds(engine_and_data):
    engine, df, meta = engine_and_data
    # 30d density must be <= 60d density <= 90d density for every setup
    assert (df["pre_30d_event_density"] <= df["pre_60d_event_density"]).all()
    assert (df["pre_60d_event_density"] <= df["pre_90d_event_density"]).all()


def test_8_coverage_variable_pit_integrity(engine_and_data):
    engine, df, meta = engine_and_data
    assert (df["total_archive_density"] >= df["pre_90d_event_density"]).all()


def test_9_matching_outcome_blindness(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    assert matched_sum["matched_pairs_count"] == 14
    assert len(df_pairs) == 14


def test_10_strict_covariate_balance_calculation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    archive_row = df_balance[df_balance["covariate"] == "total_archive_density"].iloc[0]
    assert archive_row["smd_reduction_pct"] > 70.0
    assert abs(archive_row["smd_after"]) < 0.25


def test_11_common_support_metrics(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    assert matched_sum["matched_pairs_count"] == 14
    assert matched_sum["treatment_unmatched_count"] == 45
    assert matched_sum["control_unmatched_count"] == 0


def test_12_model_r0_estimation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r0 = df_matrix[df_matrix["Spec"] == "R0: Raw Canonical Baseline"].iloc[0]
    assert abs(r0["Effect_pp"] - 3.1037) < 0.001


def test_13_model_r1_estimation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r1 = df_matrix[df_matrix["Spec"] == "R1: 14.3.4 Matched Baseline"].iloc[0]
    assert abs(r1["Effect_pp"] - 2.6001) < 0.01


def test_14_model_r2_estimation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r2 = df_matrix[df_matrix["Spec"] == "R2: Archive Adjusted"].iloc[0]
    assert r2["Effect_pp"] > 2.5


def test_15_model_r3_estimation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r3 = df_matrix[df_matrix["Spec"] == "R3: Recent Density Adjusted"].iloc[0]
    assert r3["Effect_pp"] > 3.5
    assert r3["p_value"] < 0.05


def test_16_model_r4_estimation(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r4 = df_matrix[df_matrix["Spec"] == "R4: Quant + Coverage"].iloc[0]
    assert r4["Effect_pp"] > 3.0


def test_17_model_r5_event_cluster_sandwich(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r5 = df_matrix[df_matrix["Spec"] == "R5: + Event-Aware Inference"].iloc[0]
    assert r5["Effect_pp"] > 3.0
    assert r5["p_value"] < 0.05


def test_18_model_r6_strict_matched_cluster(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r6 = df_matrix[df_matrix["Spec"] == "R6: Strict Matched + Event"].iloc[0]
    assert abs(r6["Effect_pp"] - 2.6001) < 0.01
    assert r6["p_value"] < 0.05


def test_19_model_r7_event_equalized(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    r7 = df_matrix[df_matrix["Spec"] == "R7: Event Equalized"].iloc[0]
    assert r7["Effect_pp"] > 3.0
    assert r7["p_value"] < 0.05


def test_20_model_r8_coverage_lodo_stability(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    assert len(df_lodo) == 30
    assert (df_lodo["evidence_coef_pp"] > 0).all()
    assert matrix_summary["r8_lodo_sign_changes"] == 0


def test_21_wild_cluster_bootstrap_execution(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    assert matrix_summary["wild_cluster_p_val_r5"] < 0.05
    # R6 on matched N=28 exhibits directionally robust bootstrap p-value < 0.10
    assert matrix_summary["wild_cluster_p_val_r6"] < 0.10


def test_22_inference_reconciliation_table_integrity(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    df_matrix, df_lodo, df_inference, matrix_summary = engine.execute_models_r0_to_r8(df, df_pairs)
    assert len(df_inference) == 6
    assert all(df_inference["Effect_pp"] > 2.0)


def test_23_red_team_35_attacks_passed(engine_and_data):
    engine, df, meta = engine_and_data
    df_pairs, df_balance, matched_sum = engine.execute_strict_pre_t_matching(df)
    attacks = engine.execute_35_red_team_attacks(df, df_pairs)
    assert len(attacks) == 35
    assert all(a["status"] == "PASS" for a in attacks)


def test_24_dual_run_deterministic_reproducibility(engine_and_data):
    engine, df, meta = engine_and_data
    repro = engine.execute_dual_run_reproducibility()
    assert repro["reproducibility_status"] == "EXACT_REPRODUCIBILITY_CONFIRMED"
    assert repro["max_discrepancy_pp"] == 0.0


def test_25_all_10_required_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_3_6_strict_counterfactual_inference_gate.md",
        "gates/closed/zzz14_3_6_information_environment.csv",
        "gates/closed/zzz14_3_6_pre_t_balance.csv",
        "gates/closed/zzz14_3_6_strict_matching_pairs.csv",
        "gates/closed/zzz14_3_6_event_cluster_inference.csv",
        "gates/closed/zzz14_3_6_event_equalized.csv",
        "gates/closed/zzz14_3_6_lodo.csv",
        "gates/closed/zzz14_3_6_inference_reconciliation.csv",
        "gates/closed/zzz14_3_6_result_matrix.csv",
        "gates/closed/zzz14_3_6_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required deliverable artifact: {rf}"
        assert os.path.getsize(rf) > 0, f"Artifact {rf} is empty"

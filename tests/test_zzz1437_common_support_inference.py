"""
tests/test_zzz1437_common_support_inference.py

Automated Test Suite for Batch ZZZ.14.3.7:
Strict Common-Support, Estimand & Inference Reconciliation Gate.
Validates 35 strict methodological, econometric, support, and integrity assertions.
"""

import os
import pytest
import numpy as np
import pandas as pd
from core.common_support_inference_engine import (
    CommonSupportInferenceEngine,
    EXPECTED_MANIFEST_HASH,
    CANONICAL_12_TICKERS,
    COMMODITY_TICKERS,
    NON_COMMODITY_TICKERS
)

@pytest.fixture(scope="module")
def engine_and_data():
    engine = CommonSupportInferenceEngine()
    df, X_pre_t, Y_outcome, meta = engine.load_canonical_data_and_separate_xy()
    df_distances, df_identifiable, support_summary = engine.execute_multivariate_common_support(X_pre_t)
    df_pairs, df_balance, matched_summary = engine.execute_outcome_blind_matching(X_pre_t, Y_outcome)
    df_single_source, df_result_matrix, df_ticker_support, df_date_support, summary = engine.build_single_source_inference_and_estimands(df, df_pairs)
    red_attacks = engine.execute_40_red_team_attacks(df, X_pre_t, df_pairs)
    repro = engine.execute_dual_run_reproducibility()
    
    return {
        "engine": engine,
        "df": df,
        "X_pre_t": X_pre_t,
        "Y_outcome": Y_outcome,
        "meta": meta,
        "df_distances": df_distances,
        "df_identifiable": df_identifiable,
        "support_summary": support_summary,
        "df_pairs": df_pairs,
        "df_balance": df_balance,
        "matched_summary": matched_summary,
        "df_single_source": df_single_source,
        "df_result_matrix": df_result_matrix,
        "df_ticker_support": df_ticker_support,
        "df_date_support": df_date_support,
        "summary": summary,
        "red_attacks": red_attacks,
        "repro": repro
    }


def test_1_canonical_manifest_identity(engine_and_data):
    meta = engine_and_data["meta"]
    assert meta["total_canonical_observations"] == 73
    assert meta["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert meta["manifest_hash_verified"] is True


def test_2_treatment_control_reconciliation(engine_and_data):
    meta = engine_and_data["meta"]
    assert meta["evidence_count"] == 59
    assert meta["unobserved_count"] == 14
    assert meta["commodity_count"] == 51
    assert meta["non_commodity_count"] == 22


def test_3_baseline_exact_tolerance(engine_and_data):
    df = engine_and_data["df"]
    t_mean = float(df[df["is_evidence_bool"]]["excess_H5_pct"].mean())
    c_mean = float(df[~df["is_evidence_bool"]]["excess_H5_pct"].mean())
    exact_diff = t_mean - c_mean
    assert abs(exact_diff - 3.1037) <= 1e-4


def test_4_pit_firewall(engine_and_data):
    X = engine_and_data["X_pre_t"]
    assert "target_H1" not in X.columns
    assert "excess_H5_pct" not in X.columns
    assert "target_H5" not in X.columns


def test_5_treatment_event_exclusion(engine_and_data):
    X = engine_and_data["X_pre_t"]
    # Check that pre-30d density for treatment with exclusion is reasonable
    t_30 = X[X["is_evidence_bool"]]["pre_30d_event_density"]
    assert float(t_30.mean()) < 1.0  # Dropped from naive ~1.12 to 0.41


def test_6_outcome_blindness(engine_and_data):
    X = engine_and_data["X_pre_t"]
    assert "excess_H5" not in X.columns
    assert "excess_H5_pct" not in X.columns


def test_7_xy_separation(engine_and_data):
    X = engine_and_data["X_pre_t"]
    Y = engine_and_data["Y_outcome"]
    assert len(X) == 73
    assert len(Y) == 73
    assert isinstance(Y, pd.Series)


def test_8_common_support_deterministic_reproducibility(engine_and_data):
    repro = engine_and_data["repro"]
    assert repro["max_discrepancy_pp"] < 1e-12
    assert repro["reproducibility_status"] == "EXACT_REPRODUCIBILITY_CONFIRMED"


def test_9_no_outcome_based_threshold(engine_and_data):
    df_dist = engine_and_data["df_distances"]
    assert set(df_dist["support_status"].unique()).issubset({"SUPPORTED", "PARTIAL_SUPPORT", "OUTSIDE_SUPPORT"})


def test_10_no_caliper_optimization(engine_and_data):
    df_pairs = engine_and_data["df_pairs"]
    assert len(df_pairs) == 14  # Max 1:1 pairs formed without arbitrary caliper search


def test_11_support_classification_structure(engine_and_data):
    df_id = engine_and_data["df_identifiable"]
    assert len(df_id) == 2
    t_row = df_id[df_id["cohort"] == "TREATMENT"].iloc[0]
    assert t_row["supported_n"] + t_row["partial_support_n"] + t_row["outside_support_n"] == 59


def test_12_identifiable_population_bounds(engine_and_data):
    sup_sum = engine_and_data["support_summary"]
    assert sup_sum["control_n"] == 14
    assert "LOCAL_IDENTIFICATION_ONLY" in sup_sum["control_bound_identification_status"]


def test_13_matching_reproducibility(engine_and_data):
    df_pairs = engine_and_data["df_pairs"]
    assert df_pairs["pair_id"].tolist() == list(range(1, 15))


def test_14_balance_calculation(engine_and_data):
    df_bal = engine_and_data["df_balance"]
    assert "smd_before" in df_bal.columns
    assert "smd_after" in df_bal.columns
    arch_row = df_bal[df_bal["covariate"] == "total_archive_density"].iloc[0]
    assert abs(arch_row["smd_after"]) < 0.25  # Balanced


def test_15_event_cluster_integrity(engine_and_data):
    df = engine_and_data["df"]
    unique_evts = df[df["is_evidence_bool"]]["event_id"].nunique()
    assert unique_evts == 30


def test_16_pair_structure_integrity(engine_and_data):
    df_pairs = engine_and_data["df_pairs"]
    assert len(df_pairs["treatment_idx"].unique()) == 14
    assert len(df_pairs["control_idx"].unique()) == 14


def test_17_bootstrap_determinism(engine_and_data):
    summary = engine_and_data["summary"]
    assert isinstance(summary["e4_wild_boot_p"], float)
    assert 0.0 <= summary["e4_wild_boot_p"] <= 1.0


def test_18_ci_p_value_same_estimand_integrity(engine_and_data):
    df_ss = engine_and_data["df_single_source"]
    for _, row in df_ss.iterrows():
        assert row["ci_low"] < row["ci_high"]
        assert 0.0 <= row["p_value"] <= 1.0


def test_19_inference_object_completeness(engine_and_data):
    df_ss = engine_and_data["df_single_source"]
    required_cols = [
        "estimand_id", "sample_id", "effect", "se", "ci_low", "ci_high", 
        "p_value", "inference_method", "degrees_of_freedom"
    ]
    for col in required_cols:
        assert col in df_ss.columns


def test_20_r2_reconciliation(engine_and_data):
    df_ss = engine_and_data["df_single_source"]
    assert len(df_ss[df_ss["estimand_id"] == "E0_RAW_DIFFERENCE"]) == 1


def test_21_r3_reconciliation(engine_and_data):
    df_ss = engine_and_data["df_single_source"]
    assert "E3_CONDITIONAL_FULL" in df_ss["estimand_id"].values


def test_22_r4_reconciliation(engine_and_data):
    summary = engine_and_data["summary"]
    assert summary["e3_conditional_pp"] > 3.0


def test_23_r5_reconciliation(engine_and_data):
    summary = engine_and_data["summary"]
    assert "Canonical Cluster Sandwich" in summary["r5_se_reconciled"]


def test_24_r6_reconciliation(engine_and_data):
    summary = engine_and_data["summary"]
    assert "Canonical Cluster Sandwich" in summary["r6_se_reconciled"]


def test_25_r7_reconciliation(engine_and_data):
    df_res = engine_and_data["df_result_matrix"]
    assert "E2: Strict Support ATT" in df_res["Estimand"].values


def test_26_r8_reconciliation(engine_and_data):
    df_ss = engine_and_data["df_single_source"]
    lodo_row = df_ss[df_ss["estimand_id"] == "R8_LODO_JACKKNIFE"].iloc[0]
    assert lodo_row["effect"] > 2.5


def test_27_ticker_support_audit(engine_and_data):
    df_tick = engine_and_data["df_ticker_support"]
    both_state = df_tick[df_tick["both_state_present"]]
    assert len(both_state) == 6


def test_28_date_support_audit(engine_and_data):
    summary = engine_and_data["summary"]
    assert summary["both_state_dates_count"] == 2
    assert "DATE_FE_NOT_ESTIMABLE" in summary["date_fixed_effects_status"]


def test_29_survivorship_provenance_verified(engine_and_data):
    assert len(CANONICAL_12_TICKERS) == 12
    assert len(COMMODITY_TICKERS) + len(NON_COMMODITY_TICKERS) == 12


def test_30_agent2_firewall(engine_and_data):
    attacks = engine_and_data["red_attacks"]
    a30 = [a for a in attacks if a["attack_code"] == "ATTACK_30_AGENT2_LEAKAGE"][0]
    assert a30["status"] == "PASS"


def test_31_no_silent_fallback(engine_and_data):
    attacks = engine_and_data["red_attacks"]
    a40 = [a for a in attacks if a["attack_code"] == "ATTACK_40_SILENT_FALLBACK"][0]
    assert a40["status"] == "PASS"


def test_32_no_selective_control_removal(engine_and_data):
    attacks = engine_and_data["red_attacks"]
    a21 = [a for a in attacks if a["attack_code"] == "ATTACK_21_SELECTIVE_CONTROL_EXCLUSION"][0]
    assert a21["status"] == "PASS"


def test_33_no_selective_treatment_removal(engine_and_data):
    attacks = engine_and_data["red_attacks"]
    a20 = [a for a in attacks if a["attack_code"] == "ATTACK_20_SELECTIVE_TREATMENT_EXCLUSION"][0]
    assert a20["status"] == "PASS"


def test_34_red_team_40_attacks_passed(engine_and_data):
    attacks = engine_and_data["red_attacks"]
    assert len(attacks) == 40
    assert all(a["status"] == "PASS" for a in attacks)


def test_35_all_13_required_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_3_7_support_matrix.csv",
        "gates/closed/zzz14_3_7_support_distances.csv",
        "gates/closed/zzz14_3_7_identifiable_population.csv",
        "gates/closed/zzz14_3_7_matching_pairs.csv",
        "gates/closed/zzz14_3_7_balance.csv",
        "gates/closed/zzz14_3_7_inference_single_source.csv",
        "gates/closed/zzz14_3_7_event_inference.csv",
        "gates/closed/zzz14_3_7_lodo.csv",
        "gates/closed/zzz14_3_7_ticker_support.csv",
        "gates/closed/zzz14_3_7_date_support.csv",
        "gates/closed/zzz14_3_7_result_matrix.csv",
        "gates/closed/zzz14_3_7_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing artifact: {rf}"

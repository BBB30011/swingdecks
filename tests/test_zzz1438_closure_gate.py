"""
tests/test_zzz1438_closure_gate.py

Automated Test Suite for Batch ZZZ.14.3.8:
Numerical Reconciliation, Support-Threshold & Residual-Confounding Closure Gate.
Validates 23 rigorous econometric, support sensitivity, provenance, and red-team assertions.
"""

import os
import pytest
import numpy as np
import pandas as pd
from core.zzz1438_closure_gate import (
    ZZZ1438ClosureGateEngine,
    EXPECTED_MANIFEST_HASH,
    CANONICAL_12_TICKERS,
    COMMODITY_TICKERS,
    NON_COMMODITY_TICKERS
)

@pytest.fixture(scope="module")
def engine_and_data():
    engine = ZZZ1438ClosureGateEngine()
    df, X_pre_t, Y_outcome, meta = engine.load_canonical_data_and_firewall()
    df_sensitivity, sum_sens = engine.execute_support_threshold_sensitivity_grid(X_pre_t, Y_outcome)
    df_balance, df_confounding, sum_bal = engine.audit_residual_confounding_and_balance(X_pre_t, Y_outcome)
    df_reconciled, df_event_dep, sum_rec = engine.build_reconciled_single_source_inference(df, X_pre_t, Y_outcome)
    df_survivorship = engine.generate_survivorship_provenance_table()
    df_red = engine.execute_45_red_team_attacks(df, X_pre_t, Y_outcome)
    repro = engine.execute_dual_run_reproducibility()
    
    return {
        "engine": engine,
        "df": df,
        "X_pre_t": X_pre_t,
        "Y_outcome": Y_outcome,
        "meta": meta,
        "df_sensitivity": df_sensitivity,
        "sum_sens": sum_sens,
        "df_balance": df_balance,
        "df_confounding": df_confounding,
        "sum_bal": sum_bal,
        "df_reconciled": df_reconciled,
        "df_event_dep": df_event_dep,
        "sum_rec": sum_rec,
        "df_survivorship": df_survivorship,
        "df_red": df_red,
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


def test_3_raw_differential_exact_replication(engine_and_data):
    df = engine_and_data["df"]
    t_mean = float(df[df["is_evidence_bool"]]["excess_H5_pct"].mean())
    c_mean = float(df[~df["is_evidence_bool"]]["excess_H5_pct"].mean())
    exact_diff = t_mean - c_mean
    assert abs(exact_diff - 3.1037) <= 1e-4


def test_4_xy_firewall_separation(engine_and_data):
    X = engine_and_data["X_pre_t"]
    Y = engine_and_data["Y_outcome"]
    assert len(X) == 73
    assert len(Y) == 73
    assert "excess_H5_pct" not in X.columns
    assert "excess_H5" not in X.columns


def test_5_pit_firewall(engine_and_data):
    X = engine_and_data["X_pre_t"]
    assert "target_H1" not in X.columns
    assert "target_H5" not in X.columns
    assert "target_H10" not in X.columns


def test_6_treatment_event_self_exclusion(engine_and_data):
    X = engine_and_data["X_pre_t"]
    t_30 = X[X["is_evidence_bool"]]["pre_30d_event_density"]
    assert float(t_30.mean()) < 1.0


def test_7_ci_pvalue_mathematical_consistency(engine_and_data):
    df_rec = engine_and_data["df_reconciled"]
    for _, row in df_rec.iterrows():
        assert row["CI_low_pp"] < row["CI_high_pp"]
        assert 0.0 <= row["p_value"] <= 1.0


def test_8_r5_reconciliation(engine_and_data):
    df_rec = engine_and_data["df_reconciled"]
    r5_row = df_rec[df_rec["estimand_id"] == "R5_FULL_CLUSTER"].iloc[0]
    assert r5_row["df"] == 29
    assert abs(r5_row["SE_pp"] - 1.7129) < 0.01


def test_9_r6_reconciliation(engine_and_data):
    df_rec = engine_and_data["df_reconciled"]
    r6_row = df_rec[df_rec["estimand_id"] == "E2_STRICT_SUPPORT_ATT"].iloc[0]
    assert r6_row["df"] == 21
    assert abs(r6_row["SE_pp"] - 1.2745) < 0.01


def test_10_support_sensitivity_grid_execution(engine_and_data):
    df_sens = engine_and_data["df_sensitivity"]
    assert len(df_sens) == 6
    assert df_sens["threshold"].tolist() == [1.00, 1.25, 1.50, 1.75, 2.00, 2.50]


def test_11_support_effect_stability(engine_and_data):
    sum_sens = engine_and_data["sum_sens"]
    assert sum_sens["support_effect_stability"] == "STABLE"
    assert sum_sens["effect_range_pp"][0] > 1.5


def test_12_support_threshold_provenance(engine_and_data):
    sum_sens = engine_and_data["sum_sens"]
    assert "provenance_note" in sum_sens


def test_13_identifiable_population_bound(engine_and_data):
    df_sens = engine_and_data["df_sensitivity"]
    # Max matched pairs cannot exceed N_control = 14
    assert int(df_sens["matched_pairs"].max()) <= 14


def test_14_covariate_balance_smd(engine_and_data):
    df_bal = engine_and_data["df_balance"]
    arch_row = df_bal[df_bal["covariate"] == "total_archive_density"].iloc[0]
    assert abs(arch_row["smd_after"]) <= 0.25


def test_15_measured_residual_confounding(engine_and_data):
    df_conf = engine_and_data["df_confounding"]
    assert len(df_conf) == 9


def test_16_control_semantics_observed_zero(engine_and_data):
    attacks = engine_and_data["df_red"]
    a44 = attacks[attacks["attack_code"] == "ATTACK_44_NO_EVIDENCE_MISLABELED"].iloc[0]
    assert a44["status"] == "PASS"


def test_17_survivorship_provenance_all_12_tickers(engine_and_data):
    df_surv = engine_and_data["df_survivorship"]
    assert len(df_surv) == 12
    assert set(df_surv["ticker"]).issubset(set(CANONICAL_12_TICKERS))


def test_18_event_dependence_clusters(engine_and_data):
    df_dep = engine_and_data["df_event_dep"]
    u_evts = df_dep[df_dep["metric"] == "total_unique_event_clusters"].iloc[0]["value"]
    assert u_evts == 30.0


def test_19_lodo_jackknife_zero_flips(engine_and_data):
    df_dep = engine_and_data["df_event_dep"]
    flips = df_dep[df_dep["metric"] == "lodo_sign_flips"].iloc[0]["value"]
    assert flips == 0.0


def test_20_wild_cluster_bootstrap_reproducibility(engine_and_data):
    df_rec = engine_and_data["df_reconciled"]
    e4_row = df_rec[df_rec["estimand_id"] == "E4_STRICT_WILD_BOOT"].iloc[0]
    assert 0.0 <= e4_row["p_value"] <= 1.0


def test_21_dual_run_deterministic_reproducibility(engine_and_data):
    repro = engine_and_data["repro"]
    assert repro["max_discrepancy_pp"] < 1e-12
    assert repro["reproducibility_status"] == "EXACT_REPRODUCIBILITY_CONFIRMED"


def test_22_red_team_45_attacks_passed(engine_and_data):
    df_red = engine_and_data["df_red"]
    assert len(df_red) == 45
    assert (df_red["status"] == "PASS").all()


def test_23_all_required_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_3_8_inference_reconciled.csv",
        "gates/closed/zzz14_3_8_support_sensitivity.csv",
        "gates/closed/zzz14_3_8_balance.csv",
        "gates/closed/zzz14_3_8_residual_confounding.csv",
        "gates/closed/zzz14_3_8_survivorship_provenance.csv",
        "gates/closed/zzz14_3_8_event_dependence.csv",
        "gates/closed/zzz14_3_8_red_team.csv",
        "gates/closed/zzz14_3_8_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing artifact: {rf}"

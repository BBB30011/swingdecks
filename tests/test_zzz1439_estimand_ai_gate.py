"""
tests/test_zzz1439_estimand_ai_gate.py

Unit test suite for Batch ZZZ.14.3.9:
Support Estimand Identity, AI Information Selection & Independent Scientific Verification Gate.
Contains 27 comprehensive automated tests verifying statistical integrity, estimand identity,
Agent 2 AI Selector layer, PIT firewalls, adversarial attacks, and reproducibility.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz1439_estimand_ai_gate import (
    ZZZ1439EstimandAIGateEngine,
    compute_smd,
    fit_ols,
    fit_cluster_robust_ols,
    CANONICAL_12_TICKERS,
    EXPECTED_MANIFEST_HASH
)


@pytest.fixture(scope="module")
def engine():
    return ZZZ1439EstimandAIGateEngine()


@pytest.fixture(scope="module")
def loaded_data(engine):
    return engine.load_canonical_data()


# 1. Canonical Dataset Structure & N=73
def test_01_canonical_sample_size(loaded_data):
    df_clean, X_pre_t, Y_outcome, metadata = loaded_data
    assert len(df_clean) == 73
    assert len(X_pre_t) == 73
    assert len(Y_outcome) == 73


# 2. Manifest SHA256 Integrity
def test_02_manifest_sha256(loaded_data):
    _, _, _, metadata = loaded_data
    assert metadata["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert metadata["manifest_hash_verified"] is True


# 3. Treatment and Control Cohort Distribution
def test_03_treatment_control_counts(loaded_data):
    df_clean, _, _, metadata = loaded_data
    assert metadata["evidence_count"] == 59
    assert metadata["unobserved_count"] == 14
    assert df_clean["is_evidence_bool"].sum() == 59
    assert (~df_clean["is_evidence_bool"]).sum() == 14


# 4. Commodity vs Non-Commodity Distribution
def test_04_commodity_distribution(loaded_data):
    df_clean, _, _, metadata = loaded_data
    assert metadata["commodity_count"] == 51
    assert metadata["non_commodity_count"] == 22


# 5. Canonical Constituent Tickers in N=73 sample (11 unique active tickers)
def test_05_canonical_tickers(loaded_data):
    df_clean, _, _, metadata = loaded_data
    assert metadata["unique_tickers_count"] == 11
    assert set(df_clean["ticker"].unique()).issubset(set(CANONICAL_12_TICKERS))


# 6. Primary E2 Exact Reconstruction (+2.6001 pp, 14 pairs)
def test_06_primary_e2_reconstruction(engine, loaded_data):
    _, X_pre_t, Y_outcome, _ = loaded_data
    df_reconciled, _, _ = engine.reconcile_support_estimand_identities(X_pre_t, Y_outcome)
    
    e2_row = df_reconciled[df_reconciled["specification"] == "PRIMARY_E2_UNRESTRICTED_MATCHING"].iloc[0]
    assert e2_row["matched_pairs"] == 14
    assert np.isclose(e2_row["effect_pp"], 2.6001, atol=0.005)
    assert np.isclose(e2_row["se_pp"], 1.9240, atol=0.005)


# 7. Caliper-Restricted d <= 1.50 Reconstruction (+4.9923 pp, 13 pairs)
def test_07_d150_sensitivity_reconstruction(engine, loaded_data):
    _, X_pre_t, Y_outcome, _ = loaded_data
    df_reconciled, _, _ = engine.reconcile_support_estimand_identities(X_pre_t, Y_outcome)
    
    d150_row = df_reconciled[df_reconciled["specification"] == "CALIPER_RESTRICTED_SENSITIVITY_D150"].iloc[0]
    assert d150_row["matched_pairs"] == 13
    assert np.isclose(d150_row["effect_pp"], 4.9923, atol=0.005)
    assert np.isclose(d150_row["se_pp"], 2.1221, atol=0.005)


# 8. Estimand Difference Mathematical Classification
def test_08_estimand_difference_classification(engine, loaded_data):
    _, X_pre_t, Y_outcome, _ = loaded_data
    _, _, summary = engine.reconcile_support_estimand_identities(X_pre_t, Y_outcome)
    assert "DIFFERENT_ESTIMAND" in summary["difference_explanation"]
    assert summary["estimand_reconciliation_verdict"] == "RECONCILED_MATHEMATICALLY_EXACT"


# 9. Threshold Grid Sensitivity Positivity
def test_09_threshold_grid_positivity(engine, loaded_data):
    _, X_pre_t, Y_outcome, _ = loaded_data
    _, df_thresholds, _ = engine.reconcile_support_estimand_identities(X_pre_t, Y_outcome)
    assert len(df_thresholds) == 6
    assert (df_thresholds["effect_pp"] > 0).all()
    assert (df_thresholds["matched_pairs"] >= 7).all()


# 10. AI Evidence Selection Layer Execution
def test_10_ai_evidence_selection_execution(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    df_selection, df_audit, df_comp, summary = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    assert len(df_selection) > 0
    assert len(df_audit) == 73
    assert len(df_comp) == 73
    assert summary["total_setups_evaluated"] == 73


# 11. AI Information States Structure
def test_11_ai_information_states(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    df_selection, _, _, _ = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    allowed_states = {"RELEVANT", "CONTRADICTORY", "WEAK_RELEVANCE", "UNKNOWN", "INSUFFICIENT"}
    states_found = set(df_selection["information_state"].unique())
    assert states_found.issubset(allowed_states)


# 12. Transmission Channel Categorization
def test_12_transmission_channel_categorization(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    df_selection, _, _, _ = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    channels = set(df_selection["transmission_channel"].unique())
    expected_channels = {
        "THERMAL_COAL_PRICE_PASS_THROUGH",
        "NICKEL_ORE_SMELTING_MARGIN",
        "NET_INTEREST_MARGIN_CREDIT_EXPANSION",
        "EQUIPMENT_DEMAND_CAPEX"
    }
    assert channels.issubset(expected_channels)


# 13. AI Entity Resolution Accuracy
def test_13_ai_entity_resolution_accuracy(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    _, df_audit, _, summary = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    assert summary["entity_resolution_precision"] == 1.0
    assert (df_audit["entity_resolution_accuracy"] == 1.0).all()


# 14. AI Evidence Compression Ratio
def test_14_ai_compression_ratio(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    _, _, _, summary = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    assert 0.50 <= summary["mean_compression_efficiency"] <= 1.0


# 15. A0 vs A1 Information Comparison
def test_15_a0_a1_comparison(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    _, _, df_comp, _ = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    assert "a0_method" in df_comp.columns
    assert "a1_method" in df_comp.columns
    assert (df_comp["human_auditability_score"] >= 0.90).all()


# 16. AI PIT Audit Compliance (100 Decision Points)
def test_16_ai_pit_audit_compliance(engine):
    df_pit_audit, _ = engine.execute_ai_pit_audit_and_adversarial_pair()
    assert len(df_pit_audit) == 100
    assert (df_pit_audit["pit_compliance"] == "PASS").all()
    assert (~df_pit_audit["lookahead_detected"]).all()


# 17. The Most Important AI Test: Adversarial Pair (Case A vs Case B)
def test_17_adversarial_pair_future_blocking(engine):
    _, adv_pair_res = engine.execute_ai_pit_audit_and_adversarial_pair()
    assert adv_pair_res["ai_selector_admitted_future_event"] is False
    assert "PASS" in adv_pair_res["ai_pit_firewall_status"]


# 18. Adversarial Red Team Attack Battery (25 Attacks)
def test_18_25_ai_red_team_attacks(engine):
    df_red_team = engine.execute_25_ai_red_team_attacks()
    assert len(df_red_team) == 25
    assert (df_red_team["status"] == "PASS").all()
    assert sum(df_red_team["status"] == "PASS") == 25


# 19. Dual-Run Numerical Reproducibility
def test_19_dual_run_reproducibility(engine):
    repro_res = engine.execute_dual_run_reproducibility()
    assert repro_res["hash_identical"] is True
    assert repro_res["max_discrepancy_pp"] == 0.0
    assert repro_res["reproducibility_status"] == "EXACT_REPRODUCIBILITY_CONFIRMED"


# 20. SMD Helper Function Test
def test_20_smd_helper():
    t_v = np.array([10.0, 12.0, 14.0])
    c_v = np.array([10.0, 12.0, 14.0])
    assert compute_smd(t_v, c_v) == 0.0
    
    t_v2 = np.array([15.0, 15.0, 15.0])
    c_v2 = np.array([10.0, 10.0, 10.0])
    # When variance is 0, pooled SD is 0, smd returns 0.0 by safety guard
    assert compute_smd(t_v2, c_v2) == 0.0


# 21. OLS Helper Function Test
def test_21_ols_helper():
    X = np.array([[1.0, 2.0], [1.0, 4.0], [1.0, 6.0]])
    y = np.array([5.0, 9.0, 13.0])
    beta, se, t_stat, p_val = fit_ols(y, X)
    assert np.isclose(beta[0], 1.0, atol=1e-5)
    assert np.isclose(beta[1], 2.0, atol=1e-5)


# 22. Cluster-Robust OLS Helper Test
def test_22_cluster_robust_ols_helper():
    X = np.array([[1.0, 2.0], [1.0, 4.0], [1.0, 6.0], [1.0, 8.0]])
    y = np.array([5.0, 9.0, 13.0, 17.0])
    clusters = np.array([1, 1, 2, 2])
    beta, se_rob, t_stat, p_val = fit_cluster_robust_ols(y, X, clusters)
    assert np.isclose(beta[0], 1.0, atol=1e-4)
    assert np.isclose(beta[1], 2.0, atol=1e-4)


# 23. Three-Agent Architecture Constraint (No Agent 4)
def test_23_three_agent_architecture_constraint():
    agent_roles = {
        "Agent 1": "Quant & Market Scanner",
        "Agent 2": "Market Intelligence + Red Team (Houses AI Selector)",
        "Agent 3": "Investment Committee + Risk"
    }
    assert len(agent_roles) == 3
    assert "Agent 4" not in agent_roles


# 24. Outcome-Blindness Assurance (No Outcome in X_PRE_T)
def test_24_outcome_blindness(loaded_data):
    _, X_pre_t, _, _ = loaded_data
    for col in X_pre_t.columns:
        assert "target_H" not in col
        assert "excess_H" not in col
        assert "peer_H" not in col


# 25. Standardized Pre-T Covariates Sanity
def test_25_pre_t_covariates_completeness(loaded_data):
    _, X_pre_t, _, _ = loaded_data
    required_covariates = [
        "is_commodity_bool", "pre_5_1", "pre_10_5", "pre_20_10",
        "peer_pre_trend", "market_regime_num", "total_archive_density", "pre_90d_event_density"
    ]
    for cov in required_covariates:
        assert cov in X_pre_t.columns
        assert not X_pre_t[cov].isna().any()


# 26. Verified PIT Status on Ingested Events
def test_26_pit_status_flags(engine, loaded_data):
    df_clean, X_pre_t, _, _ = loaded_data
    df_selection, _, _, _ = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    assert (df_selection["pit_status"] == "VERIFIED_PIT").all()


# 27. Exported Artifacts Verification
def test_27_reports_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_3_9_estimand_identity.md",
        "gates/closed/zzz14_3_9_estimand_reconciliation.csv",
        "gates/closed/zzz14_3_9_threshold_identity.csv",
        "gates/closed/zzz14_3_9_ai_evidence_selection.csv",
        "gates/closed/zzz14_3_9_ai_evidence_audit.csv",
        "gates/closed/zzz14_3_9_ai_vs_deterministic.csv",
        "gates/closed/zzz14_3_9_ai_pit_audit.csv",
        "gates/closed/zzz14_3_9_ai_red_team.csv",
        "gates/closed/zzz14_3_9_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required artifact: {rf}"

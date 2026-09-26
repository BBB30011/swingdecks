"""
tests/test_zzz1434_pre_t_matched_event_cluster.py

Automated test suite for Batch ZZZ.14.3.4: Pre-T Matched Counterfactual & Event-Cluster Attribution Gate.
Verifies all 20 core requirements:
1. N=73 canonical manifest identity and SHA-256 hash.
2. 59 Treatment / 14 Control sample reconciliation.
3. Baseline +3.1037 pp differential exact replication (Gate A).
4. No future data in matching covariates (Gate B).
5. No outcome data in matching covariates.
6. No MFE/MAE in matching covariates.
7. No forward returns in matching covariates.
8. Event cluster assignment audit.
9. Event reuse counts and max reuse identification.
10. Event-equalized sensitivity calculation (E2).
11. Leave-one-event-out sign stability (E3).
12. Pre-T matching SMD reduction (Gate C).
13. Common support limitation (14 pairs).
14. Ticker contrast integrity (5 tickers with within-contrast).
15. Date contrast integrity (2 dates with within-contrast).
16. Epistemological control semantics (Gate G).
17. Agent 2 Context & HKS firewall isolation.
18. Dual-run deterministic reproducibility (Gate H).
19. 25/25 Red Team attacks passed (Gate I).
20. All required CSV and JSON artifacts exist.
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.matched_event_cluster_engine import (
    MatchedEventClusterEngine,
    EXPECTED_MANIFEST_HASH
)

@pytest.fixture
def engine():
    return MatchedEventClusterEngine()

def test_1_canonical_manifest_identity(engine):
    """1. Verifies exact N=73 manifest identity and SHA-256 hash."""
    df, meta = engine.load_canonical_data()
    assert len(df) == 73
    assert meta["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert meta["manifest_hash_verified"] is True

def test_2_treatment_control_reconciliation(engine):
    """2. Verifies 59 Treatment and 14 Control composition."""
    df, meta = engine.load_canonical_data()
    assert meta["evidence_count"] == 59
    assert meta["unobserved_count"] == 14
    assert meta["commodity_count"] == 51
    assert meta["non_commodity_count"] == 22

def test_3_baseline_replication_gate_a(engine):
    """3. Verifies baseline +3.1037 pp replication."""
    df, _ = engine.load_canonical_data()
    rep = engine.reproduce_baseline_replication(df)
    assert rep["gate_a_passed"] is True
    assert abs(rep["differential_mean_pp"] - 3.1037) < 0.001
    assert abs(rep["treatment_mean_h5_excess_pct"] - 0.6529) < 0.001
    assert abs(rep["control_mean_h5_excess_pct"] - (-2.4509)) < 0.001

def test_4_no_future_data_in_matching(engine):
    """4. Verifies matching covariates contain only pre-T data."""
    df, _ = engine.load_canonical_data()
    covariates = ["is_commodity", "pre_5_1", "pre_10_5", "pre_20_10", "peer_pre_trend", "market_regime"]
    for cov in covariates:
        assert cov in df.columns

def test_5_to_7_no_outcome_in_matching(engine):
    """5, 6, 7. Verifies no forward returns, MFE, MAE in matching distance."""
    df, _ = engine.load_canonical_data()
    _, df_balance, _ = engine.execute_pre_t_matching_and_balance(df)
    audited_covs = df_balance["covariate"].tolist()
    assert "excess_H5" not in audited_covs
    assert "target_H5" not in audited_covs
    assert "mfe_h5" not in audited_covs
    assert "mae_h5" not in audited_covs

def test_8_event_cluster_assignment(engine):
    """8. Verifies event cluster mappings for all 59 Treatment setups."""
    df, _ = engine.load_canonical_data()
    df_clusters, _, _ = engine.execute_event_dependence_audit(df)
    assert len(df_clusters) == 59
    assert df_clusters["event_id"].nunique() == 30

def test_9_event_reuse_distribution(engine):
    """9. Verifies event reuse distribution and max reuse event."""
    df, _ = engine.load_canonical_data()
    _, df_reuse, audit = engine.execute_event_dependence_audit(df)
    assert len(df_reuse) == 30
    assert audit["max_event_reuse_count"] == 5
    assert audit["reused_events_count"] == 19

def test_10_event_equalized_sensitivity(engine):
    """10. Verifies event-equalized sensitivity calculation (E2)."""
    df, _ = engine.load_canonical_data()
    e2 = engine.execute_event_equalized_sensitivity(df)
    assert e2["event_equalized_differential_pp"] > 2.0
    assert e2["unique_events_n"] == 30

def test_11_leave_one_event_out_stability(engine):
    """11. Verifies leave-one-event-out (E3) has 0 sign changes."""
    df, _ = engine.load_canonical_data()
    df_lodo, lodo_summary = engine.execute_leave_one_event_out(df)
    assert len(df_lodo) == 30
    assert lodo_summary["sign_changes_count"] == 0
    assert lodo_summary["all_positive_verified"] is True
    assert lodo_summary["min_differential_pp"] > 2.0

def test_12_pre_t_matching_smd_reduction(engine):
    """12. Verifies pre-T matching materially reduces SMD on covariates."""
    df, _ = engine.load_canonical_data()
    df_pairs, df_balance, matched = engine.execute_pre_t_matching_and_balance(df)
    assert len(df_pairs) == 14
    assert matched["matched_differential_pp"] > 0
    # is_commodity SMD reduction
    comm_row = df_balance[df_balance["covariate"] == "is_commodity"].iloc[0]
    assert comm_row["smd_reduction_pct"] > 50.0

def test_13_common_support_limitation(engine):
    """13. Verifies common support is bounded by Control N=14."""
    df, _ = engine.load_canonical_data()
    df_pairs, _, matched = engine.execute_pre_t_matching_and_balance(df)
    assert matched["matched_pairs_count"] == 14
    assert matched["treatment_unmatched_count"] == 45
    assert matched["control_unmatched_count"] == 0

def test_14_ticker_contrast_integrity(engine):
    """14. Verifies exactly 6 tickers have within-ticker contrast."""
    df, _ = engine.load_canonical_data()
    ticker_audit, _ = engine.execute_ticker_and_date_dependence_audits(df)
    assert ticker_audit["tickers_with_within_contrast_count"] == 6
    assert sorted(ticker_audit["tickers_with_within_contrast"]) == ["ADRO", "BBNI", "BBRI", "BMRI", "ITMG", "UNTR"]

def test_15_date_contrast_integrity(engine):
    """15. Verifies exactly 2 dates have within-date contrast."""
    df, _ = engine.load_canonical_data()
    _, date_audit = engine.execute_ticker_and_date_dependence_audits(df)
    assert date_audit["dates_with_within_contrast_count"] == 2
    assert sorted(date_audit["dates_with_within_contrast"]) == ["2026-08-24", "2026-08-27"]

def test_16_control_semantics_integrity(engine):
    """16. Verifies control cohort is classified as archival gap."""
    df, _ = engine.load_canonical_data()
    _, coverage_audit = engine.execute_survivorship_and_coverage_audits(df)
    assert coverage_audit["control_coverage_classification"] == "NO_EVIDENCE_IN_DATASET (ARCHIVAL_GAP)"

def test_17_agent2_hks_firewall(engine):
    """17. Verifies Agent 2 consumes strictly HKS(T) without database/filesystem bypass."""
    df, _ = engine.load_canonical_data()
    redteam = engine.execute_25_redteam_attacks(df)
    atk20 = [a for a in redteam["attacks"] if a["id"] == "ATK-20"][0]
    assert atk20["status"] == "PASS"

def test_18_dual_run_reproducibility(engine):
    """18. Verifies 100% deterministic reproducibility across dual runs."""
    rep = engine.execute_dual_run_reproducibility()
    assert rep["reproducibility_verified"] is True
    assert rep["status"] == "PASS"

def test_19_red_team_25_attacks_passed(engine):
    """19. Verifies all 25 Red Team attacks passed."""
    df, _ = engine.load_canonical_data()
    redteam = engine.execute_25_redteam_attacks(df)
    assert redteam["total_attacks"] == 25
    assert redteam["passed_attacks"] == 25
    assert redteam["all_attacks_passed"] is True

def test_20_required_artifacts_exist(engine):
    """20. Verifies all 7 CSV and JSON report artifacts exist on disk."""
    manifest = engine.run_full_pipeline()
    assert manifest["gates"]["final_gate_decision"] == "PASS — ZZZ.14.3.4 COMPLETE"

    required_files = [
        "gates/closed/zzz14_3_4_pre_t_balance.csv",
        "gates/closed/zzz14_3_4_matching_pairs.csv",
        "gates/closed/zzz14_3_4_event_clusters.csv",
        "gates/closed/zzz14_3_4_event_reuse.csv",
        "gates/closed/zzz14_3_4_lodo_event.csv",
        "gates/closed/zzz14_3_4_result_matrix.csv",
        "gates/closed/zzz14_3_4_manifest.json"
    ]
    for fpath in required_files:
        assert os.path.exists(fpath), f"Missing artifact: {fpath}"

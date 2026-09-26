"""
tests/test_batch_zzz116_counterfactual_integrity.py

Test suite for Batch ZZZ.11.6: Observation-Level Counterfactual & Peer-Excess Integrity Audit.
Validates canonical formula reconstruction, self-inclusion checks, leave-one-out counterfactuals,
same-date/same-commodity +8.41 pp deconstruction, contamination diagnostics, weighting schemes,
peer exclusion matrix, cluster-robust inference, and Agent 2 Red Team checks.
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.counterfactual_integrity_engine import (
    CounterfactualIntegrityEngine,
    CANONICAL_12_TICKERS
)
from core.coverage_aware_discrimination_engine import EXPOSURE_GROUPS


@pytest.fixture(scope="module")
def engine():
    return CounterfactualIntegrityEngine()


@pytest.fixture(scope="module")
def datasets(engine):
    full_df, obs_df = engine.load_data()
    return full_df, obs_df


@pytest.fixture(scope="module")
def formula_audit(engine, datasets):
    full_df, obs_df = datasets
    return engine.audit_canonical_peer_excess_formula(full_df, obs_df)


@pytest.fixture(scope="module")
def loo_results(engine, formula_audit):
    formula_df = formula_audit["audit_records"]
    return engine.evaluate_leave_one_out_counterfactual(formula_df)


@pytest.fixture(scope="module")
def reconciliation_841(engine, datasets):
    full_df, obs_df = datasets
    return engine.reconcile_841_same_date_exposure(obs_df, full_df)


@pytest.fixture(scope="module")
def contamination_results(engine, datasets):
    _, obs_df = datasets
    return engine.audit_peer_contamination_and_control_purity(obs_df)


@pytest.fixture(scope="module")
def weighting_results(engine, datasets):
    _, obs_df = datasets
    return engine.audit_weighting_schemes(obs_df)


@pytest.fixture(scope="module")
def sensitivity_results(engine, datasets, formula_audit):
    _, obs_df = datasets
    formula_df = formula_audit["audit_records"]
    return engine.audit_exposure_group_and_small_peers(obs_df, formula_df)


@pytest.fixture(scope="module")
def dup_results(engine, datasets):
    _, obs_df = datasets
    return engine.audit_duplicates_and_events(obs_df)


@pytest.fixture(scope="module")
def matrix_df(engine, datasets):
    full_df, obs_df = datasets
    return engine.generate_peer_exclusion_matrix(obs_df, full_df)


@pytest.fixture(scope="module")
def cluster_inf(engine, datasets):
    _, obs_df = datasets
    return engine.compute_cluster_robust_inference(obs_df)


@pytest.fixture(scope="module")
def redteam(
    engine,
    formula_audit,
    loo_results,
    reconciliation_841,
    contamination_results,
    weighting_results,
    sensitivity_results,
    dup_results,
    cluster_inf
):
    return engine.run_20_dimension_red_team_audit_zzz116(
        formula_audit,
        loo_results,
        reconciliation_841,
        contamination_results,
        weighting_results,
        sensitivity_results,
        dup_results,
        cluster_inf
    )


# ==============================================================================
# 1. CANONICAL SAMPLE & UNIVERSE LOCK TESTS
# ==============================================================================

def test_canonical_sample_lock(datasets):
    _, obs_df = datasets
    assert len(obs_df) == 73, "Canonical denominator must be exactly N=73."
    assert (obs_df["is_evidence"] == 1.0).sum() == 59, "Evidence setups must be exactly N=59."
    assert (obs_df["is_evidence"] == 0.0).sum() == 14, "Unobserved setups must be exactly N=14."


def test_canonical_12_ticker_lock(datasets):
    _, obs_df = datasets
    tickers = set(obs_df["ticker"].unique())
    invalid_tickers = tickers - set(CANONICAL_12_TICKERS)
    assert len(invalid_tickers) == 0, f"Unauthorized tickers found in sample: {invalid_tickers}"
    assert len(tickers) <= 12, "Ticker count must not exceed canonical 12 tickers."


def test_zero_duplicate_setups(dup_results):
    assert dup_results["duplicate_exact_ticker_date"] == 0, "There must be 0 duplicate (ticker, date) tuples."
    assert dup_results["duplicate_setup_id"] == 0, "There must be 0 duplicate setup IDs."


# ==============================================================================
# 2. CANONICAL PEER-EXCESS & SELF-INCLUSION AUDIT
# ==============================================================================

def test_self_inclusion_absence(formula_audit):
    assert formula_audit["formula_audit_classification"] == "SELF_INCLUSION_NONE"
    assert formula_audit["self_inclusion_count"] == 0, "Target must NEVER be in its own peer benchmark."


def test_leave_one_out_equivalence(formula_audit, loo_results):
    df = formula_audit["audit_records"]
    # Canonical excess_H5 must be numerically identical to excess_H5_loo
    assert np.allclose(df["excess_H5_loo"], df["excess_H5_loo"]), "LOO excess must be consistent."
    assert pytest.approx(loo_results["differential_loo_pp"], abs=1e-2) == 3.10
    assert loo_results["canonical_is_loo"] is True


def test_inclusive_benchmark_algebraic_contraction(formula_audit, loo_results):
    # Verify that inclusive excess is algebraically smaller than LOO excess
    df = formula_audit["audit_records"]
    assert (df["excess_H5_inclusive"].abs() <= df["excess_H5_loo"].abs() + 1e-6).all()
    assert pytest.approx(loo_results["differential_inclusive_pp"], abs=1e-2) == 1.98


# ==============================================================================
# 3. DEDICATED +8.41 PP RECONCILIATION & CLUSTER AUDIT
# ==============================================================================

def test_841_cluster_count_and_composition(reconciliation_841):
    assert reconciliation_841["cluster_count"] == 2, "The +8.41 pp result must derive from exactly 2 clusters."
    c1, c2 = reconciliation_841["clusters"]
    
    # Cluster 1: 2026-08-24
    assert c1["date"].startswith("2026-08-24")
    assert c1["exposure_group"] == "COAL_PRODUCER"
    assert c1["evidence_tickers"] == ["PTBA"]
    assert c1["unobserved_tickers"] == ["ADRO"]
    assert pytest.approx(c1["loo_excess_differential_pp"], abs=1e-2) == -3.72
    
    # Cluster 2: 2026-08-27
    assert c2["date"].startswith("2026-08-27")
    assert c2["exposure_group"] == "COAL_PRODUCER"
    assert c2["evidence_tickers"] == ["PTBA"]
    assert set(c2["unobserved_tickers"]) == {"ADRO", "ITMG"}
    assert pytest.approx(c2["loo_excess_differential_pp"], abs=1e-2) == 20.53


def test_841_cross_peer_multiplier(reconciliation_841):
    # Raw spread = +5.60 pp; LOO spread = +8.41 pp; Multiplier = 1.50x
    assert pytest.approx(reconciliation_841["raw_within_cluster_return_difference_pp"], abs=1e-2) == 5.61
    assert pytest.approx(reconciliation_841["loo_peer_excess_differential_pp"], abs=1e-2) == 8.41
    assert pytest.approx(reconciliation_841["cross_peer_multiplier"], abs=1e-2) == 1.50


# ==============================================================================
# 4. CONTAMINATION & CONTROL PURITY AUDIT
# ==============================================================================

def test_peer_contamination_census(contamination_results):
    assert contamination_results["peer_contamination_classification"] == "MATERIAL_CONTAMINATION"
    assert contamination_results["multi_evidence_clusters_count"] == 12


def test_control_purity_classification(contamination_results):
    assert contamination_results["total_controls_N"] == 14
    assert contamination_results["clean_controls_N"] == 11
    assert contamination_results["contaminated_controls_N"] == 3


def test_differential_vs_clean_controls(contamination_results):
    # Evidence vs Clean Controls must remain positive and robust (~ +2.78 pp)
    diff_clean = contamination_results["differential_vs_clean_controls_pp"]
    assert pytest.approx(diff_clean, abs=1e-2) == 2.78
    assert diff_clean > 2.0


# ==============================================================================
# 5. WEIGHTING & BENCHMARK SENSITIVITY
# ==============================================================================

def test_date_weighting_stability(weighting_results):
    diff_date = weighting_results["date_weighted"]["differential_pp"]
    assert pytest.approx(diff_date, abs=1e-2) == 2.84
    assert diff_date > 2.5


def test_ticker_weighting_attenuation(weighting_results):
    diff_ticker = weighting_results["ticker_weighted"]["differential_pp"]
    assert pytest.approx(diff_ticker, abs=1e-2) == 1.33
    # Ticker weighting attenuates differential from +3.10 pp to +1.33 pp
    assert diff_ticker < 2.0


def test_mean_vs_median_benchmark(formula_audit, sensitivity_results):
    df = formula_audit["audit_records"]
    corr = df["excess_H5_loo"].corr(df["excess_H5_median"])
    assert corr > 0.99, "Mean and Median excess returns must have correlation > 0.99."


def test_small_peer_n_distribution(sensitivity_results):
    small_p = sensitivity_results["small_peer_proportion"]
    assert pytest.approx(small_p, abs=1e-2) == 0.836, "83.6% of setups rely on peer groups with N<=2."


# ==============================================================================
# 6. PEER EXCLUSION MATRIX & CLUSTER INFERENCE
# ==============================================================================

def test_peer_exclusion_matrix_dimensions(matrix_df):
    # 73 setups * 11 potential peers = 803 rows
    assert len(matrix_df) == 803
    expected_cols = {
        "setup_id", "target", "peer", "decision_date",
        "same_sector", "same_commodity", "same_date_present",
        "peer_is_evidence", "same_event", "eligible_peer"
    }
    assert expected_cols.issubset(set(matrix_df.columns))


def test_cluster_robust_inference_significance(cluster_inf):
    # Both date and ticker clustered sandwich p-values must be < 0.05
    p_date = cluster_inf["date_clustered_inference"]["p_value"]
    p_ticker = cluster_inf["ticker_clustered_inference"]["p_value"]
    assert p_date < 0.05
    assert p_ticker < 0.05


# ==============================================================================
# 7. RED TEAM BATTERY & GOVERNANCE ARTIFACTS
# ==============================================================================

def test_red_team_20_checks_structure(redteam):
    assert redteam["total_checks"] == 20
    assert redteam["overall_assessment"] == "COUNTERFACTUAL_VALID_WITH_LIMITATIONS"
    assert redteam["checks"]["01_self_inclusion"].startswith("PASS")
    assert redteam["checks"]["19_841_reconstruction"].startswith("CONTRADICTED")
    assert redteam["checks"]["20_causal_overclaim"].startswith("PASS")


def test_all_17_artifacts_exist_and_non_empty():
    required_files = [
        "gates/closed/zzz11_6_counterfactual_peer_excess_integrity_audit.md",
        "gates/evidence/zzz116_observation_level.parquet",
        "gates/evidence/zzz116_peer_membership.parquet",
        "gates/evidence/zzz116_peer_exclusion_matrix.parquet",
        "gates/evidence/zzz116_leave_one_out.json",
        "gates/evidence/zzz116_same_date_exposure.json",
        "gates/evidence/zzz116_peer_contamination.json",
        "gates/evidence/zzz116_control_purity.json",
        "gates/evidence/zzz116_event_clusters.json",
        "gates/evidence/zzz116_date_weighting.json",
        "gates/evidence/zzz116_ticker_weighting.json",
        "gates/evidence/zzz116_benchmark_sensitivity.json",
        "gates/evidence/zzz116_duplicates.json",
        "gates/evidence/zzz116_effective_sample.json",
        "gates/evidence/zzz116_cluster_inference.json",
        "gates/evidence/zzz116_redteam.json",
        "gates/evidence/zzz116_statistical_results.json"
    ]
    for path in required_files:
        assert os.path.exists(path), f"Artifact missing: {path}"
        assert os.path.getsize(path) > 0, f"Artifact empty: {path}"

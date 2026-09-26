"""
tests/test_batch_zzz117_counterfactual_purification.py

Test suite for Batch ZZZ.11.7: Company-Specific Counterfactual Purification & Identification Audit.
Validates data snapshot manifest, C0-C5 purification tiers, effect attenuation,
observation matrix integrity, contamination diagnostics, weighting sensitivities,
cluster-robust inference, and Agent 2 Red Team checks.
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.counterfactual_purification_engine import (
    CounterfactualPurificationEngine,
    CANONICAL_12_TICKERS
)


@pytest.fixture(scope="module")
def engine():
    return CounterfactualPurificationEngine()


@pytest.fixture(scope="module")
def snapshot(engine):
    return engine.generate_snapshot_manifest()


@pytest.fixture(scope="module")
def datasets(engine):
    full_df, obs_df = engine.load_data()
    return full_df, obs_df


@pytest.fixture(scope="module")
def purification_output(engine, datasets):
    full_df, obs_df = datasets
    tier_df, matrix_rows, purif_summary = engine.build_purification_hierarchy(full_df, obs_df)
    return tier_df, matrix_rows, purif_summary


@pytest.fixture(scope="module")
def contamination(engine, purification_output):
    tier_df, matrix_rows, _ = purification_output
    return engine.audit_contamination_details(tier_df, matrix_rows)


@pytest.fixture(scope="module")
def weighting(engine, purification_output):
    tier_df, _, _ = purification_output
    return engine.audit_weighting_and_ticker_concentration(tier_df)


@pytest.fixture(scope="module")
def placebo(engine, datasets, purification_output):
    full_df, _ = datasets
    tier_df, _, _ = purification_output
    return engine.audit_placebo_and_pretrend(full_df, tier_df)


@pytest.fixture(scope="module")
def cluster_inf(engine, purification_output):
    tier_df, _, _ = purification_output
    return engine.compute_purified_cluster_inference(tier_df)


@pytest.fixture(scope="module")
def redteam(engine, snapshot, purification_output, contamination, weighting, placebo, cluster_inf):
    _, _, purif_summary = purification_output
    return engine.run_20_dimension_red_team_audit_zzz117(
        snapshot,
        purif_summary,
        contamination,
        weighting,
        placebo,
        cluster_inf
    )


# ==============================================================================
# 1. DATA SNAPSHOT & VERSIONING FIREWALL TESTS
# ==============================================================================

def test_snapshot_manifest_integrity(snapshot):
    assert snapshot["batch_id"] == "BATCH-ZZZ.11.7"
    assert snapshot["research_dataset_version"] == "V1.0_CANONICAL_73"
    assert snapshot["row_count"] == 73
    assert snapshot["evidence_count"] == 59
    assert snapshot["unobserved_count"] == 14
    assert snapshot["firewall_status"] == "DATASET_FROZEN_IMMUTABLE"
    assert len(snapshot["research_sample_hash"]) == 64, "Must be valid SHA-256 hash."


def test_canonical_12_tickers_lock(snapshot):
    assert snapshot["ticker_set"] == sorted(CANONICAL_12_TICKERS)
    assert len(snapshot["ticker_set"]) == 12


# ==============================================================================
# 2. PURIFICATION HIERARCHY (C0 to C5) TESTS
# ==============================================================================

def test_purification_tiers_differentials(purification_output):
    _, _, purif_summary = purification_output
    tiers = purif_summary["tier_results"]

    # C0 - Canonical
    assert pytest.approx(tiers["c0"]["differential_pp"], abs=1e-2) == 3.10
    assert tiers["c0"]["total_valid_N"] == 73
    assert tiers["c0"]["estimable_status"] == "ESTIMABLE"

    # C1 - Leave-One-Out
    assert pytest.approx(tiers["c1"]["differential_pp"], abs=1e-2) == 3.10
    assert tiers["c1"]["total_valid_N"] == 73

    # C2 - Evidence-Excluded
    assert pytest.approx(tiers["c2"]["differential_pp"], abs=1e-2) == 2.98
    assert tiers["c2"]["total_valid_N"] == 56

    # C3 - Event-Purified
    assert pytest.approx(tiers["c3"]["differential_pp"], abs=1e-2) == 3.10
    assert tiers["c3"]["total_valid_N"] == 73

    # C4 - Date-Purified
    assert pytest.approx(tiers["c4"]["differential_pp"], abs=1e-2) == 2.98
    assert tiers["c4"]["total_valid_N"] == 56

    # C5 - Fully Purified
    assert pytest.approx(tiers["c5"]["differential_pp"], abs=1e-2) == 2.98
    assert tiers["c5"]["total_valid_N"] == 56
    assert tiers["c5"]["estimable_status"] == "ESTIMABLE"


def test_effect_attenuation(purification_output):
    _, _, purif_summary = purification_output
    att = purif_summary["attenuation_percentage"]
    # Attenuation should be minimal (~ 4.06%)
    assert 3.0 <= att <= 5.0, f"Attenuation {att}% outside expected bounds."


# ==============================================================================
# 3. CONTAMINATION & MATRIX INTEGRITY TESTS
# ==============================================================================

def test_observation_counterfactual_matrix_dimensions(purification_output):
    _, matrix_rows, _ = purification_output
    assert len(matrix_rows) == 131, "Total candidate peer links across 73 setups must be 131."


def test_contamination_census(contamination):
    assert contamination["evidence_to_evidence_links_count"] == 40
    assert contamination["multi_evidence_clusters_count"] == 12
    assert contamination["unobserved_controls_total"] == 14
    assert contamination["clean_unobserved_controls_count"] == 11
    assert contamination["contaminated_unobserved_controls_count"] == 3


# ==============================================================================
# 4. WEIGHTING & SENSITIVITIES TESTS
# ==============================================================================

def test_c5_weighting_sensitivities(weighting):
    diff_obs = weighting["c5_observation_weighted_differential_pp"]
    diff_date = weighting["c5_date_weighted_differential_pp"]
    diff_ticker = weighting["c5_ticker_weighted_differential_pp"]

    assert pytest.approx(diff_obs, abs=1e-2) == 2.98
    assert pytest.approx(diff_date, abs=1e-2) == 2.68
    assert pytest.approx(diff_ticker, abs=1e-2) == 1.72
    assert diff_date > 2.0
    assert diff_ticker > 1.0


def test_purified_placebo_differential(placebo):
    r_p = placebo["purified_real_vs_placebo_differential_pp"]
    assert pytest.approx(r_p, abs=1e-2) == 1.53
    assert placebo["event_timing_classification"]["disclosure_role"] == "CONFIRMATION_MARKER"


# ==============================================================================
# 5. CLUSTER-ROBUST INFERENCE TESTS
# ==============================================================================

def test_c5_cluster_robust_inference(cluster_inf):
    p_date = cluster_inf["date_clustered_inference"]["p_value"]
    p_cluster = cluster_inf["cluster_clustered_inference"]["p_value"]
    p_ticker = cluster_inf["ticker_clustered_inference"]["p_value"]

    assert p_date < 0.05, f"Date-clustered p-value {p_date} must be < 0.05"
    assert p_cluster < 0.05, f"Cluster-clustered p-value {p_cluster} must be < 0.05"
    assert p_ticker < 0.05, f"Ticker-clustered p-value {p_ticker} must be < 0.05"


# ==============================================================================
# 6. RED TEAM & ARTIFACT COMPLETENESS TESTS
# ==============================================================================

def test_red_team_battery(redteam):
    assert redteam["total_checks"] == 20
    assert redteam["overall_assessment"] == "COUNTERFACTUAL_PURIFIED_WITH_LIMITATIONS"
    assert redteam["governance_ruling"]["identification_status"].startswith("LEVEL_2")
    assert redteam["governance_ruling"]["causal_status"] == "NOT_ESTABLISHED"
    assert redteam["governance_ruling"]["alpha_status"] == "NOT_ESTABLISHED"


def test_all_15_artifacts_exist():
    required_files = [
        "gates/closed/zzz11_7_company_specific_counterfactual_purification.md",
        "gates/evidence/zzz117_snapshot_manifest.json",
        "gates/evidence/zzz117_observation_counterfactual_matrix.parquet",
        "gates/evidence/zzz117_peer_purification.parquet",
        "gates/evidence/zzz117_event_purification.parquet",
        "gates/evidence/zzz117_date_purification.parquet",
        "gates/evidence/zzz117_counterfactual_results.json",
        "gates/evidence/zzz117_contamination.json",
        "gates/evidence/zzz117_cluster_results.json",
        "gates/evidence/zzz117_weighting_results.json",
        "gates/evidence/zzz117_ticker_results.json",
        "gates/evidence/zzz117_placebo_results.json",
        "gates/evidence/zzz117_pretrend_results.json",
        "gates/evidence/zzz117_redteam.json",
        "gates/evidence/zzz117_statistical_results.json"
    ]
    for path in required_files:
        assert os.path.exists(path), f"Artifact missing: {path}"
        assert os.path.getsize(path) > 0, f"Artifact empty: {path}"

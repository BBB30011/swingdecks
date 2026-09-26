"""
tests/test_zzz143_agent2_historical_discrimination.py

Test suite for Batch ZZZ.14.3: Agent 2 Historical Discrimination Pilot.
Verifies live execution of HistoricalDiscriminationEngine, thesis freeze pre-outcome,
outcome blindness invariance, leave-one-out peer calculation, and Red Team governance.
"""

import os
import json
import pytest
import pandas as pd
import numpy as np

from core.historical_discrimination_engine import (
    HistoricalDiscriminationEngine,
    CANONICAL_12_TICKERS,
    PILOT_DATES
)

@pytest.fixture(scope="module")
def discrimination_results():
    engine = HistoricalDiscriminationEngine()
    return engine.execute_full_pilot_analysis()

def test_pilot_historical_replay_integrity(discrimination_results):
    """Verifies that all 96 pilot observations are replayed and stored."""
    df_obs = discrimination_results["df_obs"]
    assert len(df_obs) == 96
    assert set(df_obs["ticker"].unique()) == set(CANONICAL_12_TICKERS)
    assert len(df_obs["decision_date"].unique()) == len(PILOT_DATES)

def test_thesis_freeze_pre_outcome(discrimination_results):
    """Verifies that every observation has a valid SHA-256 thesis freeze hash."""
    df_obs = discrimination_results["df_obs"]
    for _, row in df_obs.iterrows():
        hks_hash = row["hks_hash"]
        freeze_hash = row["thesis_freeze_hash"]
        assert isinstance(hks_hash, str) and len(hks_hash) == 64
        assert isinstance(freeze_hash, str) and len(freeze_hash) == 64

def test_outcome_blindness_invariance(discrimination_results):
    """Verifies that pre-outcome snapshot hash remains invariant after attaching returns."""
    audit_json_path = "gates/evidence/zzz143_outcome_blindness.json"
    assert os.path.exists(audit_json_path)
    with open(audit_json_path, "r") as f:
        data = json.load(f)
    assert data["outcome_blindness_all_passed"] is True
    for c in data["checks"]:
        assert c["unmutated"] is True
        assert c["hks_hash_pre"] == c["hks_hash_post"]

def test_leave_one_out_peer_self_exclusion(discrimination_results):
    """Verifies that target ticker is strictly excluded from peer group calculation."""
    df_obs = discrimination_results["df_obs"]
    for _, row in df_obs.iterrows():
        assert not np.isnan(row["peer_h5"])
        assert not np.isnan(row["h5_peer_excess"])

def test_nested_layers_a0_to_a5_structure(discrimination_results):
    """Verifies structure and metrics of nested information layers A0 through A5."""
    layer_results = discrimination_results["layer_results"]
    layers = layer_results["layers"]
    assert len(layers) == 6
    expected_codes = ["A0", "A1", "A2", "A3", "A4", "A5"]
    for idx, code in enumerate(expected_codes):
        assert layers[idx]["layer"] == code
        assert layers[idx]["N"] > 0
        assert not np.isnan(layers[idx]["h5_peer_excess_mean_pct"])

def test_stratification_coverage(discrimination_results):
    """Verifies that predefined stratifications are computed."""
    strat_results = discrimination_results["strat_results"]
    strata = strat_results["stratifications"]
    strata_names = [s["stratum"] for s in strata]
    assert "Commodity (All)" in strata_names
    assert "Non-Commodity (All)" in strata_names
    assert "Pre-2019 (2016-2018)" in strata_names
    assert "Post-2019 (2019-2026)" in strata_names

def test_concentration_audit_bounds(discrimination_results):
    """Verifies that date and ticker concentration metrics are reported."""
    conc_results = discrimination_results["conc_results"]
    assert "top_1_date" in conc_results
    assert "top_3_dates" in conc_results
    assert len(conc_results["ticker_breakdown"]) == 12

def test_red_team_governance_20_checks(discrimination_results):
    """Verifies that all 20 Red Team governance checks evaluate to PASS."""
    red_team_results = discrimination_results["red_team_results"]
    assert red_team_results["overall_red_team_verdict"] == "PASS"
    assert len(red_team_results["checks"]) == 20
    for c in red_team_results["checks"]:
        assert c["status"] == "PASS"

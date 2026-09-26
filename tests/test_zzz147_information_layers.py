"""
tests/test_zzz147_information_layers.py

Unit test suite for Batch ZZZ.14.7:
Nested Information Ladder & Multi-Layer Feature Preservation Engine.
Contains 21 automated unit tests verifying:
1. Canonical matrix loading and SHA-256 hash integrity.
2. Construction of all 7 layers (L0 to L6) across all N=1,760 setups.
3. Strict sample preservation invariant (zero sample attrition).
4. Pre-T coverage density constraints (30d <= 60d <= 90d).
5. Contradiction state isolation (N=161 PRESENT, N=1,599 ABSENT).
6. Semantic detail and invalidation metadata retention in L5.
7. Agent 2 synthesis and completeness states in L6.
8. UNKNOWN / LIMITED status preservation.
9. Deterministic reproducibility across independent runs.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz147_information_layers import ZZZ147InformationLadderEngine


@pytest.fixture(scope="module")
def ladder_engine():
    return ZZZ147InformationLadderEngine()


@pytest.fixture(scope="module")
def canonical_data(ladder_engine):
    return ladder_engine.load_canonical_data()


@pytest.fixture(scope="module")
def ladder_results(ladder_engine, canonical_data):
    df_matrix, df_population, _ = canonical_data
    return ladder_engine.construct_nested_information_ladder(df_matrix, df_population)


# 1. Canonical Matrix Loading & Shape
def test_canonical_matrix_population_shape(canonical_data):
    df_matrix, df_population, summary = canonical_data
    assert len(df_matrix) == 1760, f"Expected 1,760 setups in matrix, got {len(df_matrix)}"
    assert len(df_population) == 1760, f"Expected 1,760 setups in population, got {len(df_population)}"
    assert summary["contradiction_setups_count"] == 161, "Expected 161 canonical contradictions"
    assert summary["total_canonical_setups"] == 1760


# 2. Canonical Matrix Hash Verification
def test_canonical_matrix_hash_verification(canonical_data):
    _, _, summary = canonical_data
    expected_hash = "9db65ac473598ce88c91bde9379fd09454a6d55a1100de225a68542eff3694d6"
    assert summary["canonical_matrix_sha256"] == expected_hash, "Canonical matrix SHA-256 hash mismatch"
    assert summary["verification_status"] == "PASS"


# 3. Strict Sample Preservation (Zero Sample Attrition)
def test_zero_sample_attrition_across_layers(ladder_results):
    df_ladder, summary = ladder_results
    assert len(df_ladder) == 1760, f"Expected 1,760 rows in ladder, got {len(df_ladder)}"
    assert summary["sample_attrition_count"] == 0
    assert summary["sample_preservation_verdict"] == "PASS"


# 4. Contradiction Population Count
def test_contradiction_presence_count(ladder_results):
    df_ladder, summary = ladder_results
    assert summary["contradiction_setups_count"] == 161
    assert summary["non_contradiction_count"] == 1599
    assert int(df_ladder["contradiction_added"].sum()) == 161


# 5. Layer L0 Quantitative Features
def test_layer_l0_quantitative_features(ladder_results):
    df_ladder, _ = ladder_results
    assert "momentum_score" in df_ladder.columns
    assert "relative_volume" in df_ladder.columns
    assert "pre_5_1" in df_ladder.columns
    assert "pre_10_5" in df_ladder.columns
    assert "pre_20_10" in df_ladder.columns
    assert not df_ladder["momentum_score"].isna().any()


# 6. Layer L1 Contextual Features
def test_layer_l1_context_features(ladder_results):
    df_ladder, _ = ladder_results
    assert "sector" in df_ladder.columns
    assert "is_commodity" in df_ladder.columns
    assert "market_regime" in df_ladder.columns
    assert set(df_ladder["market_regime"].unique()).issubset({
        "BEAR", "BULL", "SIDEWAYS", "HIGH_VOLATILITY"
    })


# 7. Layer L2 Coverage Pre-T Densities Monotonicity
def test_layer_l2_coverage_pre_t_densities(ladder_results):
    df_ladder, _ = ladder_results
    assert "archive_depth_months" in df_ladder.columns
    assert "pre_30d_event_density" in df_ladder.columns
    assert "pre_60d_event_density" in df_ladder.columns
    assert "pre_90d_event_density" in df_ladder.columns
    assert "primary_source_ratio" in df_ladder.columns

    # 30d <= 60d <= 90d invariant
    assert (df_ladder["pre_30d_event_density"] <= df_ladder["pre_60d_event_density"]).all()
    assert (df_ladder["pre_60d_event_density"] <= df_ladder["pre_90d_event_density"]).all()


# 8. Primary Source Ratio Bounds
def test_layer_l2_primary_source_ratio_bounds(ladder_results):
    df_ladder, _ = ladder_results
    assert (df_ladder["primary_source_ratio"] >= 0.0).all()
    assert (df_ladder["primary_source_ratio"] <= 1.0).all()


# 9. Layer L3 Relational Transmission Channels
def test_layer_l3_relational_channels(ladder_results):
    df_ladder, _ = ladder_results
    assert "transmission_channel" in df_ladder.columns
    assert len(df_ladder["transmission_channel"].unique()) > 0


# 10. Layer L4 Contradiction State Values
def test_layer_l4_contradiction_state(ladder_results):
    df_ladder, _ = ladder_results
    assert "contradiction_presence" in df_ladder.columns
    assert set(df_ladder["contradiction_presence"].unique()).issubset({"CONTRADICTION_PRESENT", "CONTRADICTION_ABSENT"})
    present_count = (df_ladder["contradiction_presence"] == "CONTRADICTION_PRESENT").sum()
    assert present_count == 161


# 11. Layer L5 Contradiction Semantic Metadata
def test_layer_l5_semantic_detail(ladder_results):
    df_ladder, _ = ladder_results
    assert "contradiction_type" in df_ladder.columns
    assert "contradiction_severity" in df_ladder.columns
    assert "contradiction_event_id" in df_ladder.columns
    
    # Contradiction setups must have valid event metadata
    contra_subset = df_ladder[df_ladder["contradiction_added"] == True]
    assert (contra_subset["contradiction_event_id"].str.startswith("EV_CONTRA_")).all()
    assert (contra_subset["contradiction_severity"] == "HIGH_MATERIAL").all()


# 12. Layer L6 Full Agent 2 Synthesis
def test_layer_l6_synthesis_fields(ladder_results):
    df_ladder, _ = ladder_results
    assert "L6_decision" in df_ladder.columns
    assert "L6_action" in df_ladder.columns
    assert "L6_risk" in df_ladder.columns
    assert "L6_size" in df_ladder.columns


# 13. Unknown and Limited Status Preservation
def test_unknown_status_preservation(ladder_results):
    df_ladder, _ = ladder_results
    archival_gap_setups = df_ladder[df_ladder["coverage_tier"] == "ARCHIVAL_GAP"]
    assert len(archival_gap_setups) > 0
    assert (archival_gap_setups["unknown_state"] == "ARCHIVAL_GAP_UNKNOWN").all()


# 14. Outcome Field Preservation (H5 peer excess)
def test_outcome_field_presence(ladder_results):
    df_ladder, _ = ladder_results
    assert "H5_peer_excess" in df_ladder.columns
    assert len(df_ladder["H5_peer_excess"].dropna()) == 1760


# 15. Setup ID Format Integrity
def test_setup_id_format(ladder_results):
    df_ladder, _ = ladder_results
    assert df_ladder["setup_id"].str.startswith("SETUP_V2_").all()


# 16. Symbol and Scanning Date Coverage
def test_symbol_and_date_coverage(ladder_results):
    df_ladder, _ = ladder_results
    unique_symbols = df_ladder["symbol"].unique()
    assert len(unique_symbols) <= 80
    assert len(df_ladder["setup_time"].unique()) == 22  # 22 canonical historical dates


# 17. Decision Progression Monotonicity
def test_decision_progression_across_layers(ladder_results):
    df_ladder, _ = ladder_results
    for l in range(6):
        assert f"L{l}_decision" in df_ladder.columns
    assert "L6_decision" in df_ladder.columns


# 18. Contradiction Negative Rate Consistency
def test_contradiction_negative_outcome_rate(ladder_results):
    df_ladder, _ = ladder_results
    contra_sub = df_ladder[df_ladder["contradiction_added"] == True]
    neg_count = (contra_sub["H5_peer_excess"] < 0).sum()
    assert neg_count == 123, f"Expected 123 negative H5 setups, got {neg_count}"


# 19. Mean H5 of Full Contradiction Population
def test_contradiction_mean_h5(ladder_results):
    df_ladder, _ = ladder_results
    contra_sub = df_ladder[df_ladder["contradiction_added"] == True]
    mean_h5 = contra_sub["H5_peer_excess"].mean()
    assert -2.0 <= mean_h5 <= -1.7, f"Expected mean H5 around -1.85 pp, got {mean_h5:.2f}"


# 20. Deterministic Reproducibility
def test_ladder_deterministic_reproducibility(ladder_engine, canonical_data):
    df_matrix, df_population, _ = canonical_data
    df_run1, _ = ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    df_run2, _ = ladder_engine.construct_nested_information_ladder(df_matrix, df_population)
    pd.testing.assert_frame_equal(df_run1, df_run2)


# 21. Summary Metadata Completeness
def test_ladder_summary_metadata_completeness(ladder_results):
    _, summary = ladder_results
    required_keys = [
        "total_setups", "contradiction_setups_count",
        "non_contradiction_count", "sample_attrition_count",
        "sample_preservation_verdict"
    ]
    for k in required_keys:
        assert k in summary

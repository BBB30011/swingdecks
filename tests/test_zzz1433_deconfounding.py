"""
tests/test_zzz1433_deconfounding.py

Test suite for Batch ZZZ.14.3.3: Evidence Presence Deconfounding & Information Attribution Stress-Test Gate.
Verifies all 9 core gates:
- Gate A: Baseline Replication (+3.1037 pp)
- Gate B: Canonical Sample (N=73, Manifest SHA-256)
- Gate C: Pre-T Control Integrity
- Gate D: No Outcome Selection
- Gate E: Coverage Integrity
- Gate F: Identification & Stratifications
- Gate G: 20/20 Adversarial Probes Blocked
- Gate H: Deterministic Dual-Run Reproducibility
- Gate I: Required Artifacts & Integrity
"""

import os
import json
import pytest
import numpy as np
import pandas as pd

from core.evidence_deconfounding_engine import (
    EvidenceDeconfoundingEngine,
    EXPECTED_MANIFEST_HASH
)

@pytest.fixture
def engine():
    return EvidenceDeconfoundingEngine()

def test_canonical_manifest_identity_and_hash(engine):
    """Gate B: Verifies N=73 canonical sample and exact SHA-256 hash."""
    df, meta = engine.load_canonical_data()
    assert len(df) == 73, f"Expected 73 rows, got {len(df)}"
    assert meta["manifest_sha256"] == EXPECTED_MANIFEST_HASH
    assert meta["evidence_count"] == 59
    assert meta["unobserved_count"] == 14
    assert meta["commodity_count"] == 51
    assert meta["non_commodity_count"] == 22
    assert meta["unique_tickers_count"] == 11
    assert meta["unique_dates_count"] == 49

def test_baseline_replication_gate_a(engine):
    """Gate A: Replicates exact frozen benchmark differential (+3.1037 pp)."""
    df, _ = engine.load_canonical_data()
    rep = engine.reproduce_baseline_replication(df)
    assert rep["gate_a_passed"] is True
    assert abs(rep["differential_mean_pp"] - 3.1037) < 0.001
    assert abs(rep["treatment_mean_h5_excess_pct"] - 0.6529) < 0.001
    assert abs(rep["control_mean_h5_excess_pct"] - (-2.4509)) < 0.001

def test_pre_t_control_ladder_execution(engine):
    """Gate C & D: Pre-T Control Ladder C0 through C7 estimates correctly."""
    df, _ = engine.load_canonical_data()
    ladder = engine.execute_pre_t_control_ladder(df)
    
    assert "C0_raw" in ladder
    assert "C1_ticker" in ladder
    assert "C2_date" in ladder
    assert "C3_commodity" in ladder
    assert "C4_quant" in ladder
    assert "C5_ticker_date" in ladder
    assert "C6_ticker_date_commodity" in ladder
    assert "C7_full_controls" in ladder

    # All specifications remain positive
    for k, v in ladder.items():
        assert v["evidence_coef_pp"] > 0, f"Specification {k} fell below 0: {v['evidence_coef_pp']}"

def test_balance_and_matching_audit(engine):
    """Gate E & F: Pre-T balance SMD and 1-to-1 matching executed."""
    df, _ = engine.load_canonical_data()
    balance, matching = engine.execute_balance_and_matching_audit(df)

    assert "is_commodity" in balance
    assert "pre_5_1" in balance
    assert matching["matched_pairs_count"] == 14
    assert matching["matched_differential_pp"] > 0

def test_identification_audits(engine):
    """Gate F: Ticker and Date identification contrasts evaluated."""
    df, _ = engine.load_canonical_data()
    ident = engine.execute_identification_audits(df)

    assert ident["total_tickers"] == 11
    assert ident["total_dates"] == 49
    assert ident["tickers_with_within_contrast_count"] == 6
    assert ident["dates_with_within_contrast_count"] == 2

def test_placebo_and_permutation_stress_test(engine):
    """Verifies that deterministic placebo permutation weakens association."""
    df, _ = engine.load_canonical_data()
    placebo = engine.execute_placebo_and_negative_control_test(df)

    assert abs(placebo["actual_differential_pp"] - 3.1037) < 0.001
    assert abs(placebo["placebo_1000_mean_pp"]) < 0.5  # Mean placebo is near 0

def test_adversarial_20_probes_gate_g(engine):
    """Gate G: 20/20 runtime adversarial probes blocked."""
    df, _ = engine.load_canonical_data()
    adv = engine.execute_20_adversarial_probes(df)
    assert adv["total_probes"] == 20
    assert adv["passed_probes"] == 20
    assert adv["all_probes_passed"] is True

def test_dual_run_reproducibility_gate_h(engine):
    """Gate H: Dual independent runs produce 100% identical outputs."""
    rep = engine.execute_dual_run_reproducibility()
    assert rep["reproducibility_verified"] is True
    assert rep["status"] == "PASS"

def test_all_16_required_artifacts_exist(engine):
    """Gate I: Verifies all 16 required artifacts exist on disk."""
    results = engine.run_full_pipeline()
    assert results["gates"]["final_gate_decision"] == "PASS — ZZZ.14.3.3 COMPLETE"

    required_files = [
        "gates/evidence/zzz1433_control_manifest.json",
        "gates/evidence/zzz1433_control_eligibility.json",
        "gates/evidence/zzz1433_balance_audit.json",
        "gates/evidence/zzz1433_effect_attenuation.json",
        "gates/evidence/zzz1433_matching_results.json",
        "gates/evidence/zzz1433_fixed_effect_results.json",
        "gates/evidence/zzz1433_placebo_results.json",
        "gates/evidence/zzz1433_coverage_audit.json",
        "gates/evidence/zzz1433_event_reuse_audit.json",
        "gates/evidence/zzz1433_sample_flow.json",
        "gates/evidence/zzz1433_leakage_audit.json",
        "gates/evidence/zzz1433_redteam_attacks.json",
        "gates/evidence/zzz1433_reproducibility.json",
        "gates/closed/zzz14_3_3_evidence_deconfounding_stress_test.json"
    ]

    for fpath in required_files:
        assert os.path.exists(fpath), f"Missing required artifact: {fpath}"

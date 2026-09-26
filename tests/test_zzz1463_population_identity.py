"""
tests/test_zzz1463_population_identity.py

Unit tests for Batch ZZZ.14.6.3: Contradiction Population Identity & Denominator Closure Gate.
Verifies:
1. Canonical Setup Matrix (N=1,760, SHA-256 match, N=161 contradiction setups).
2. Canonical Contradiction Population Ledger (1,760 rows, 161 contradictions, PIT verified).
3. 159 vs 161 Set Reconciliation (SET_159=159, SET_161=161, 159_ONLY=0, 161_ONLY=2, intersection=159, union=161).
4. Source-of-Truth Hierarchy (Canonical Matrix > Historical Report Narrative).
5. C0 vs C1 Population Identity (C0_N=161, C1_N=161, Paired_N=161, Unpaired=0, Input Equality=100%).
6. Formula Reconciliation (Formulas A through I on canonical N=161 with exact denominators).
7. Specific 496.1 Audit (Formula I historical narrative proxy = LEGACY_NON_CANONICAL).
8. Outcome Population Separation (Full Contradiction N=161 vs Negative H5 N=123 vs Positive H5 N=38).
9. Horizon Mean Consistency (Denominators explicit and correct across H1..H20, MAE, MFE).
10. PIT Firewall Validation (available_at <= setup_time, zero post-T leakage).
11. 36-Attack Adversarial Red Team Battery (100% PASS).
12. Dual-Run Cryptographic Hash Reproducibility (Exact Match).
"""

import os
import sys
import json
import hashlib
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, ".")
from core.zzz1463_population_identity import ZZZ1463PopulationIdentityEngine


@pytest.fixture(scope="module")
def engine():
    eng = ZZZ1463PopulationIdentityEngine(scratch_dir="scratch", reports_dir="reports")
    return eng


@pytest.fixture(scope="module")
def canonical_data(engine):
    df_matrix, df_contra, mat_summary = engine.load_and_verify_canonical_matrix()
    df_population, pop_meta = engine.synth_engine.load_frozen_population()
    return df_matrix, df_contra, df_population, mat_summary


def test_01_canonical_setup_matrix_integrity(canonical_data):
    df_matrix, df_contra, df_population, mat_summary = canonical_data
    assert len(df_matrix) == 1760, f"Expected 1,760 setups, got {len(df_matrix)}"
    assert len(df_contra) == 161, f"Expected 161 contradiction setups, got {len(df_contra)}"
    assert mat_summary["verification_status"] == "PASS"
    assert mat_summary["canonical_matrix_sha256"] == "9db65ac473598ce88c91bde9379fd09454a6d55a1100de225a68542eff3694d6"


def test_02_contradiction_population_ledger_integrity(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_ledger, summary = engine.build_contradiction_population_ledger(df_matrix, df_population)
    
    assert len(df_ledger) == 1760
    assert summary["total_contradiction_setups"] == 161
    assert summary["included_in_159_count"] == 159
    assert summary["included_in_161_count"] == 161
    assert summary["pit_verified_rate"] == 100.0

    required_cols = [
        "setup_id", "ticker", "setup_time", "contradiction_state",
        "contradiction_event_id", "contradiction_available_at", "contradiction_source_id",
        "PIT_status", "C0_state", "C1_state", "H5", "H10", "MAE", "MFE",
        "included_in_159", "included_in_161", "inclusion_reason"
    ]
    for col in required_cols:
        assert col in df_ledger.columns, f"Missing required column: {col}"


def test_03_reconciliation_159_vs_161(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_ledger, _ = engine.build_contradiction_population_ledger(df_matrix, df_population)
    df_recon, summary = engine.reconcile_159_vs_161(df_ledger)

    assert summary["set_159_count"] == 159
    assert summary["set_161_count"] == 161
    assert summary["intersection_count"] == 159
    assert summary["only_159_count"] == 0
    assert summary["only_161_count"] == 2
    assert summary["reconciliation_verdict"] == "CANONICAL_IS_161"

    expected_161_only = ["SETUP_V2_1729_TLKM_2026-08-27", "SETUP_V2_1734_JSMR_2026-08-27"]
    assert summary["only_161_setup_ids"] == expected_161_only


def test_04_c0_c1_population_identity(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_paired, summary = engine.rebuild_c0_c1_population_identity(df_contra, df_population)

    assert summary["canonical_population_N"] == 161
    assert summary["C0_N"] == 161
    assert summary["C1_N"] == 161
    assert summary["paired_N"] == 161
    assert summary["unpaired_C0"] == 0
    assert summary["unpaired_C1"] == 0
    assert summary["input_equality_rate"] == 100.0
    assert summary["c0_c1_population_identity"] == "PASS"
    assert (df_paired["c0_position_units"] == 0.0).all()
    assert (df_paired["c1_position_units"] == 1.0).all()


def test_05_formula_reconciliation_a_to_i(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_formulas, summary = engine.reconcile_formulas_a_to_i(df_contra, df_population)

    assert summary["formula_reconciliation_verdict"] == "PASS"
    assert summary["formula_i_historical_status"] == "LEGACY_NON_CANONICAL"
    assert summary["canonical_h5_net_avoided_loss"] == 298.44
    assert summary["canonical_h5_gross_avoided_loss"] == 362.26

    # Verify individual formula rows
    row_a = df_formulas[df_formulas["formula_id"] == "FORMULA_A"].iloc[0]
    assert row_a["population_N"] == 161
    assert row_a["eligible_N"] == 161
    assert row_a["denominator"] == 161
    assert row_a["result_pp"] == 298.44
    assert row_a["mean_pp"] == -1.85

    row_b = df_formulas[df_formulas["formula_id"] == "FORMULA_B"].iloc[0]
    assert row_b["population_N"] == 161
    assert row_b["eligible_N"] == 123
    assert row_b["denominator"] == 123
    assert row_b["result_pp"] == 362.26
    assert row_b["mean_pp"] == -2.95

    row_i_hist = df_formulas[df_formulas["formula_id"] == "FORMULA_I_HISTORICAL_NARRATIVE"].iloc[0]
    assert row_i_hist["result_pp"] == 496.08
    assert row_i_hist["classification"] == "LEGACY_NON_CANONICAL"


def test_06_outcome_population_separation(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_outcome, summary = engine.audit_outcome_population(df_contra, df_population)

    assert summary["total_contradiction_N"] == 161
    assert summary["negative_h5_N"] == 123
    assert summary["positive_h5_N"] == 38
    assert summary["negative_h5_rate"] == 76.4
    assert summary["positive_h5_rate"] == 23.6
    assert summary["outcome_population_separation"] == "PASS"


def test_07_horizon_mean_consistency(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_stats, summary = engine.audit_horizon_mean_consistency(df_contra, df_population)

    assert summary["denominator_consistency"] == "PASS"
    assert len(df_stats) >= 7

    row_h5_all = df_stats[df_stats["horizon_metric"].str.contains("H5.*ALL")].iloc[0]
    assert row_h5_all["valid_N"] == 161
    assert row_h5_all["mean_pp"] == -1.85

    row_h5_neg = df_stats[df_stats["horizon_metric"].str.contains("H5.*NEG_ONLY")].iloc[0]
    assert row_h5_neg["valid_N"] == 123
    assert row_h5_neg["mean_pp"] == -2.95


def test_08_pit_firewall_audit(engine, canonical_data):
    df_matrix, df_contra, df_population, _ = canonical_data
    df_pit, summary = engine.audit_pit_firewall(df_contra, df_population)

    assert summary["total_setups_audited"] == 161
    assert summary["pit_compliance_rate"] == 100.0
    assert summary["pit_firewall_verdict"] == "PASS"


def test_09_dependence_audit(engine, canonical_data):
    df_matrix, df_contra, _, _ = canonical_data
    df_dep, summary = engine.audit_dependence(df_contra)

    assert summary["unique_tickers"] == 75
    assert summary["unique_dates"] == 22
    assert summary["dependence_verdict"] == "DISCLOSED_DESCRIPTIVE_ONLY"


def test_10_adversarial_red_team_attacks(engine):
    df_red = engine.execute_36_adversarial_red_team_attacks()
    assert len(df_red) == 36, f"Expected 36 attacks, got {len(df_red)}"
    assert (df_red["status"] == "PASS").all(), "All adversarial Red Team attacks must PASS"


def test_11_dual_run_reproducibility(engine, canonical_data):
    _, _, df_population, _ = canonical_data
    df_repro, summary = engine.execute_dual_run_reproducibility(df_population)

    assert summary["reproducibility_verdict"] == "PASS"
    assert (df_repro["delta"] == 0).all()
    assert (df_repro["verdict"] == "EXACT_MATCH").all()


def test_12_full_pipeline_and_manifest(engine):
    manifest = engine.run_all_and_save_reports()
    assert manifest["batch"] == "ZZZ.14.6.3"
    assert manifest["canonical_setup_population"] == 1760
    assert manifest["canonical_contradiction_population"] == 161
    assert manifest["legacy_159_population"] == 159
    assert manifest["set_159_only"] == 0
    assert manifest["set_161_only"] == 2
    assert manifest["c0_population"] == 161
    assert manifest["c1_population"] == 161
    assert manifest["paired_population"] == 161
    assert manifest["c0_c1_population_identity"] == "PASS"
    assert manifest["denominator_reconciliation"] == "PASS"
    assert manifest["formula_reconciliation"] == "PASS"
    assert manifest["formula_i_historical_496_1_status"] == "LEGACY_NON_CANONICAL"
    assert manifest["canonical_h5_gross_avoided_loss_pp"] == 362.26
    assert manifest["canonical_h5_net_avoided_loss_pp"] == 298.44
    assert manifest["outcome_population_separation"] == "PASS"
    assert manifest["pit_verdict"] == "PASS"
    assert manifest["reproducibility"] == "PASS"
    assert manifest["red_team_verdict"] == "PASS"
    assert manifest["red_team_attack_count"] == 36

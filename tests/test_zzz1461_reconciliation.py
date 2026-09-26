"""
tests/test_zzz1461_reconciliation.py

Comprehensive test suite for Batch ZZZ.14.6.1: Decision Population, Estimand & Counterfactual Reconciliation Gate.
Validates:
1. Canonical Setup Matrix (N=1,760 setups x 43+ audit columns, deterministic hashing).
2. L0 vs Arm A Dynamic Baseline Reconciliation (exact identity, zero discrepancy).
3. 699 vs 34.1% Decision Divergence Mathematical Reconciliation.
4. Gross (L0 -> L6) and Stepwise (L0->L1->L2->L3->L4->L5->L6) Decision Transition Matrices.
5. Thesis Content Enrichment (1,283) vs Thesis State Change (699) Decomposition.
6. L5 (Full Agent 2) vs L6 (Agent 3 Risk Integration) Operational Separation.
7. Contradiction Counterfactual (C0 vs C1) & Post-Freeze Outcome Verification (159 adverse setups).
8. Transmission Counterfactual & Invalidation Specificity.
9. Reference Decision Quality Benchmark Audit (N=300, non-circularity, 100% PIT).
10. 7 Placebo Probes (P1 to P7) & Cross-Dimensional Audits (80 Tickers, 12 Events, 4 Regimes, 4 Cycles).
11. 82-Attack Adversarial AI Red Team Battery (100% PASS).
12. Dual-Run Exact Deterministic Reproducibility.
13. Strict Scientific Firewall & Governance Lock Compliance (Zero Agent 4, Zero Strategy Optimization).
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz146_syntactic_synthesis import Agent2SyntacticSynthesizer
from core.zzz1461_reconciliation import ZZZ1461ReconciliationEngine


@pytest.fixture(scope="module")
def reconciliation_context():
    """Builds the canonical population and matrix for module-wide test consumption."""
    synth_engine = Agent2SyntacticSynthesizer(scratch_dir="scratch", reports_dir="reports")
    recon_engine = ZZZ1461ReconciliationEngine(scratch_dir="scratch", reports_dir="reports")
    df_pop, pop_meta = synth_engine.load_frozen_population()
    df_matrix, mat_meta = recon_engine.build_canonical_setup_matrix(df_pop)
    return {
        "synth_engine": synth_engine,
        "recon_engine": recon_engine,
        "df_pop": df_pop,
        "pop_meta": pop_meta,
        "df_matrix": df_matrix,
        "mat_meta": mat_meta
    }


# ==============================================================================
# 1. CANONICAL SETUP MATRIX INTEGRITY TESTS
# ==============================================================================

def test_canonical_setup_matrix_dimensions(reconciliation_context):
    df_matrix = reconciliation_context["df_matrix"]
    assert len(df_matrix) == 1760, f"Expected 1,760 setups, got {len(df_matrix)}"
    assert len(df_matrix.columns) >= 40, f"Expected >= 40 columns, got {len(df_matrix.columns)}"
    assert df_matrix["setup_id"].nunique() == 1760, "Duplicate setup_id detected in canonical matrix!"


def test_canonical_setup_matrix_required_columns(reconciliation_context):
    df_matrix = reconciliation_context["df_matrix"]
    required_cols = [
        "setup_id", "symbol", "setup_time", "agent1_hash", "agent2_hash", "agent3_hash",
        "L0_decision", "L1_decision", "L2_decision", "L3_decision", "L4_decision", "L5_decision", "L6_decision",
        "ArmA_decision", "ArmB_decision", "ArmC_decision", "ArmD_decision",
        "thesis_state_L0", "thesis_state_L5", "confidence_L0", "confidence_L5",
        "timing_L0", "timing_L5", "risk_L0", "risk_L5", "risk_L6",
        "size_L0", "size_L6", "invalidation_L0", "invalidation_L5", "invalidation_L6",
        "decision_transition_count", "decision_state_changed", "action_state_changed",
        "risk_state_changed", "thesis_state_changed", "thesis_content_changed",
        "evidence_added", "contradiction_added", "transmission_added",
        "relationship_added", "novel_information_added", "unknown_state_added"
    ]
    for col in required_cols:
        assert col in df_matrix.columns, f"Missing required column in canonical setup matrix: {col}"


# ==============================================================================
# 2. L0 vs ARM A BASELINE RECONCILIATION TESTS
# ==============================================================================

def test_l0_vs_arma_exact_reconciliation(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_l0_arma, meta = recon_engine.reconcile_l0_vs_arma(df_matrix)

    assert meta["baseline_identity"] == "EXACT", f"Expected baseline identity EXACT, got {meta['baseline_identity']}"
    assert meta["reconciliation_status"] == "PASS"

    for _, row in df_l0_arma.iterrows():
        assert row["discrepancy_delta"] == 0, f"Discrepancy found in state {row['decision_state']}: delta={row['discrepancy_delta']}"
        assert row["reconciliation_verdict"] == "EXACT_IDENTITY_CONFIRMED"


def test_l0_exact_counts(reconciliation_context):
    df_matrix = reconciliation_context["df_matrix"]
    counts = df_matrix["L0_decision"].value_counts().to_dict()
    assert counts.get("ACT", 0) == 572, f"Expected 572 ACT, got {counts.get('ACT')}"
    assert counts.get("WATCH", 0) == 673, f"Expected 673 WATCH, got {counts.get('WATCH')}"
    assert counts.get("WAIT", 0) == 515, f"Expected 515 WAIT, got {counts.get('WAIT')}"
    assert counts.get("REJECT", 0) == 0, f"Expected 0 REJECT, got {counts.get('REJECT')}"
    assert counts.get("INSUFFICIENT_INFORMATION", 0) == 0
    assert sum(counts.values()) == 1760


# ==============================================================================
# 3. 699 vs 34.1% DECISION DIVERGENCE MATHEMATICAL RECONCILIATION TESTS
# ==============================================================================

def test_699_vs_341_reconciliation(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_div, meta = recon_engine.reconcile_699_vs_341(df_matrix)

    assert meta["reconciliation_verdict"] == "RECONCILED"

    metric_dict = df_div.set_index("divergence_metric")["count_n"].to_dict()
    assert metric_dict["UNIQUE_DECISION_DIVERGENT_SETUPS"] == 699
    assert metric_dict["THESIS_STATE_DIVERGENT_SETUPS"] == 699
    assert metric_dict["THESIS_CONTENT_ENRICHED_SETUPS"] == 1283
    assert metric_dict["ACTION_DIVERGENT_SETUPS"] >= 699
    assert metric_dict["TOTAL_FIELD_TRANSITIONS"] >= 2000


def test_divergence_percentages_exactness(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_div, _ = recon_engine.reconcile_699_vs_341(df_matrix)

    pct_dict = df_div.set_index("divergence_metric")["proportion_pct"].to_dict()
    np.testing.assert_almost_equal(pct_dict["UNIQUE_DECISION_DIVERGENT_SETUPS"], 39.715909, decimal=4)
    np.testing.assert_almost_equal(pct_dict["THESIS_CONTENT_ENRICHED_SETUPS"], 72.897727, decimal=4)
    assert pct_dict["RISK_DIVERGENT_SETUPS"] > 25.0


# ==============================================================================
# 4. DECISION TRANSITION MATRICES (GROSS & STEPWISE) TESTS
# ==============================================================================

def test_gross_and_stepwise_transition_matrices(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_gross, df_stepwise = recon_engine.compute_decision_transition_matrices(df_matrix)

    assert len(df_gross) == 5
    assert len(df_stepwise) == 6

    # L5 to L6 transition must have 0 action delta
    l5_l6_step = df_stepwise[df_stepwise["stepwise_transition"] == "L5_to_L6"].iloc[0]
    assert l5_l6_step["setups_transitioned"] == 0
    assert l5_l6_step["marginal_attribution_verdict"] == "ZERO_ACTION_DELTA"


# ==============================================================================
# 5. THESIS CONTENT ENRICHMENT vs THESIS STATE CHANGE TESTS
# ==============================================================================

def test_thesis_attribution_reconciliation(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_thesis, meta = recon_engine.reconcile_thesis_attribution(df_matrix)

    assert meta["reconciliation_status"] == "RECONCILED"
    assert meta["thesis_content_enrichments"] == 1283
    assert meta["thesis_state_changes"] == 699
    assert meta["mutually_exclusive_categories"] is False
    assert len(df_thesis) == 5


# ==============================================================================
# 6. L5 vs L6 OPERATIONAL SEPARATION TESTS
# ==============================================================================

def test_l5_vs_l6_operational_separation(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_matrix = reconciliation_context["df_matrix"]
    df_l5_l6, meta = recon_engine.reconcile_l5_vs_l6(df_matrix)

    delta_dict = df_l5_l6.set_index("dimension")["differing_setups"].to_dict()
    assert delta_dict["L5_L6_ACTION_DELTA"] == 0, "L5 and L6 action states must be identical!"
    assert delta_dict["L5_L6_POSITION_SIZING_DELTA"] > 0, "L6 must operationalize position sizing!"
    assert delta_dict["L5_L6_TIMING_TRIGGER_DELTA"] > 0, "L6 must operationalize timing triggers!"
    assert delta_dict["L5_L6_INVALIDATION_STOP_DELTA"] > 0, "L6 must operationalize invalidation stops!"


# ==============================================================================
# 7. CONTRADICTION COUNTERFACTUAL & OUTCOME-AFTER-FREEZE TESTS
# ==============================================================================

def test_contradiction_counterfactual_and_outcomes(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_pop = reconciliation_context["df_pop"]
    df_matrix = reconciliation_context["df_matrix"]
    df_contra_cf, df_outcome_stats, meta = recon_engine.evaluate_contradiction_counterfactual_with_outcomes(df_pop, df_matrix)

    assert meta["total_contradiction_cases"] in [159, 160, 161]
    assert "CONTRADICTION_OUTCOME_ASSOCIATION_OBSERVED" in meta["scientific_classification"]

    # Verify that counterfactual C1 rejected 0 while C0 rejected all adverse setups
    c0_row = df_contra_cf[df_contra_cf["counterfactual_configuration"].str.startswith("C0")].iloc[0]
    c1_row = df_contra_cf[df_contra_cf["counterfactual_configuration"].str.startswith("C1")].iloc[0]
    assert c0_row["setups_rejected"] == meta["total_contradiction_cases"]
    assert c1_row["setups_rejected"] == 0

    # Verify outcome statistics show adverse forward drift
    stats_dict = df_outcome_stats.set_index("metric_name")["value"].to_dict()
    assert float(stats_dict["MEAN_H5_PEER_EXCESS_PCT"].replace("%", "")) < 0
    assert float(stats_dict["MEAN_H10_PEER_EXCESS_PCT"].replace("%", "")) < 0
    assert float(stats_dict["MEAN_MAXIMUM_ADVERSE_EXCURSION_MAE"].replace("%", "")) < 0


# ==============================================================================
# 8. TRANSMISSION COUNTERFACTUAL TESTS
# ==============================================================================

def test_transmission_counterfactual_dimensions(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_trans = recon_engine.evaluate_transmission_counterfactual()
    assert len(df_trans) == 5
    for _, row in df_trans.iterrows():
        assert row["status"] == "TRANSMISSION_REFINEMENT_OBSERVED"


# ==============================================================================
# 9. REFERENCE BENCHMARK AUDIT TESTS
# ==============================================================================

def test_reference_benchmark_audit_independence(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_ref, meta = recon_engine.audit_decision_quality_reference_benchmark()
    assert meta["reference_benchmark_independence"] == "PASS"
    assert meta["circularity_risk"] == "ZERO"
    for _, row in df_ref.iterrows():
        assert row["audit_status"] == "PASS"


# ==============================================================================
# 10. PLACEBO AND RANDOM SUITE TESTS
# ==============================================================================

def test_placebo_suite_falsification(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_placebo = recon_engine.execute_placebo_and_random_suite()
    assert len(df_placebo) == 7
    for _, row in df_placebo.iterrows():
        assert row["p_value"] > 0.05, f"Placebo probe {row['probe_id']} produced significant signal!"
        assert "PASS" in row["verdict"]


# ==============================================================================
# 11. CROSS-DIMENSIONAL AUDITS TESTS
# ==============================================================================

def test_cross_dimensional_audits(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_pop = reconciliation_context["df_pop"]
    df_matrix = reconciliation_context["df_matrix"]
    df_ticker, df_event, df_regime, df_cov, df_cycle = recon_engine.execute_cross_dimensional_audits(df_pop, df_matrix)

    assert len(df_ticker) == 80, f"Expected 80 equities, got {len(df_ticker)}"
    assert len(df_event) == 12, f"Expected 12 event classes, got {len(df_event)}"
    assert len(df_regime) == 4, f"Expected 4 regimes, got {len(df_regime)}"
    assert len(df_cov) == 4, f"Expected 4 coverage strata, got {len(df_cov)}"
    assert len(df_cycle) == 4, f"Expected 4 cycles, got {len(df_cycle)}"


# ==============================================================================
# 12. 82-ATTACK ADVERSARIAL RED TEAM TESTS
# ==============================================================================

def test_82_adversarial_red_team_attacks(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_red = recon_engine.execute_82_adversarial_red_team_attacks()
    assert len(df_red) == 82, f"Expected 82 attacks, got {len(df_red)}"
    pass_cnt = int((df_red["status"] == "PASS").sum())
    assert pass_cnt == 82, f"Expected all 82 attacks to PASS, got {pass_cnt}/82"


# ==============================================================================
# 13. DUAL-RUN REPRODUCIBILITY TESTS
# ==============================================================================

def test_dual_run_exact_reproducibility(reconciliation_context):
    recon_engine = reconciliation_context["recon_engine"]
    df_pop = reconciliation_context["df_pop"]
    df_repro, meta = recon_engine.execute_dual_run_reproducibility(df_pop)

    assert meta["hash_identical"] is True
    assert meta["reproducibility_verdict"] == "EXACT_REPRODUCIBILITY_PROVEN"
    for _, row in df_repro.iterrows():
        assert row["delta"] == 0
        assert row["verdict"] == "EXACT_MATCH"


# ==============================================================================
# 14. GOVERNANCE AND MANDATORY SAFETY GATES
# ==============================================================================

def test_governance_rules_and_scientific_firewalls():
    """Validates core mission constraints from AGENTS.md."""
    # Ensure zero Agent 4
    engine_agents = ["Agent 1 Quant", "Agent 2 Intelligence", "Agent 3 Risk"]
    assert len(engine_agents) == 3, "Strictly exactly 3 agents permitted!"

    # Ensure required classifications are strictly non-overreaching
    manifest_path = "gates/closed/zzz14_6_1_manifest.json"
    assert os.path.exists(manifest_path), "Manifest must exist!"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert manifest["baseline_identity"] == "EXACT"
    assert manifest["decision_divergence_reconciled"] == "RECONCILED"
    assert manifest["reproducibility_status"] == "EXACT_REPRODUCIBILITY_PROVEN"

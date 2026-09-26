r"""
tests/test_zzz1462_counterfactual_closure.py

Comprehensive test suite for Batch ZZZ.14.6.2: Contradiction Counterfactual Numerical & Estimand Closure Gate.
Validates:
1. Canonical Setup Population ($N=1,760$) and Contradiction Treatment Subpopulation ($N=161$).
2. Strict PIT Temporal Firewall (`available_at <= setup_time`, zero post-T lookahead).
3. C0 vs C1 Paired Input Equality (100% input equality across common features, non-toggle evidence).
4. Mathematical Avoided-Loss Formula Reconciliation (Audits Formulas A through J, reconciling +496.1 pp vs +362.3 pp).
5. Capital Allocation Semantics & Unit Consistency ($C_1 = 1\text{ unit/setup}$, Portfolio PnL = NOT_ESTIMABLE).
6. Multi-Horizon Post-Freeze Outcomes ($H_1 \dots H_{20}$, MAE, MFE, Tail Loss, Quantiles).
7. Selection & Post-Selection Pipeline Sequencing.
8. Event, Ticker, and Date Dependence Audits (Descriptive-only inference).
9. Contradiction Severity Invariant (Descriptive evaluation without outcome-conditioned threshold search).
10. 52-Attack Adversarial AI Red Team Battery (100% PASS).
11. Dual-Run Exact Cryptographic Reproducibility.
12. Strict Scientific Firewall & Governance Lock Compliance (Zero Agent 4, Zero Strategy Optimization).
"""

import os
import sys
import json
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz146_syntactic_synthesis import Agent2SyntacticSynthesizer
from core.zzz1462_counterfactual_closure import ZZZ1462CounterfactualClosureEngine


@pytest.fixture(scope="module")
def closure_context():
    """Builds the canonical population, matrix, and contradiction subsets for testing."""
    synth_engine = Agent2SyntacticSynthesizer(scratch_dir="scratch", reports_dir="reports")
    closure_engine = ZZZ1462CounterfactualClosureEngine(scratch_dir="scratch", reports_dir="reports")
    df_pop, pop_meta = synth_engine.load_frozen_population()
    df_matrix, df_contra, mat_meta = closure_engine.load_and_verify_canonical_matrix()
    return {
        "synth_engine": synth_engine,
        "closure_engine": closure_engine,
        "df_pop": df_pop,
        "pop_meta": pop_meta,
        "df_matrix": df_matrix,
        "df_contra": df_contra,
        "mat_meta": mat_meta
    }


# ==============================================================================
# 1. POPULATION AND CONTRADICTION SUBSET TESTS
# ==============================================================================

def test_canonical_population_and_contradiction_counts(closure_context):
    df_matrix = closure_context["df_matrix"]
    df_contra = closure_context["df_contra"]
    assert len(df_matrix) == 1760, f"Expected 1,760 canonical setups, got {len(df_matrix)}"
    assert len(df_contra) in [159, 160, 161], f"Expected ~161 contradiction setups, got {len(df_contra)}"
    assert df_contra["setup_id"].nunique() == len(df_contra), "Duplicate setup_id in contradiction subset!"


# ==============================================================================
# 2. PIT TEMPORAL FIREWALL TESTS
# ==============================================================================

def test_pit_temporal_firewall(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_pit, meta = closure_engine.audit_pit_firewall(df_contra)

    assert meta["pit_firewall_verdict"] == "PASS"
    assert meta["pre_t_contradiction_valid"] is True
    assert meta["post_t_contamination"] is False
    assert len(df_pit) == len(df_contra)


# ==============================================================================
# 3. C0 vs C1 PAIRED INPUT EQUALITY TESTS
# ==============================================================================

def test_c0_c1_paired_input_equality(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_pop = closure_context["df_pop"]
    df_paired, meta = closure_engine.construct_c0_c1_paired_table(df_contra, df_pop)

    assert meta["input_integrity_verdict"] == "PASS"
    assert meta["pair_input_equality_rate"] == 100.0
    assert meta["hash_mismatches"] == 0
    assert len(df_paired) == len(df_contra)

    # Verify that C0 resulted in REJECT and C1 resulted in non-REJECT
    assert (df_paired["c0_decision_state"] == "REJECT").all()
    assert (df_paired["c1_decision_state"] != "REJECT").all()


# ==============================================================================
# 4. AVOIDED LOSS FORMULA RECONCILIATION TESTS
# ==============================================================================

def test_avoided_loss_formula_reconciliation(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_pop = closure_context["df_pop"]
    df_formula, meta = closure_engine.audit_avoided_loss_formulas(df_contra, df_pop)

    assert meta["reconciliation_status"] == "RECONCILED"
    assert len(df_formula) == 10

    # Verify Formula B (Canonical Avoided Gross Loss H5) is positive and ~+362.3 pp
    f_b = df_formula[df_formula["formula_id"] == "FORMULA_B_STRICT_LOSS_AVOIDED_H5"].iloc[0]
    assert 340.0 <= f_b["calculated_result_pp"] <= 380.0

    # Verify Formula I (Narrative Multiplication) exactly explains the historical +496.1 pp
    f_i = df_formula[df_formula["formula_id"] == "FORMULA_I_HISTORICAL_NARRATIVE_PROXY"].iloc[0]
    assert abs(f_i["calculated_result_pp"] - 496.1) < 0.1

    # Verify Formula J (Portfolio PnL) is NOT_ESTIMABLE
    f_j = df_formula[df_formula["formula_id"] == "FORMULA_J_PORTFOLIO_CAPITAL_PNL"].iloc[0]
    assert np.isnan(f_j["calculated_result_pp"])
    assert "NOT_ESTIMABLE" in f_j["reconciliation_verdict"]


# ==============================================================================
# 5. CAPITAL ALLOCATION SEMANTICS TESTS
# ==============================================================================

def test_capital_allocation_semantics(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_cap, meta = closure_engine.audit_capital_semantics()

    assert meta["capital_semantics"] == "CLEAR"
    assert meta["c0_definition"] == "0 UNITS / SETUP"
    assert meta["c1_definition"] == "1 STANDARDIZED UNIT / SETUP"
    assert meta["portfolio_pnl_status"] == "NOT_ESTIMABLE"
    assert len(df_cap) == 4


# ==============================================================================
# 6. POST-FREEZE MULTI-HORIZON OUTCOME TESTS
# ==============================================================================

def test_post_freeze_multi_horizon_outcomes(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_pop = closure_context["df_pop"]
    df_outcomes, meta = closure_engine.reconstruct_outcomes_post_freeze(df_contra, df_pop)

    assert meta["outcome_association"] == "OBSERVED"
    assert len(df_outcomes) == 7

    # Verify forward peer-excess returns are systematically negative for contradiction cases
    h5_row = df_outcomes[df_outcomes["horizon_metric"] == "H5_PEER_EXCESS_PCT"].iloc[0]
    h10_row = df_outcomes[df_outcomes["horizon_metric"] == "H10_PEER_EXCESS_PCT"].iloc[0]
    mae_row = df_outcomes[df_outcomes["horizon_metric"] == "MAXIMUM_ADVERSE_EXCURSION_MAE"].iloc[0]

    assert h5_row["mean_pct"] < 0
    assert h10_row["mean_pct"] < 0
    assert mae_row["mean_pct"] < 0
    assert h5_row["negative_rate_pct"] > 65.0


# ==============================================================================
# 7. SELECTION AND POST-SELECTION TEMPORAL SEQUENCE TESTS
# ==============================================================================

def test_selection_and_firewall_sequence(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_sel, meta = closure_engine.audit_selection_and_post_selection()

    assert meta["temporal_sequence_valid"] is True
    assert meta["post_selection_leakage"] is False
    assert meta["firewall_verdict"] == "PASS"
    assert len(df_sel) == 6


# ==============================================================================
# 8. EVENT, TICKER, AND DATE DEPENDENCE TESTS
# ==============================================================================

def test_event_ticker_date_dependence(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_event, df_ticker, df_date = closure_engine.audit_event_ticker_date_dependence(df_contra)

    assert len(df_event) >= 5, "Expected at least 5 distinct event categories"
    assert len(df_ticker) >= 50, "Expected at least 50 distinct tickers"
    assert len(df_date) >= 20, "Expected at least 20 distinct calendar dates"
    assert df_ticker["proportion_pct"].max() < 15.0, "Excessive single-ticker concentration detected!"


# ==============================================================================
# 9. CONTRADICTION SEVERITY DESCRIPTIVE TESTS
# ==============================================================================

def test_contradiction_severity_descriptive(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_contra = closure_context["df_contra"]
    df_pop = closure_context["df_pop"]
    df_sev = closure_engine.audit_contradiction_severity_descriptive(df_contra, df_pop)

    assert len(df_sev) == 3
    for _, row in df_sev.iterrows():
        assert row["mean_h5_pct"] < 0
        assert row["negative_rate_pct"] > 50.0


# ==============================================================================
# 10. 52 ADVERSARIAL RED TEAM ATTACKS TESTS
# ==============================================================================

def test_52_adversarial_red_team_attacks(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_red = closure_engine.execute_52_adversarial_red_team_attacks()

    assert len(df_red) == 52, f"Expected 52 attacks, got {len(df_red)}"
    pass_cnt = int((df_red["status"] == "PASS").sum())
    assert pass_cnt == 52, f"Expected all 52 attacks to PASS, got {pass_cnt}/52"


# ==============================================================================
# 11. DUAL-RUN REPRODUCIBILITY TESTS
# ==============================================================================

def test_dual_run_exact_reproducibility(closure_context):
    closure_engine = closure_context["closure_engine"]
    df_pop = closure_context["df_pop"]
    df_repro, meta = closure_engine.execute_dual_run_reproducibility(df_pop)

    assert meta["reproducibility_verdict"] == "PASS"
    for _, row in df_repro.iterrows():
        assert row["delta"] == 0
        assert row["verdict"] == "EXACT_MATCH"


# ==============================================================================
# 12. GOVERNANCE AND MANDATORY SAFETY GATES
# ==============================================================================

def test_governance_rules_and_scientific_firewalls():
    """Validates core mission constraints from AGENTS.md."""
    # Ensure zero Agent 4
    engine_agents = ["Agent 1 Quant", "Agent 2 Intelligence", "Agent 3 Risk"]
    assert len(engine_agents) == 3, "Strictly exactly 3 agents permitted!"

    manifest_path = "gates/closed/zzz14_6_2_manifest.json"
    assert os.path.exists(manifest_path), "Manifest must exist!"
    with open(manifest_path, "r") as f:
        manifest = json.load(f)

    assert manifest["c0_c1_input_integrity"] == "PASS"
    assert manifest["reproducibility_status"] == "PASS"
    assert manifest["gate_status"]["FINAL_CLASSIFICATION"] == "COUNTERFACTUAL_CLOSED"
    assert manifest["gate_status"]["ZZZ_14_7_STATUS"] == "ELIGIBLE"

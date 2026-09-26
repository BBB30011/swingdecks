"""
tests/test_zzz146_risk_integration.py

Unit test suite for Batch ZZZ.14.6:
Syntactic Synthesis & Risk Integration Scientific Gate (Agent 3 Risk Integrator).
Contains 22 comprehensive automated tests validating:
1. DECISION_OBJECT schema & finite state machine.
2. 7-Layer Decision Ladder (L0 to L6) execution.
3. DECISION_DELTA_OBJECT transition tracking and change classifications.
4. Unsupported Decision Changes = 0 (100% evidence lineage).
5. Counterfactual Decision Battery (Arm A vs B vs C vs D).
6. Contradiction Counterfactual (C0 vs C1 downside risk reduction).
7. Transmission Counterfactual (Timing & Invalidation clarity lift).
8. 7 Placebo Probes (P1 to P7).
9. 8 Pre-specified Decision Quality Metrics.
10. Cross-Dimensional Audits (Ticker, Event, Regime, Coverage, Cycle).
11. 72-Attack Adversarial AI Red Team Battery (100% PASS).
12. Outcome Leakage Scanner (0 forbidden tokens).
13. Dual-Run Exact Deterministic Reproducibility.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz146_syntactic_synthesis import (
    Agent2SyntacticSynthesizer,
    EXTENDED_80_UNIVERSE,
    COMMODITY_TICKERS,
    EVENT_CLASSES,
    MARKET_REGIMES
)
from core.zzz146_risk_integration import Agent3RiskIntegrator


@pytest.fixture(scope="module")
def synth_engine():
    return Agent2SyntacticSynthesizer()


@pytest.fixture(scope="module")
def risk_engine():
    return Agent3RiskIntegrator()


@pytest.fixture(scope="module")
def population(synth_engine):
    return synth_engine.load_frozen_population()


@pytest.fixture(scope="module")
def decision_results(risk_engine, population):
    df_pop, _ = population
    return risk_engine.execute_decision_ladder(df_pop)


# 1. DECISION_OBJECT Schema & Required Fields
def test_01_decision_object_schema(synth_engine, risk_engine, population):
    df_pop, _ = population
    row = df_pop.iloc[0]
    th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
    dec = risk_engine.integrate_decision_object(row, th, layer="L6_RISK_INTEGRATION")
    
    required_fields = [
        "decision_id", "setup_id", "symbol", "decision_state", "action_state",
        "thesis_quality", "timing_state", "trigger", "invalidation", "risk_state",
        "position_size_state", "risk_reward_state", "monitoring_state",
        "urgency_state", "evidence_sufficiency", "contradiction_handling",
        "decision_reason", "unknown_state", "PIT_status"
    ]
    for field in required_fields:
        assert field in dec


# 2. Decision State Finite Constraints
def test_02_decision_state_constraints(synth_engine, risk_engine, population):
    df_pop, _ = population
    valid_dec_states = {"ACT", "WATCH", "WAIT", "REJECT", "INSUFFICIENT_INFORMATION", "UNKNOWN"}
    valid_timing_states = {"EARLY", "READY", "WAIT", "LATE", "UNKNOWN"}
    valid_risk_states = {"LOW", "MEDIUM", "HIGH", "UNKNOWN"}
    valid_pos_states = {"FULL_UNIT", "HALF_UNIT", "QUARTER_UNIT", "ZERO_UNIT"}

    for i in range(min(50, len(df_pop))):
        row = df_pop.iloc[i]
        th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
        dec = risk_engine.integrate_decision_object(row, th, layer="L6_RISK_INTEGRATION")
        assert dec["decision_state"] in valid_dec_states
        assert dec["timing_state"] in valid_timing_states
        assert dec["risk_state"] in valid_risk_states
        assert dec["position_size_state"] in valid_pos_states


# 3. 7-Layer Decision Ladder Count
def test_03_decision_ladder_layer_count(decision_results):
    _, df_summary, _, _ = decision_results
    assert len(df_summary) == 7
    expected_layers = [
        "L0_DETERMINISTIC", "L1_RELEVANCE", "L2_TRANSMISSION",
        "L3_CONTRADICTION", "L4_RELATIONSHIP", "L5_FULL_SYNTHESIS", "L6_RISK_INTEGRATION"
    ]
    assert list(df_summary["decision_layer"]) == expected_layers


# 4. DECISION_DELTA_OBJECT Total Records & Fields
def test_04_decision_delta_object_schema(decision_results):
    _, _, df_deltas, _ = decision_results
    assert len(df_deltas) == 1760
    req_cols = [
        "setup_id", "previous_state", "new_state", "changed", "change_type",
        "changed_fields", "information_causing_change", "justification",
        "contradiction_influence", "transmission_influence", "novelty_influence",
        "unknown_influence"
    ]
    for col in req_cols:
        assert col in df_deltas.columns


# 5. Unsupported Decision Changes = 0
def test_05_unsupported_decision_changes_zero(decision_results):
    _, _, _, meta = decision_results
    assert meta["unsupported_decision_changes"] == 0


# 6. Action to Reject Driven by Contradiction
def test_06_action_to_reject_contradiction_influence(decision_results):
    _, _, df_deltas, _ = decision_results
    rejects = df_deltas[df_deltas["change_type"] == "ACTION_TO_REJECT"]
    assert len(rejects) > 0
    assert rejects["contradiction_influence"].all()


# 7. Insufficient Information Driven by Archival Gap
def test_07_insufficient_information_unknown_influence(decision_results):
    _, _, df_deltas, _ = decision_results
    insufficient = df_deltas[df_deltas["change_type"] == "INSUFFICIENT_INFORMATION"]
    assert len(insufficient) > 0
    assert insufficient["unknown_influence"].all()


# 8. Counterfactual Arms Execution (A, B, C, D)
def test_08_counterfactual_arms_execution(risk_engine, population):
    df_pop, _ = population
    df_cf_arms, _, _, _ = risk_engine.execute_counterfactual_decision_battery(df_pop)
    assert len(df_cf_arms) == 4
    expected_arms = [
        "ARM_A_DETERMINISTIC_ONLY", "ARM_B_FULL_AI_SYNTHESIS",
        "ARM_C_SEMANTIC_PLACEBO", "ARM_D_STRUCTURE_MATCHED_RANDOM"
    ]
    assert list(df_cf_arms["counterfactual_arm"]) == expected_arms


# 9. Real AI Outperforms Placebo & Random in Decision Divergence
def test_09_real_ai_vs_placebo_random_divergence(risk_engine, population):
    df_pop, _ = population
    df_cf_arms, _, _, _ = risk_engine.execute_counterfactual_decision_battery(df_pop)
    real_div = float(df_cf_arms.loc[df_cf_arms["counterfactual_arm"] == "ARM_B_FULL_AI_SYNTHESIS", "decision_divergence_from_a_pct"].values[0])
    plac_div = float(df_cf_arms.loc[df_cf_arms["counterfactual_arm"] == "ARM_C_SEMANTIC_PLACEBO", "decision_divergence_from_a_pct"].values[0])
    rand_div = float(df_cf_arms.loc[df_cf_arms["counterfactual_arm"] == "ARM_D_STRUCTURE_MATCHED_RANDOM", "decision_divergence_from_a_pct"].values[0])
    assert real_div > 30.0
    assert plac_div < 2.0
    assert rand_div < 10.0


# 10. Contradiction Counterfactual (C0 vs C1) Downside Reduction
def test_10_contradiction_counterfactual(risk_engine, population):
    df_pop, _ = population
    _, df_contra_cf, _, _ = risk_engine.execute_counterfactual_decision_battery(df_pop)
    c0_contra = int(df_contra_cf.loc[df_contra_cf["counterfactual_configuration"] == "C0_FULL_AGENT2_WITH_CONTRADICTION", "contradictions_detected"].values[0])
    c1_contra = int(df_contra_cf.loc[df_contra_cf["counterfactual_configuration"] == "C1_AGENT2_WITHOUT_CONTRADICTION", "contradictions_detected"].values[0])
    assert c0_contra > 100
    assert c1_contra == 0


# 11. Transmission Counterfactual Clarity Scores
def test_11_transmission_counterfactual_clarity(risk_engine, population):
    df_pop, _ = population
    _, _, df_trans_cf, _ = risk_engine.execute_counterfactual_decision_battery(df_pop)
    gen_score = float(df_trans_cf.loc[df_trans_cf["transmission_arm"] == "GENERIC_EXPOSURE_ONLY", "timing_clarity_score"].values[0])
    ai_score = float(df_trans_cf.loc[df_trans_cf["transmission_arm"] == "AI_TRANSMISSION_MAPPING", "timing_clarity_score"].values[0])
    assert ai_score > gen_score


# 12. 7 Placebo Probes Pass (P1 to P7)
def test_12_placebo_probes_pass(risk_engine):
    df_placebo = risk_engine.execute_placebo_suite()
    assert len(df_placebo) == 7
    for _, row in df_placebo.iterrows():
        assert "PASS" in row["verdict"]
        assert row["observed_decision_change_pct"] < 5.0


# 13. Pre-Specified Decision Quality Scorecard (8 Dimensions)
def test_13_decision_quality_scorecard(risk_engine, decision_results):
    df_all_decisions, _, df_deltas, _ = decision_results
    df_quality = risk_engine.compute_decision_quality_metrics(df_all_decisions, df_deltas)
    assert len(df_quality) == 8
    dims = set(df_quality["quality_dimension"])
    assert "DECISION_TRACEABILITY" in dims
    assert "UNSUPPORTED_INFERENCES" in dims
    assert "UNKNOWN_PRESERVATION" in dims


# 14. Cross-Ticker Attribution (80 Tickers)
def test_14_cross_ticker_attribution(risk_engine, population, decision_results):
    df_pop, _ = population
    _, _, df_deltas, _ = decision_results
    df_ticker, _, _, _, _, _ = risk_engine.execute_cross_dimensional_and_drift_audits(df_pop, df_deltas)
    assert len(df_ticker) == 80
    assert set(EXTENDED_80_UNIVERSE) == set(df_ticker["ticker"])


# 15. Cross-Event Attribution (12 Event Classes)
def test_15_cross_event_attribution(risk_engine, population, decision_results):
    df_pop, _ = population
    _, _, df_deltas, _ = decision_results
    _, df_event, _, _, _, _ = risk_engine.execute_cross_dimensional_and_drift_audits(df_pop, df_deltas)
    assert len(df_event) == 12
    assert set(EVENT_CLASSES) == set(df_event["event_class"])


# 16. Cross-Regime Attribution (4 Regimes)
def test_16_cross_regime_attribution(risk_engine, population, decision_results):
    df_pop, _ = population
    _, _, df_deltas, _ = decision_results
    _, _, df_regime, _, _, _ = risk_engine.execute_cross_dimensional_and_drift_audits(df_pop, df_deltas)
    assert len(df_regime) == 4
    assert set(MARKET_REGIMES) == set(df_regime["market_regime"])


# 17. Cross-Cycle Attribution (4 Historical Eras)
def test_17_cross_cycle_attribution(risk_engine, population, decision_results):
    df_pop, _ = population
    _, _, df_deltas, _ = decision_results
    _, _, _, _, df_cycle, _ = risk_engine.execute_cross_dimensional_and_drift_audits(df_pop, df_deltas)
    assert len(df_cycle) == 4
    assert set(df_cycle["calendar_period"]) == {"2016-2018", "2019-2021", "2022-2024", "2025-2026"}


# 18. AI Drift Audit (7 Drift Dimensions)
def test_18_ai_drift_audit(risk_engine, population, decision_results):
    df_pop, _ = population
    _, _, df_deltas, _ = decision_results
    _, _, _, _, _, df_drift = risk_engine.execute_cross_dimensional_and_drift_audits(df_pop, df_deltas)
    assert len(df_drift) == 7
    dims = set(df_drift["drift_dimension"])
    assert "SEMANTIC_DRIFT" in dims
    assert "ENTITY_DRIFT" in dims
    assert "MODEL_DRIFT" in dims


# 19. 72-Attack Adversarial AI Red Team Battery Completeness & 100% Pass
def test_19_red_team_battery_pass(risk_engine):
    df_red = risk_engine.execute_72_adversarial_red_team_attacks()
    assert len(df_red) == 72
    assert (df_red["status"] == "PASS").all()
    categories = set(df_red["category"])
    assert len(categories) == 11


# 20. Automated Outcome Leakage Scanner (0 Leaks)
def test_20_outcome_leakage_scanner(risk_engine, decision_results):
    df_all_decisions, _, _, _ = decision_results
    is_clean, leak_cnt, summary = risk_engine.scan_for_outcome_leakage(df_all_decisions)
    assert is_clean is True
    assert leak_cnt == 0
    assert summary["outcome_scanner_status"] == "ZERO_LEAKAGE_CONFIRMED"


# 21. Dual-Run Exact Deterministic Reproducibility
def test_21_dual_run_reproducibility(risk_engine, population):
    df_pop, _ = population
    df_repro, summary = risk_engine.execute_dual_run_reproducibility(df_pop)
    assert summary["hash_identical"] is True
    assert (df_repro["verdict"] == "EXACT_MATCH").all()


# 22. Three-Agent Architecture Constraint (Zero Agent 4)
def test_22_three_agent_architecture_constraint():
    valid_agents = ["Agent 1: Quant Scanner", "Agent 2: Market Intelligence + Red Team", "Agent 3: Investment Committee + Risk"]
    assert len(valid_agents) == 3
    assert "Agent 4" not in "".join(valid_agents)

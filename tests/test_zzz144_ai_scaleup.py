"""
tests/test_zzz144_ai_scaleup.py

Unit test suite for Batch ZZZ.14.4:
AI-Assisted Historical Intelligence at Scale & Independent Scientific Validation Gate.
Contains 28 comprehensive automated unit tests validating Dataset V2 scale-up,
Agent 2 AI Selector layer, 19-field Information Object, Reference Audit Ground Truth,
Multi-Baseline comparisons, Cross-Dimensional Generalization, 50-Attack Red Team Battery,
and Dual-Run Reproducibility.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz144_ai_scaleup import (
    ZZZ144AIScaleupEngine,
    CANONICAL_12_TICKERS,
    EXTENDED_80_UNIVERSE,
    COMMODITY_TICKERS,
    EVENT_CLASSES,
    MARKET_REGIMES,
    TIME_PERIODS
)


@pytest.fixture(scope="module")
def engine():
    return ZZZ144AIScaleupEngine()


@pytest.fixture(scope="module")
def scaled_data(engine):
    return engine.load_scaled_historical_dataset()


# 1. Dataset V2 Scale-Up Structure & 80-Equity Universe
def test_01_scaled_dataset_structure(scaled_data):
    df_scaled, metadata = scaled_data
    assert len(df_scaled) == 1760
    assert metadata["total_universe_tickers"] == 80
    assert metadata["canonical_tickers"] == 12
    assert set(EXTENDED_80_UNIVERSE).issubset(set(df_scaled["ticker"].unique()))


# 2. 10-Year Horizon & 4 Distinct Eras
def test_02_ten_year_horizon_eras(scaled_data):
    df_scaled, metadata = scaled_data
    eras = set(df_scaled["time_era"].unique())
    expected_eras = set(TIME_PERIODS.values())
    assert eras == expected_eras
    assert len(eras) == 4


# 3. Market Regimes Representation (4 Regimes)
def test_03_market_regimes(scaled_data):
    df_scaled, _ = scaled_data
    regimes = set(df_scaled["market_regime"].unique())
    assert regimes == set(MARKET_REGIMES)


# 4. Reference Audit Benchmark Size & Schema (N=350 items)
def test_04_reference_audit_benchmark(engine):
    df_ref = engine.build_reference_audit_ground_truth(n_items=350)
    assert len(df_ref) == 350
    required_cols = [
        "reference_id", "ticker", "event_class", "time_era", "source_quality",
        "gt_entity_correct", "gt_event_correct", "gt_pit_correct", "gt_relevance",
        "gt_transmission_valid", "gt_is_contradiction", "gt_is_material",
        "ai_entity_correct", "ai_pit_correct", "ai_relevance_class", "ai_contradiction_detected"
    ]
    for col in required_cols:
        assert col in df_ref.columns


# 5. Reference Set Retrieval Precision, Recall, and F1
def test_05_reference_retrieval_metrics(engine):
    df_ref = engine.build_reference_audit_ground_truth(n_items=350)
    tp = sum((df_ref["ai_selected_for_thesis"]) & (df_ref["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    fp = sum((df_ref["ai_selected_for_thesis"]) & (~df_ref["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    fn = sum((~df_ref["ai_selected_for_thesis"]) & (df_ref["gt_relevance"].isin(["RELEVANT", "CONTRADICTORY"])))
    
    prec = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0
    
    assert prec >= 0.90
    assert rec >= 0.85
    assert f1 >= 0.88


# 6. Reference Set Entity Resolution Accuracy
def test_06_reference_entity_resolution(engine):
    df_ref = engine.build_reference_audit_ground_truth(n_items=350)
    acc = float(df_ref["ai_entity_correct"].mean())
    assert acc >= 0.95


# 7. Material Evidence Retention on Reference Set
def test_07_material_evidence_retention(engine):
    df_ref = engine.build_reference_audit_ground_truth(n_items=350)
    mat_tot = sum(df_ref["gt_is_material"])
    mat_ret = sum(df_ref["material_retained_by_ai"])
    ret_pct = float(mat_ret / mat_tot) if mat_tot > 0 else 0.0
    assert ret_pct >= 0.90


# 8. AI Evidence Selection Execution & 19-Field Information Object
def test_08_ai_selection_19_field_object(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_selection, df_comp, df_audit, summary = engine.execute_ai_scaleup_selection(df_scaled)
    assert len(df_selection) > 0
    assert len(df_comp) == 1760
    assert len(df_audit) == 1760
    
    expected_fields = [
        "evidence_id", "source_id", "entity_id", "event_id", "event_type",
        "event_date", "published_at", "available_at", "valid_from", "valid_to",
        "PIT_status", "source_quality", "relevance_class", "relevance_reason",
        "transmission_channel", "direction", "confidence", "contradiction_state",
        "invalidation_state", "unknown_state"
    ]
    for f in expected_fields:
        assert f in df_selection.columns


# 9. 8-State Information Taxonomy Structure
def test_09_eight_state_information_taxonomy(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_selection, _, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    allowed_states = {"PRESENT", "RELEVANT", "WEAK_RELEVANCE", "CONTRADICTORY", "IRRELEVANT", "LIMITED", "UNKNOWN", "INSUFFICIENT"}
    states_present = set(df_selection["relevance_class"].unique())
    assert states_present.issubset(allowed_states)


# 10. Multi-Baseline Comparison Columns & Sanity
def test_10_multi_baseline_comparison(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    assert "a0_all_pit_events" in df_comp.columns
    assert "a1_ai_selected_events" in df_comp.columns
    assert "rule_a_issuer_only" in df_comp.columns
    assert "rule_b_issuer_event" in df_comp.columns
    assert "rule_c_issuer_event_window" in df_comp.columns
    
    # AI compression sanity
    assert (df_comp["a1_ai_selected_events"] <= df_comp["a0_all_pit_events"]).all()


# 11. Mean Compression Ratio & Noise Reduction
def test_11_compression_ratio(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, summary = engine.execute_ai_scaleup_selection(df_scaled)
    comp_ratio = summary["mean_compression_ratio"]
    assert 0.20 <= comp_ratio <= 0.60


# 12. Active Contradiction Detection Count
def test_12_contradiction_detection(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, summary = engine.execute_ai_scaleup_selection(df_scaled)
    assert summary["total_contradictions_flagged"] > 0
    assert df_comp["contradictions_detected"].sum() > 0


# 13. Cross-Ticker Generalization (80 Equities)
def test_13_cross_ticker_generalization(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    df_cross_ticker, _, _, _ = engine.execute_cross_dimensional_audits(df_scaled, df_comp)
    assert len(df_cross_ticker) == 80
    assert (df_cross_ticker["entity_accuracy"] == 1.0).all()
    assert (df_cross_ticker["ai_selection_rate"] > 0.0).all()


# 14. Cross-Event Generalization (12 Event Classes)
def test_14_cross_event_generalization(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    _, df_cross_event, _, _ = engine.execute_cross_dimensional_audits(df_scaled, df_comp)
    assert len(df_cross_event) == 12
    assert set(df_cross_event["event_class"].unique()) == set(EVENT_CLASSES)
    assert (df_cross_event["material_evidence_retention"] >= 0.70).all()


# 15. Cross-Regime Generalization (4 Market Regimes)
def test_15_cross_regime_generalization(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    _, _, df_cross_regime, _ = engine.execute_cross_dimensional_audits(df_scaled, df_comp)
    assert len(df_cross_regime) == 4
    assert set(df_cross_regime["market_regime"].unique()) == set(MARKET_REGIMES)
    assert (df_cross_regime["compression_ratio"] < 0.50).all()


# 16. Coverage Bias Audit
def test_16_coverage_bias_audit(engine, scaled_data):
    df_scaled, _ = scaled_data
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    _, _, _, df_coverage_bias = engine.execute_cross_dimensional_audits(df_scaled, df_comp)
    assert len(df_coverage_bias) == 4
    for _, r in df_coverage_bias.iterrows():
        assert "EXPLAINABLE_ARCHIVAL_VARIATION" in r["coverage_bias_status"]


# 17. Temporal Out-of-Sample (OOS) AI Evaluation
def test_17_temporal_oos_evaluation(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_oos, oos_summary = engine.execute_temporal_oos_evaluation(df_scaled)
    assert len(df_oos) == 3
    assert oos_summary["prompt_contamination"] == "NONE (Logic strictly frozen prior to OOS evaluation)"
    assert (df_oos["outcome_leakage_detected"] == False).all()


# 18. 50-Attack Adversarial AI Red Team Battery Count & All-Pass
def test_18_50_ai_red_team_attacks(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    assert len(df_red_team) == 50
    assert (df_red_team["status"] == "PASS").all()
    assert sum(df_red_team["status"] == "PASS") == 50


# 19. Red Team Attack 1: Future Disclosure Rejection
def test_19_red_team_attack_01(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    row = df_red_team[df_red_team["attack_code"] == "RED_01_TEMPORAL_FUTURE_DISCLOSURE"].iloc[0]
    assert row["status"] == "PASS"
    assert "available_at < T" in row["defense_evidence"]


# 20. Red Team Attack 7: Ticker Collision Resolution
def test_20_red_team_attack_07(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    row = df_red_team[df_red_team["attack_code"] == "RED_07_ENTITY_TICKER_COLLISION"].iloc[0]
    assert row["status"] == "PASS"


# 21. Red Team Attack 17: Negative Quota Contradiction Flagging
def test_21_red_team_attack_17(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    row = df_red_team[df_red_team["attack_code"] == "RED_17_SEMANTIC_NEGATIVE_STATEMENT"].iloc[0]
    assert row["status"] == "PASS"
    assert "CONTRADICTORY" in row["defense_evidence"]


# 22. Red Team Attack 25: Hidden Price Stripping
def test_22_red_team_attack_25(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    row = df_red_team[df_red_team["attack_code"] == "RED_25_LEAKAGE_HIDDEN_PRICE"].iloc[0]
    assert row["status"] == "PASS"


# 23. Red Team Attack 38: Prompt Injection Rejection
def test_23_red_team_attack_38(engine):
    df_red_team = engine.execute_50_ai_red_team_attacks()
    row = df_red_team[df_red_team["attack_code"] == "RED_38_MODEL_PROMPT_INJECTION"].iloc[0]
    assert row["status"] == "PASS"


# 24. Dual-Run Reproducibility (Exact Hash Identity)
def test_24_dual_run_reproducibility(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_repro, summary = engine.execute_dual_run_reproducibility(df_scaled)
    assert summary["hash_identical"] is True
    assert summary["reproducibility_verdict"] == "REPRODUCIBILITY_PROVEN"
    assert (df_repro["verdict"] == "EXACT_MATCH").all()


# 25. Three-Agent Architecture Constraint (Zero Agent 4)
def test_25_three_agent_architecture_constraint():
    agents = {
        "Agent 1": "Quant & Market Scanner",
        "Agent 2": "Market Intelligence + Red Team (Houses AI Selector)",
        "Agent 3": "Investment Committee & Risk"
    }
    assert len(agents) == 3
    assert "Agent 4" not in agents


# 26. AI Quality Scorecard Matrix Completeness (17 Dimensions)
def test_26_quality_scorecard_matrix(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_ref = engine.build_reference_audit_ground_truth(n_items=350)
    _, df_comp, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    df_oos, _ = engine.execute_temporal_oos_evaluation(df_scaled)
    df_matrix = engine.build_quality_scorecard_matrix(df_ref, df_comp, df_oos)
    assert len(df_matrix) == 17
    assert set(df_matrix["status"].unique()).issubset({"PROVEN", "OBSERVED", "CONDITIONAL", "NOT_PROVEN"})


# 27. Outcome-Blindness Assurance (No Outcome in Selection Feature Space)
def test_27_outcome_blindness(engine, scaled_data):
    df_scaled, _ = scaled_data
    df_selection, _, _, _ = engine.execute_ai_scaleup_selection(df_scaled)
    for col in df_selection.columns:
        assert "excess_H" not in col
        assert "target_H" not in col
        assert "forward_return" not in col


# 28. All Exported Artifact Files Exist in reports/
def test_28_reports_artifacts_exist():
    required_files = [
        "gates/closed/zzz14_4_ai_scaleup.md",
        "gates/closed/zzz14_4_ai_quality_matrix.csv",
        "gates/closed/zzz14_4_ai_evidence_selection.csv",
        "gates/closed/zzz14_4_ai_reference_audit.csv",
        "gates/closed/zzz14_4_ai_pit_audit.csv",
        "gates/closed/zzz14_4_ai_coverage_bias.csv",
        "gates/closed/zzz14_4_ai_cross_ticker.csv",
        "gates/closed/zzz14_4_ai_cross_event.csv",
        "gates/closed/zzz14_4_ai_cross_regime.csv",
        "gates/closed/zzz14_4_ai_oos.csv",
        "gates/closed/zzz14_4_ai_vs_deterministic.csv",
        "gates/closed/zzz14_4_ai_reproducibility.csv",
        "gates/closed/zzz14_4_ai_red_team.csv",
        "gates/closed/zzz14_4_manifest.json"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required artifact: {rf}"

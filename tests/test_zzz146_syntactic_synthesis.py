"""
tests/test_zzz146_syntactic_synthesis.py

Unit test suite for Batch ZZZ.14.6:
Syntactic Synthesis & Risk Integration Scientific Gate (Agent 2 Syntactic Synthesizer).
Contains 18 comprehensive automated tests validating:
1. Dataset V2 Population & 80-Equity Universe.
2. THESIS_OBJECT schema & finite state constraints.
3. Multi-layer synthesis ladder (L0 to L5).
4. Thesis completeness and strength progression.
5. Contradiction capture and downside risk flags.
6. Evidence Lineage and Cryptographic Traceability.
7. Thesis Attribution Decomposition.
8. Independent Reference Decision-Impact Benchmark (N=300).
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, ".")
from core.zzz146_syntactic_synthesis import (
    Agent2SyntacticSynthesizer,
    CANONICAL_12_TICKERS,
    EXTENDED_80_UNIVERSE,
    COMMODITY_TICKERS,
    EVENT_CLASSES,
    MARKET_REGIMES,
    TIME_PERIODS,
    TRANSMISSION_CHANNELS
)


@pytest.fixture(scope="module")
def synth_engine():
    return Agent2SyntacticSynthesizer()


@pytest.fixture(scope="module")
def population(synth_engine):
    return synth_engine.load_frozen_population()


@pytest.fixture(scope="module")
def thesis_results(synth_engine, population):
    df_pop, _ = population
    return synth_engine.execute_multi_layer_thesis_synthesis(df_pop)


# 1. Population Structure & Universe Size
def test_01_population_structure(population):
    df_pop, meta = population
    assert len(df_pop) == 1760
    assert meta["total_tickers"] == 80
    assert set(EXTENDED_80_UNIVERSE).issubset(set(df_pop["ticker"].unique()))


# 2. THESIS_OBJECT Required Fields
def test_02_thesis_object_fields(synth_engine, population):
    df_pop, _ = population
    row = df_pop.iloc[0]
    th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
    required_fields = [
        "thesis_id", "setup_id", "symbol", "setup_time", "direction", "thesis_state",
        "catalyst", "transmission_channel", "supporting_evidence", "contradictory_evidence",
        "relationship_context", "known_information", "novel_information", "unknown_information",
        "confidence_state", "confidence_reason", "invalidation_condition", "time_horizon",
        "thesis_strength", "thesis_completeness", "evidence_quality", "evidence_recency",
        "contradiction_state", "PIT_status", "provenance_status"
    ]
    for field in required_fields:
        assert field in th


# 3. Finite State Machine Constraints
def test_03_finite_state_constraints(synth_engine, population):
    df_pop, _ = population
    valid_thesis_states = {"SUPPORTIVE", "NEUTRAL", "WEAK", "CONTRADICTED", "INSUFFICIENT", "UNKNOWN"}
    valid_conf_states = {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}
    valid_contra_states = {"NONE_OBSERVED", "PRESENT", "MATERIAL", "UNKNOWN"}
    
    for i in range(min(50, len(df_pop))):
        th = synth_engine.synthesize_thesis_object(df_pop.iloc[i], layer="L5_FULL_SYNTHESIS")
        assert th["thesis_state"] in valid_thesis_states
        assert th["confidence_state"] in valid_conf_states
        assert th["contradiction_state"] in valid_contra_states


# 4. Multi-Layer Synthesis Ladder Layer Count
def test_04_multi_layer_ladder_count(thesis_results):
    _, df_summary, _ = thesis_results
    assert len(df_summary) == 6
    expected_layers = [
        "L0_DETERMINISTIC", "L1_RELEVANCE", "L2_TRANSMISSION",
        "L3_CONTRADICTION", "L4_RELATIONSHIP", "L5_FULL_SYNTHESIS"
    ]
    assert list(df_summary["information_layer"]) == expected_layers


# 5. Thesis Completeness Monotonic Elevation
def test_05_thesis_completeness_elevation(thesis_results):
    _, df_summary, _ = thesis_results
    completeness_vals = list(df_summary["mean_thesis_completeness_pct"])
    assert completeness_vals[0] == 40.0
    assert completeness_vals[-1] == 100.0
    for i in range(len(completeness_vals) - 1):
        assert completeness_vals[i] <= completeness_vals[i + 1]


# 6. Contradiction Isolation at Layer L3+
def test_06_contradiction_isolation(thesis_results):
    _, df_summary, _ = thesis_results
    l0_contra = int(df_summary.loc[df_summary["information_layer"] == "L0_DETERMINISTIC", "contradicted_theses"].values[0])
    l5_contra = int(df_summary.loc[df_summary["information_layer"] == "L5_FULL_SYNTHESIS", "contradicted_theses"].values[0])
    assert l0_contra == 0
    assert l5_contra > 0


# 7. Contradiction Downgrades Confidence to LOW
def test_07_contradiction_confidence_downgrade(synth_engine, population):
    df_pop, _ = population
    for _, row in df_pop.iterrows():
        th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
        if th["contradiction_state"] == "MATERIAL":
            assert th["confidence_state"] == "LOW"
            assert th["thesis_state"] == "CONTRADICTED"


# 8. Archival Gap Preserved as INSUFFICIENT
def test_08_archival_gap_preservation(synth_engine, population):
    df_pop, _ = population
    archival_gap_rows = df_pop[df_pop["coverage_tier"] == "ARCHIVAL_GAP"]
    if len(archival_gap_rows) > 0:
        for _, row in archival_gap_rows.head(20).iterrows():
            th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
            assert "ARCHIVAL_GAP_PRE_2018_OWNERSHIP_UNVERIFIED" in th["unknown_information"]
            if not row["is_commodity"] and th["contradiction_state"] != "MATERIAL":
                assert th["thesis_state"] == "INSUFFICIENT"


# 9. Transmission Channel Mapped from Sector
def test_09_transmission_channel_mapping(synth_engine, population):
    df_pop, _ = population
    for _, row in df_pop.head(30).iterrows():
        th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
        expected_channel = TRANSMISSION_CHANNELS[row["sector"]]
        assert th["transmission_channel"] == expected_channel


# 10. Supporting Evidence Cryptographic UUIDs
def test_10_supporting_evidence_uuids(synth_engine, population):
    df_pop, _ = population
    for _, row in df_pop.head(20).iterrows():
        th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
        for ev_id in th["supporting_evidence"]:
            assert ev_id.startswith(f"EV_{row['ticker']}_")


# 11. Invalidation Condition Clarity
def test_11_invalidation_condition_clarity(synth_engine, population):
    df_pop, _ = population
    for _, row in df_pop.head(20).iterrows():
        th = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS")
        assert len(th["invalidation_condition"]) > 10


# 12. Thesis Attribution Decomposition Completeness
def test_12_thesis_attribution_decomposition(synth_engine, thesis_results):
    df_all_theses, _, _ = thesis_results
    df_attr = synth_engine.evaluate_thesis_attribution(df_all_theses)
    assert len(df_attr) == 6
    expected_sources = {
        "CONTRADICTION_DETECTION", "TRANSMISSION_REFINEMENT",
        "RELEVANCE_FILTERING", "NOVELTY_INTEGRATION",
        "UNKNOWN_PRESERVATION", "UNCHANGED_BASELINE"
    }
    assert set(df_attr["attribution_source"]) == expected_sources


# 13. Thesis Attribution Proportions Sum to 100%
def test_13_attribution_proportions_sum(synth_engine, thesis_results):
    df_all_theses, _, _ = thesis_results
    df_attr = synth_engine.evaluate_thesis_attribution(df_all_theses)
    tot_pct = float(df_attr["proportion_pct"].sum())
    assert pytest.approx(tot_pct, abs=1e-3) == 100.0


# 14. Reference Decision-Impact Benchmark Size (N=300)
def test_14_reference_benchmark_size(synth_engine):
    df_ref = synth_engine.build_reference_decision_impact_benchmark(n_items=300)
    assert len(df_ref) == 300


# 15. Reference Benchmark Fields
def test_15_reference_benchmark_fields(synth_engine):
    df_ref = synth_engine.build_reference_decision_impact_benchmark(n_items=300)
    req_cols = [
        "reference_id", "ticker", "event_class", "time_era", "market_regime",
        "evidence_relevant", "evidence_novel", "contradiction_material",
        "transmission_valid", "thesis_change_justified", "risk_implication_valid",
        "decision_change_justified", "pit_compliance", "outcome_blind_audit_pass"
    ]
    for col in req_cols:
        assert col in df_ref.columns


# 16. Reference Benchmark Outcome Blindness Pass
def test_16_reference_benchmark_outcome_blindness(synth_engine):
    df_ref = synth_engine.build_reference_decision_impact_benchmark(n_items=300)
    assert df_ref["outcome_blind_audit_pass"].all()
    assert df_ref["pit_compliance"].all()


# 17. Contradiction Counterfactual Flag Toggle
def test_17_contradiction_counterfactual_toggle(synth_engine, population):
    df_pop, _ = population
    row = df_pop.iloc[0]
    th_with = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS", disable_contradiction=False)
    th_without = synth_engine.synthesize_thesis_object(row, layer="L5_FULL_SYNTHESIS", disable_contradiction=True)
    assert th_without["contradiction_state"] in ["NONE_OBSERVED", "UNKNOWN"]


# 18. Zero Outcome Leakage in Thesis Objects
def test_18_zero_outcome_leakage_in_thesis(thesis_results):
    df_all_theses, _, _ = thesis_results
    forbidden_tokens = ["excess_h5", "forward_return", "mfe_pct", "mae_pct", "t_plus_5"]
    for col in df_all_theses.columns:
        assert col.lower() not in forbidden_tokens
        if df_all_theses[col].dtype == object:
            for text_val in df_all_theses[col].astype(str):
                for tok in forbidden_tokens:
                    assert tok not in text_val.lower()

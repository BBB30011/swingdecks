"""
tests/test_batch_zzz101_historical_disclosure_coverage.py

Comprehensive deterministic test suite for Batch ZZZ.10.1:
Historical Disclosure Coverage & Event Completeness Audit.

Verifies:
1. Critical Semantic Rule: ABSENCE_OF_RECORD != VERIFIED_NO_EVENT
2. 8-State Event Taxonomy Integrity
3. Reconciliation of the 49 C0_no_event classifications (0 VERIFIED_NO_EVENT, 49 NO_EVIDENCE_IN_DATASET)
4. Multi-Horizon Future Event Injection Invariant (T+1, T+2, T+5)
5. Entity Resolution & Unresolved Entity Safety
6. PIT Availability Validation (valid_from <= T, published_at <= T)
7. Source-to-Record Traceability & Provenance
8. Event-Type Completeness & Canonical Class Audit
9. Ticker-Level Coverage Across Pilot Universe
10. Coverage Rate vs Observed Event Incidence Distinction
11. Frozen Layer E Input Integrity (N=73 preserved)
12. Zero Outcome / Return Leakage in Coverage Classification
13. Exactly 3-Agent Architecture Preserved
14. Deterministic Repeatability
15. Summary JSON & Parquet Artifact Validation
16. Audit Conclusion Consistency (CONDITIONAL — COVERAGE INSUFFICIENT)
"""

import os
import sys
import json
import duckdb
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_disclosure_coverage_engine import (
    HistoricalDisclosureCoverageEngine,
    EventAuditState,
    ProvenanceState,
    CANONICAL_EVENT_TYPES
)
from core.company_specific_discrimination_engine import (
    CompanySpecificDiscriminationEngine,
    PILOT_UNIVERSE,
    EXPOSURE_GROUPS
)

@pytest.fixture(scope="module")
def coverage_engine():
    return HistoricalDisclosureCoverageEngine(db_path="tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def layer_e_df():
    path = "gates/evidence/zzz10_results.parquet"
    if not os.path.exists(path):
        path = "gates/evidence/zzz82_oos_results.parquet"
    return pd.read_parquet(path)

# 1. Critical Semantic Rule: ABSENCE_OF_RECORD != VERIFIED_NO_EVENT
def test_critical_semantic_rule_absence_not_verified_no_event(coverage_engine, layer_e_df):
    _, audit_df, metrics = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    
    # Verify that no row in the audit output is incorrectly classified as VERIFIED_NO_EVENT
    verified_no_event_count = (audit_df["reconciled_event_state"] == EventAuditState.VERIFIED_NO_EVENT.value).sum()
    assert verified_no_event_count == 0, (
        f"Critical Rule Violation: Found {verified_no_event_count} records marked as VERIFIED_NO_EVENT "
        "when qualitative sources are unpopulated."
    )
    
    # All setups without contemporary corporate actions must be marked NO_EVIDENCE_IN_DATASET or EVENT_PRESENT
    no_ev_count = (audit_df["reconciled_event_state"] == EventAuditState.NO_EVIDENCE_IN_DATASET.value).sum()
    assert no_ev_count + metrics["event_present_count"] == len(layer_e_df)

# 2. 8-State Event Taxonomy Integrity
def test_eight_state_event_taxonomy_enum():
    expected_states = {
        "VERIFIED_NO_EVENT",
        "EVENT_PRESENT",
        "NO_EVIDENCE_IN_DATASET",
        "ENTITY_UNRESOLVED",
        "PIT_UNCERTAIN",
        "CONTRADICTORY",
        "SOURCE_UNAVAILABLE",
        "EVENT_PRESENT_BUT_INCOMPLETE"
    }
    actual_states = {s.value for s in EventAuditState}
    assert actual_states == expected_states

# 3. Reconciliation of the 49 C0_no_event classifications from ZZZ.10.1 summary artifact
def test_reconciliation_of_49_c0_no_event_observations():
    with open("gates/evidence/zzz101_summary.json", "r") as f:
        data = json.load(f)
    c0_rec = data["coverage_metrics"]["c0_no_event_reconciliation"]
    assert c0_rec["original_c0_no_event_count"] == 49
    assert c0_rec["reconciled_as_no_evidence_in_dataset"] == 49
    assert c0_rec["reconciled_as_verified_no_event"] == 0

# 4. Multi-Horizon Future Event Injection Invariant (T+1, T+2, T+5)
def test_multi_horizon_future_injection_isolation(coverage_engine, layer_e_df):
    sample_cand = layer_e_df.iloc[0].to_dict()
    sample_cand["date"] = sample_cand.get("target_date", sample_cand.get("date"))
    sample_cand["symbol"] = sample_cand.get("target_symbol", sample_cand.get("symbol"))
    
    injection_results = coverage_engine.run_multi_horizon_future_injection(sample_cand, future_deltas=[1, 2, 5])
    assert injection_results["overall_status"] == "PASS"
    for r in injection_results["audit_results"]:
        assert r["found_at_T"] is False
        assert r["leakage_status"] == "PASS"

# 5. Entity Resolution & Unresolved Entity Safety
def test_entity_resolution_audit(coverage_engine):
    # Known pilot entity
    res_adro = coverage_engine.substrate.resolve_entity("ADRO")
    assert res_adro["entity_id"] == "ENT_ADRO"
    assert res_adro["canonical_name"] == "Adaro Energy Indonesia Tbk"
    
    # Unresolved unknown entity
    res_fake = coverage_engine.substrate.resolve_entity("UNKNOWN_TICKER_XYZ")
    assert res_fake["entity_id"] == "UNRESOLVED"

# 6. PIT Availability Validation (valid_from <= T, published_at <= T)
def test_pit_validity_in_substrate(coverage_engine):
    substrate_audit = coverage_engine.audit_event_records_in_substrate()
    assert substrate_audit["total_event_records"] >= 497
    assert substrate_audit["pit_valid_records"] >= 497
    assert substrate_audit["pit_validity_rate"] == 1.0

# 7. Source-to-Record Traceability & Provenance
def test_source_to_record_traceability(coverage_engine):
    con = duckdb.connect(coverage_engine.db_path, read_only=True)
    sources = con.execute("SELECT DISTINCT source_id FROM fact_event").fetchall()
    source_list = [s[0] for s in sources]
    con.close()
    
    assert "SRC_YFINANCE_MARKET" in source_list
    assert "INFO_RSS_CNBC_ID" in source_list

# 8. Event-Type Completeness & Canonical Class Audit
def test_event_type_completeness_audit(coverage_engine):
    type_df = coverage_engine.audit_event_type_completeness()
    assert len(type_df) == len(CANONICAL_EVENT_TYPES)
    
    div_row = type_df[type_df["event_type"] == "CORPORATE_ACTION_DIVIDEND"].iloc[0]
    assert div_row["record_count"] == 385
    assert div_row["ingestion_status"] == "POPULATED"
    assert div_row["audit_state"] == "COVERED"

# 9. Ticker-Level Coverage Across Pilot Universe
def test_ticker_level_coverage_audit(coverage_engine, layer_e_df):
    _, audit_df, _ = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    ticker_df = coverage_engine.audit_ticker_coverage(audit_df)
    
    assert len(ticker_df) == len(PILOT_UNIVERSE)
    assert ticker_df["layer_e_setups"].sum() == 73
    assert ticker_df["event_present"].sum() >= 24
    assert ticker_df["verified_no_event"].sum() == 0

# 10. Coverage Rate vs Observed Event Incidence Distinction
def test_coverage_rate_vs_observed_incidence(coverage_engine, layer_e_df):
    _, _, metrics = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    
    # Denominator consistency: event_present + no_evidence = total_setups
    assert metrics["event_present_count"] + metrics["no_evidence_in_dataset_count"] == metrics["total_layer_e_setups"]

# 11. Frozen Layer E Input Integrity (N=73 preserved)
def test_frozen_layer_e_input_integrity(layer_e_df):
    assert len(layer_e_df) == 73
    cols = layer_e_df.columns
    assert "target_symbol" in cols or "symbol" in cols
    assert "target_date" in cols or "date" in cols

# 12. Zero Outcome / Return Leakage in Coverage Classification
def test_no_outcome_leakage_in_coverage_audit(coverage_engine, layer_e_df):
    # Run audit on DataFrame with forward returns scrambled/masked
    df_masked = layer_e_df.copy()
    if "target_fwd_h5" in df_masked.columns:
        df_masked["target_fwd_h5"] = np.random.randn(len(df_masked))
    if "target_fwd_h10" in df_masked.columns:
        df_masked["target_fwd_h10"] = np.random.randn(len(df_masked))
        
    _, audit_df_masked, metrics_masked = coverage_engine.audit_layer_e_setup_coverage(df_masked)
    _, audit_df_orig, metrics_orig = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    
    # The coverage states must be 100% identical regardless of forward returns
    assert (audit_df_masked["reconciled_event_state"] == audit_df_orig["reconciled_event_state"]).all()
    assert metrics_masked == metrics_orig

# 13. Exactly 3-Agent Architecture Preserved
def test_three_agent_architecture_preserved():
    agents_path = "AGENTS.md"
    assert os.path.exists(agents_path)
    with open(agents_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Agent 1: Quant & Market Scanner" in content
    assert "Agent 2: Market Intelligence & Red Team" in content
    assert "Agent 3: Investment Committee & Risk Engine" in content
    assert "Do NOT create an Agent 4" in content

# 14. Deterministic Repeatability
def test_deterministic_repeatability(coverage_engine, layer_e_df):
    _, df1, m1 = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    _, df2, m2 = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    
    assert df1.equals(df2)
    assert m1 == m2

# 15. Summary JSON & Parquet Artifact Validation
def test_summary_json_and_parquet_artifacts_exist():
    json_path = "gates/evidence/zzz101_summary.json"
    parquet_path = "gates/evidence/zzz101_coverage_results.parquet"
    
    assert os.path.exists(json_path), f"Missing {json_path}"
    assert os.path.exists(parquet_path), f"Missing {parquet_path}"
    
    with open(json_path, "r") as f:
        data = json.load(f)
        
    assert data["metadata"]["batch"] == "ZZZ.10.1"
    assert data["substrate_audit"]["total_event_records"] == 497
    assert data["coverage_metrics"]["total_layer_e_setups"] == 73
    assert data["coverage_metrics"]["c0_no_event_reconciliation"]["reconciled_as_no_evidence_in_dataset"] == 49
    assert data["coverage_metrics"]["c0_no_event_reconciliation"]["reconciled_as_verified_no_event"] == 0

# 16. Audit Conclusion Consistency (CONDITIONAL — COVERAGE INSUFFICIENT)
def test_audit_verdict_is_conditional(coverage_engine, layer_e_df):
    _, _, metrics = coverage_engine.audit_layer_e_setup_coverage(layer_e_df)
    assert metrics["coverage_state_conclusion"] == "CONDITIONAL — COVERAGE INSUFFICIENT / CONCLUSION LIMITED"

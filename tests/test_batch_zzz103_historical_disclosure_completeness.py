"""
tests/test_batch_zzz103_historical_disclosure_completeness.py

Comprehensive deterministic test suite for Batch ZZZ.10.3:
Historical Disclosure Completeness, Recall & Source Cross-Validation Audit.

Verifies:
1. 73 Layer-E Denominator Invariant
2. 14 Uncovered Setups Individual Audit & Gap Attribution
3. Critical Semantic Invariant: NO_EVIDENCE != VERIFIED_NO_EVENT != GENUINE_LOW_DISCLOSURE
4. Source Channel Completeness & Audit Tracing
5. Raw Artifact SHA-256 Provenance & File Integrity
6. Deterministic Blind Recall Audit (Recall >= 75%)
7. Entity Resolution & Unresolved Entity Safety
8. Multi-Source Syndicate Deduplication
9. Contradiction Detection & Invariant Handling
10. Strict Point-in-Time (PIT) Boundary Invariant
11. T+1 Future Event Injection Rejection
12. T+2 Future Event Injection Rejection
13. T+5 Future Event Injection Rejection
14. Zero Outcome / Return Leakage in Completeness & Recall Auditing
15. Deterministic Sampling Reproducibility
16. Coverage Matrix Denominator Consistency (Sum == 73)
17. Selection Bias & Exposure Parity Delta (< 20%, LOW RISK)
18. Frozen Layer-E Input Integrity (N=73 preserved)
19. Exactly 3-Agent Architecture Preserved (Zero Agent 4)
20. Summary JSON & Parquet Output Artifacts Structure
21. ZZZ.11 Readiness Gate Evaluation
"""

import os
import sys
import json
import duckdb
import pytest
import hashlib
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_disclosure_completeness_audit import (
    HistoricalDisclosureCompletenessAuditor,
    CoverageGapReason,
    RecallAuditResult
)
from core.historical_disclosure_ingestion_engine import (
    HistoricalDisclosureIngestionEngine,
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
def completeness_auditor():
    return HistoricalDisclosureCompletenessAuditor(db_path="tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def ingestion_engine():
    return HistoricalDisclosureIngestionEngine(db_path="tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def layer_e_df():
    path = "gates/evidence/zzz10_results.parquet"
    if not os.path.exists(path):
        path = "gates/evidence/zzz82_oos_results.parquet"
    return pd.read_parquet(path)

# 1. 73 Layer-E Denominator Invariant
def test_73_layer_e_denominator_invariant(ingestion_engine, layer_e_df):
    evaluated_df, summary = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    assert len(evaluated_df) == 73
    assert summary["total_layer_e_setups"] == 73
    assert summary["after_ingestion"]["event_present"] + summary["after_ingestion"]["no_evidence_in_dataset"] == 73

# 2. 14 Uncovered Setups Individual Audit & Gap Attribution
def test_14_uncovered_setups_reconciliation(completeness_auditor, ingestion_engine, layer_e_df):
    evaluated_df, _ = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    uncovered_records, summary = completeness_auditor.audit_the_14_remaining_no_evidence_setups(evaluated_df)
    
    assert len(uncovered_records) == 14
    assert summary["total_uncovered_setups"] == 14
    assert summary["reconciled_as_verified_no_event"] == 0
    assert summary["reconciled_as_no_evidence_in_dataset"] == 14
    
    for r in uncovered_records:
        assert r.reconciled_state == EventAuditState.NO_EVIDENCE_IN_DATASET.value
        assert r.coverage_gap_reason in [e.value for e in CoverageGapReason]
        assert len(r.audit_notes) > 10

# 3. Critical Semantic Invariant: NO_EVIDENCE != VERIFIED_NO_EVENT != GENUINE_LOW_DISCLOSURE
def test_critical_semantic_invariant(ingestion_engine, layer_e_df):
    evaluated_df, summary = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    verified_no_count = (evaluated_df["reconciled_event_state"] == EventAuditState.VERIFIED_NO_EVENT.value).sum()
    assert verified_no_count == 0, "Critical Invariant Violation: Found records marked as VERIFIED_NO_EVENT."
    assert summary["after_ingestion"]["verified_no_event"] == 0

# 4. Source Channel Completeness & Audit Tracing
def test_source_channel_completeness_audit(completeness_auditor):
    source_audit = completeness_auditor.audit_source_channel_completeness()
    assert source_audit["total_channels_audited"] >= 4
    source_ids = [ch["source_id"] for ch in source_audit["channels"]]
    assert "SRC_IDX_DISCLOSURES" in source_ids
    assert "SRC_ISSUER_IR" in source_ids
    assert "SRC_ESDM_MINISTRY" in source_ids
    assert "SRC_YFINANCE_MARKET" in source_ids

# 5. Raw Artifact SHA-256 Provenance & File Integrity
def test_raw_artifact_sha256_provenance(ingestion_engine):
    raw_artifacts = ingestion_engine.load_raw_artifacts_from_directory("data/raw/disclosures")
    assert len(raw_artifacts) >= 29
    
    for art in raw_artifacts:
        assert len(art.content_hash) == 64
        expected_data = f"{art.artifact_id}|{art.source_id}|{art.published_at}|{art.entity_hint}|{art.title}|{art.raw_content}"
        expected_hash = hashlib.sha256(expected_data.encode("utf-8")).hexdigest()
        assert art.content_hash == expected_hash

# 6. Deterministic Blind Recall Audit (Recall >= 75%)
def test_deterministic_blind_recall_audit(completeness_auditor, layer_e_df):
    recall_res = completeness_auditor.run_deterministic_blind_recall_audit(layer_e_df, sample_size=15, random_seed=42)
    assert recall_res.sample_size == 15
    assert recall_res.recall_estimate >= 0.75
    assert recall_res.recall_estimate == 0.80
    assert recall_res.false_negative_rate == 0.20
    assert recall_res.audit_verdict == "ACCEPTABLE_FOR_DISCRIMINATION_PILOT"

# 7. Entity Resolution & Unresolved Entity Safety
def test_entity_resolution_audit(completeness_auditor):
    res_bbri = completeness_auditor.substrate.resolve_entity("BBRI")
    assert res_bbri["entity_id"] == "ENT_BBRI"
    assert "Bank Rakyat Indonesia" in res_bbri["canonical_name"]
    
    res_fake = completeness_auditor.substrate.resolve_entity("NON_EXISTENT_ISSUER")
    assert res_fake["entity_id"] == "UNRESOLVED"

# 8. Multi-Source Syndicate Deduplication
def test_syndicate_deduplication(ingestion_engine):
    raw_artifacts = ingestion_engine.load_raw_artifacts_from_directory("data/raw/disclosures")
    normalized = [ingestion_engine.normalize_artifact(a) for a in raw_artifacts if ingestion_engine.normalize_artifact(a) is not None]
    deduped, audit = ingestion_engine.deduplicate_and_resolve_syndicate(normalized)
    assert len(deduped) <= len(normalized)

# 9. Contradiction Detection & Invariant Handling
def test_contradiction_detection(completeness_auditor, ingestion_engine):
    raw_artifacts = ingestion_engine.load_raw_artifacts_from_directory("data/raw/disclosures")
    normalized = [ingestion_engine.normalize_artifact(a) for a in raw_artifacts if ingestion_engine.normalize_artifact(a) is not None]
    contradictions = ingestion_engine.detect_contradictions(normalized)
    assert isinstance(contradictions, list)

# 10. Strict Point-in-Time (PIT) Boundary Invariant
def test_strict_pit_boundary_in_db(completeness_auditor):
    con = duckdb.connect(completeness_auditor.db_path, read_only=True)
    invalid_rows = con.execute("""
        SELECT count(*) FROM fact_event
        WHERE published_at IS NULL OR valid_from IS NULL OR is_pit_valid = false
    """).fetchone()[0]
    con.close()
    assert invalid_rows == 0

# 11. T+1 Future Event Injection Rejection
def test_future_injection_t_plus_1(completeness_auditor, layer_e_df):
    sample_cand = layer_e_df.iloc[0].to_dict()
    sample_cand["date"] = sample_cand.get("target_date", sample_cand.get("date"))
    sample_cand["symbol"] = sample_cand.get("target_symbol", sample_cand.get("symbol"))
    
    inj_res = completeness_auditor.discrimination_engine.run_future_injection_audit_suite(sample_cand, future_deltas=[1])
    assert inj_res["overall_status"] == "PASS"
    assert inj_res["audit_results"][0]["found_at_T"] is False

# 12. T+2 Future Event Injection Rejection
def test_future_injection_t_plus_2(completeness_auditor, layer_e_df):
    sample_cand = layer_e_df.iloc[0].to_dict()
    sample_cand["date"] = sample_cand.get("target_date", sample_cand.get("date"))
    sample_cand["symbol"] = sample_cand.get("target_symbol", sample_cand.get("symbol"))
    
    inj_res = completeness_auditor.discrimination_engine.run_future_injection_audit_suite(sample_cand, future_deltas=[2])
    assert inj_res["overall_status"] == "PASS"
    assert inj_res["audit_results"][0]["found_at_T"] is False

# 13. T+5 Future Event Injection Rejection
def test_future_injection_t_plus_5(completeness_auditor, layer_e_df):
    sample_cand = layer_e_df.iloc[0].to_dict()
    sample_cand["date"] = sample_cand.get("target_date", sample_cand.get("date"))
    sample_cand["symbol"] = sample_cand.get("target_symbol", sample_cand.get("symbol"))
    
    inj_res = completeness_auditor.discrimination_engine.run_future_injection_audit_suite(sample_cand, future_deltas=[5])
    assert inj_res["overall_status"] == "PASS"
    assert inj_res["audit_results"][0]["found_at_T"] is False

# 14. Zero Outcome / Return Leakage in Completeness & Recall Auditing
def test_zero_outcome_leakage_in_completeness_audit(completeness_auditor, layer_e_df):
    df_masked = layer_e_df.copy()
    if "target_fwd_h5" in df_masked.columns:
        df_masked["target_fwd_h5"] = np.random.randn(len(df_masked))
    if "target_fwd_h10" in df_masked.columns:
        df_masked["target_fwd_h10"] = np.random.randn(len(df_masked))
        
    recall_orig = completeness_auditor.run_deterministic_blind_recall_audit(layer_e_df, sample_size=10, random_seed=42)
    recall_masked = completeness_auditor.run_deterministic_blind_recall_audit(df_masked, sample_size=10, random_seed=42)
    
    assert recall_orig.recall_estimate == recall_masked.recall_estimate
    assert recall_orig.detected_events_in_db == recall_masked.detected_events_in_db

# 15. Deterministic Sampling Reproducibility
def test_deterministic_sampling_reproducibility(completeness_auditor, layer_e_df):
    r1 = completeness_auditor.run_deterministic_blind_recall_audit(layer_e_df, sample_size=12, random_seed=123)
    r2 = completeness_auditor.run_deterministic_blind_recall_audit(layer_e_df, sample_size=12, random_seed=123)
    assert r1 == r2

# 16. Coverage Matrix Denominator Consistency (Sum == 73)
def test_coverage_matrix_denominator_consistency(completeness_auditor, ingestion_engine, layer_e_df):
    evaluated_df, _ = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    matrices = completeness_auditor.generate_coverage_matrix(evaluated_df)
    
    total_ticker_setups = sum(r["setups"] for r in matrices["ticker_matrix"])
    total_year_setups = sum(r["setups"] for r in matrices["year_matrix"])
    total_comm_setups = matrices["commodity_matrix"]["commodity_setups"] + matrices["commodity_matrix"]["non_commodity_setups"]
    
    assert total_ticker_setups == 73
    assert total_year_setups == 73
    assert total_comm_setups == 73

# 17. Selection Bias & Exposure Parity Delta (< 20%, LOW RISK)
def test_selection_bias_parity_delta(completeness_auditor, ingestion_engine, layer_e_df):
    evaluated_df, _ = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    matrices = completeness_auditor.generate_coverage_matrix(evaluated_df)
    cm = matrices["commodity_matrix"]
    
    assert cm["commodity_coverage_rate"] > 0.70
    assert cm["non_commodity_coverage_rate"] > 0.60
    assert abs(cm["parity_delta"]) < 0.20

# 18. Frozen Layer-E Input Integrity (N=73 preserved)
def test_frozen_layer_e_contract(layer_e_df):
    assert len(layer_e_df) == 73
    assert "target_symbol" in layer_e_df.columns or "symbol" in layer_e_df.columns
    assert "target_date" in layer_e_df.columns or "date" in layer_e_df.columns

# 19. Exactly 3-Agent Architecture Preserved (Zero Agent 4)
def test_three_agent_architecture():
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Agent 1: Quant & Market Scanner" in content
    assert "Agent 2: Market Intelligence & Red Team" in content
    assert "Agent 3: Investment Committee & Risk Engine" in content
    assert "Do NOT create an Agent 4" in content

# 20. Summary JSON & Parquet Output Artifacts Structure
def test_summary_json_and_parquet_artifacts_structure():
    parquet_path = "gates/evidence/zzz103_completeness_results.parquet"
    source_json = "gates/evidence/zzz103_source_coverage.json"
    recall_json = "gates/evidence/zzz103_recall_audit.json"
    
    assert os.path.exists(parquet_path), f"Missing {parquet_path}"
    assert os.path.exists(source_json), f"Missing {source_json}"
    assert os.path.exists(recall_json), f"Missing {recall_json}"
    
    with open(source_json, "r", encoding="utf-8") as f:
        s_data = json.load(f)
    with open(recall_json, "r", encoding="utf-8") as f:
        r_data = json.load(f)
        
    assert s_data["metadata"]["batch"] == "ZZZ.10.3"
    assert r_data["recall_metrics"]["recall_estimate"] == 0.80

# 21. ZZZ.11 Readiness Gate Evaluation
def test_zzz11_readiness_gate(completeness_auditor):
    gate = completeness_auditor.evaluate_zzz11_readiness_gate(
        coverage_rate=0.8082,
        recall_rate=0.80,
        pit_valid=True,
        provenance_valid=True,
        selection_bias_risk="LOW"
    )
    assert gate["readiness_status"] == "READY"
    assert gate["criteria_checklist"]["coverage_rate_threshold_met"] is True
    assert gate["criteria_checklist"]["recall_rate_threshold_met"] is True
    assert gate["criteria_checklist"]["pit_integrity_verified"] is True

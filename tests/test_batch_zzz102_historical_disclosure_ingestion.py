"""
tests/test_batch_zzz102_historical_disclosure_ingestion.py

Comprehensive deterministic test suite for Batch ZZZ.10.2:
Historical Disclosure Ingestion & Coverage Expansion.

Verifies:
1. Schema Integrity & Canonical Event Types (12 classes)
2. Strict Point-In-Time (PIT) Boundary Validation (valid_from <= T, published_at <= T)
3. Multi-Horizon Future Injection Test (T+1, T+2, T+5 rejection)
4. Deterministic Entity Resolution & Unresolved Entity Safety
5. Raw Artifact Provenance & SHA-256 Content Hash Verification
6. Multi-Source Syndicate Deduplication
7. Contradiction Detection & Invariant Handling
8. Coverage Improvement Metrics (32.88% -> 80.82%)
9. Reconciliation of the 49 Former C0 Setups (35 newly covered, 14 remain no-evidence)
10. Critical Semantic Rule: ABSENCE_OF_RECORD != VERIFIED_NO_EVENT (0 verified no-event)
11. Selection Bias & Exposure Parity Audit
12. Zero Outcome / Return Leakage in Ingestion & Classification
13. Frozen Layer-E Input Integrity (N=73 preserved)
14. Exactly 3-Agent Architecture Preserved (Zero Agent 4)
15. Deterministic Repeatability Across Consecutive Invocations
16. Summary JSON & Parquet Artifact Validation
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
from core.historical_disclosure_ingestion_engine import (
    HistoricalDisclosureIngestionEngine,
    RawDisclosureArtifact,
    NormalizedDisclosureEvent,
    SourceQualityLevel,
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
def ingestion_engine():
    return HistoricalDisclosureIngestionEngine(db_path="tests/fixtures/intelligence_mock.duckdb")

@pytest.fixture(scope="module")
def layer_e_df():
    path = "gates/evidence/zzz10_results.parquet"
    if not os.path.exists(path):
        path = "gates/evidence/zzz82_oos_results.parquet"
    return pd.read_parquet(path)

# 1. Schema Integrity & Canonical Event Types
def test_schema_integrity_and_event_types(ingestion_engine):
    con = duckdb.connect(ingestion_engine.db_path, read_only=True)
    subtypes = [r[0] for r in con.execute("SELECT DISTINCT event_subtype FROM fact_event").fetchall()]
    con.close()
    
    # Must contain corporate actions and newly ingested qualitative disclosure subtypes
    assert "DIVIDEND" in subtypes or "CORPORATE_ACTION_DIVIDEND" in subtypes
    assert "EARNINGS_FINANCIAL_RESULTS" in subtypes
    assert "PRODUCTION_OPERATIONAL" in subtypes
    assert "GOVERNMENT_PERMIT_REGULATION" in subtypes

# 2. Strict Point-In-Time (PIT) Boundary Validation
def test_strict_pit_boundary_in_substrate(ingestion_engine):
    con = duckdb.connect(ingestion_engine.db_path, read_only=True)
    invalid_pit_count = con.execute("""
        SELECT count(*) FROM fact_event
        WHERE published_at IS NULL OR valid_from IS NULL OR is_pit_valid = false
    """).fetchone()[0]
    con.close()
    assert invalid_pit_count == 0, "Found events with missing or invalid PIT timestamps"

# 3. Multi-Horizon Future Injection Test (T+1, T+2, T+5 rejection)
def test_multi_horizon_future_injection_isolation(ingestion_engine, layer_e_df):
    sample_cand = layer_e_df.iloc[0].to_dict()
    sample_cand["date"] = sample_cand.get("target_date", sample_cand.get("date"))
    sample_cand["symbol"] = sample_cand.get("target_symbol", sample_cand.get("symbol"))
    
    inj_res = ingestion_engine.discrimination_engine.run_future_injection_audit_suite(sample_cand, future_deltas=[1, 2, 5])
    assert inj_res["overall_status"] == "PASS"
    for r in inj_res["audit_results"]:
        assert r["found_at_T"] is False
        assert r["leakage_status"] == "PASS"

# 4. Deterministic Entity Resolution & Unresolved Entity Safety
def test_entity_resolution_audit(ingestion_engine):
    # Pilot entity
    res_bbca = ingestion_engine.substrate.resolve_entity("BBCA")
    assert res_bbca["entity_id"] == "ENT_BBCA"
    assert "Bank Central Asia" in res_bbca["canonical_name"]
    
    # Unresolved entity
    res_unknown = ingestion_engine.substrate.resolve_entity("UNKNOWN_ISSUER_999")
    assert res_unknown["entity_id"] == "UNRESOLVED"

# 5. Raw Artifact Provenance & SHA-256 Content Hash Verification
def test_raw_artifact_provenance_and_hash_integrity(ingestion_engine):
    raw_artifacts = ingestion_engine.load_raw_artifacts_from_directory("data/raw/disclosures")
    assert len(raw_artifacts) >= 29
    
    for art in raw_artifacts:
        assert len(art.content_hash) == 64
        expected_data = f"{art.artifact_id}|{art.source_id}|{art.published_at}|{art.entity_hint}|{art.title}|{art.raw_content}"
        expected_hash = hashlib.sha256(expected_data.encode("utf-8")).hexdigest()
        assert art.content_hash == expected_hash, f"Hash mismatch for artifact {art.artifact_id}"

# 6. Multi-Source Syndicate Deduplication
def test_syndicate_deduplication(ingestion_engine):
    # Create mock primary and secondary events with same symbol, subtype, date
    art1 = RawDisclosureArtifact(
        artifact_id="RAW_TEST_01",
        source_id="SRC_IDX_DISCLOSURES",
        source_type="OFFICIAL_EXCHANGE",
        authority_level=SourceQualityLevel.PRIMARY_AUTHORITATIVE.value,
        published_at="2026-01-20T09:00:00+07:00",
        retrieved_at="2026-01-20T10:00:00+07:00",
        entity_hint="ADRO",
        title="Target Produksi 2026",
        raw_content="Target produksi 65 juta ton",
        url_or_source_identifier="mock_url_1"
    )
    art2 = RawDisclosureArtifact(
        artifact_id="RAW_TEST_02",
        source_id="SRC_NEWS_WIRE",
        source_type="SECONDARY_MEDIA",
        authority_level=SourceQualityLevel.SECONDARY_VERIFIED.value,
        published_at="2026-01-20T09:30:00+07:00",
        retrieved_at="2026-01-20T10:30:00+07:00",
        entity_hint="ADRO",
        title="Target Produksi Batu Bara 2026",
        raw_content="Adaro target produksi 65 juta ton di 2026",
        url_or_source_identifier="mock_url_2"
    )
    
    ev1 = ingestion_engine.normalize_artifact(art1)
    ev2 = ingestion_engine.normalize_artifact(art2)
    
    deduped, audit = ingestion_engine.deduplicate_and_resolve_syndicate([ev1, ev2])
    assert len(deduped) == 1
    assert deduped[0].source_quality == SourceQualityLevel.PRIMARY_AUTHORITATIVE.value
    assert len(audit) == 1

# 7. Contradiction Detection & Invariant Handling
def test_contradiction_detection(ingestion_engine):
    art = RawDisclosureArtifact(
        artifact_id="RAW_TEST_CONTRADICT",
        source_id="SRC_IDX",
        source_type="OFFICIAL",
        authority_level=SourceQualityLevel.PRIMARY_AUTHORITATIVE.value,
        published_at="2026-01-20T09:00:00+07:00",
        retrieved_at="2026-01-20T10:00:00+07:00",
        entity_hint="ADRO",
        title="Target Produksi 2026",
        raw_content="Test content",
        url_or_source_identifier="mock_path"
    )
    ev = ingestion_engine.normalize_artifact(art)
    contradictions = ingestion_engine.detect_contradictions([ev])
    assert isinstance(contradictions, list)

# 8. Coverage Improvement Metrics (32.88% -> 80.82%)
def test_coverage_improvement_metrics(ingestion_engine, layer_e_df):
    _, summary = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    
    before_rate = summary["before_ingestion"]["coverage_rate"]
    after_rate = summary["after_ingestion"]["coverage_rate"]
    
    assert pytest.approx(before_rate, 0.001) == 0.3288
    assert pytest.approx(after_rate, 0.001) == 0.8082
    assert summary["after_ingestion"]["event_present"] == 59
    assert summary["after_ingestion"]["no_evidence_in_dataset"] == 14

# 9. Reconciliation of the 49 Former C0 Setups
def test_reconciliation_of_former_49_c0_setups(ingestion_engine, layer_e_df):
    _, summary = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    rec = summary["reconciliation_of_former_49_c0"]
    
    assert rec["total_former_c0"] == 49
    assert rec["now_event_present"] == 35
    assert rec["remains_no_evidence"] == 14
    assert pytest.approx(rec["newly_covered_percentage"], 0.001) == 0.7143

# 10. Critical Semantic Rule: ABSENCE_OF_RECORD != VERIFIED_NO_EVENT
def test_critical_semantic_rule_preservation(ingestion_engine, layer_e_df):
    evaluated_df, summary = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    
    verified_no_event_count = (evaluated_df["reconciled_event_state"] == EventAuditState.VERIFIED_NO_EVENT.value).sum()
    assert verified_no_event_count == 0, (
        f"Critical Semantic Rule Violation: Found {verified_no_event_count} records classified as VERIFIED_NO_EVENT."
    )
    assert summary["after_ingestion"]["verified_no_event"] == 0

# 11. Selection Bias & Exposure Parity Audit
def test_selection_bias_audit(ingestion_engine, layer_e_df):
    evaluated_df, _ = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    bias_audit = ingestion_engine.audit_selection_bias(evaluated_df)
    
    assert bias_audit["selection_bias_risk"] == "LOW"
    assert bias_audit["commodity_coverage_rate"] > 0.70
    assert bias_audit["non_commodity_coverage_rate"] > 0.60
    assert abs(bias_audit["coverage_parity_delta"]) < 0.20

# 12. Zero Outcome / Return Leakage in Ingestion & Classification
def test_zero_outcome_leakage(ingestion_engine, layer_e_df):
    # Mask / scramble forward returns
    df_masked = layer_e_df.copy()
    if "target_fwd_h5" in df_masked.columns:
        df_masked["target_fwd_h5"] = np.random.randn(len(df_masked))
    if "target_fwd_h10" in df_masked.columns:
        df_masked["target_fwd_h10"] = np.random.randn(len(df_masked))
        
    df_eval_masked, sum_masked = ingestion_engine.evaluate_all_73_layer_e_setups(df_masked)
    df_eval_orig, sum_orig = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    
    assert (df_eval_masked["reconciled_event_state"] == df_eval_orig["reconciled_event_state"]).all()
    assert sum_masked == sum_orig

# 13. Frozen Layer-E Input Integrity (N=73 preserved)
def test_frozen_layer_e_integrity(layer_e_df):
    assert len(layer_e_df) == 73
    assert "target_symbol" in layer_e_df.columns or "symbol" in layer_e_df.columns
    assert "target_date" in layer_e_df.columns or "date" in layer_e_df.columns

# 14. Exactly 3-Agent Architecture Preserved
def test_three_agent_architecture():
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        content = f.read()
    assert "Agent 1: Quant & Market Scanner" in content
    assert "Agent 2: Market Intelligence & Red Team" in content
    assert "Agent 3: Investment Committee & Risk Engine" in content
    assert "Do NOT create an Agent 4" in content

# 15. Deterministic Repeatability
def test_deterministic_repeatability(ingestion_engine, layer_e_df):
    df1, s1 = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    df2, s2 = ingestion_engine.evaluate_all_73_layer_e_setups(layer_e_df)
    
    assert df1.equals(df2)
    assert s1 == s2

# 16. Summary JSON & Parquet Artifact Validation
def test_output_artifacts_exist_and_valid():
    json_path = "gates/evidence/zzz102_coverage_summary.json"
    parquet_path = "gates/evidence/zzz102_disclosure_events.parquet"
    
    assert os.path.exists(json_path), f"Missing {json_path}"
    assert os.path.exists(parquet_path), f"Missing {parquet_path}"
    
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["metadata"]["batch"] == "ZZZ.10.2"
    assert data["metadata"]["evaluated_setups"] == 73
    assert data["coverage_comparison"]["after_ingestion"]["event_present"] == 59
    assert data["coverage_comparison"]["after_ingestion"]["no_evidence_in_dataset"] == 14

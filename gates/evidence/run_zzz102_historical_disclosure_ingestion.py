"""
scratch/run_zzz102_historical_disclosure_ingestion.py

Execution runner for Batch ZZZ.10.2: Historical Disclosure Ingestion & Coverage Expansion.
Loads raw artifacts, normalizes, deduplicates, ingests into DuckDB substrate,
evaluates historical state coverage for all 73 Layer-E setups, and exports summary artifacts.
"""

import os
import sys
import json
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_disclosure_ingestion_engine import (
    HistoricalDisclosureIngestionEngine,
    SourceQualityLevel
)

def main():
    print("=" * 80)
    print("BATCH ZZZ.10.2 — HISTORICAL DISCLOSURE INGESTION & COVERAGE EXPANSION")
    print("=" * 80)

    db_path = "data/duckdb/intelligence.duckdb"
    engine = HistoricalDisclosureIngestionEngine(db_path=db_path)

    # 1. Load Raw Artifacts
    print("\n--- 1. Loading Raw Disclosure Artifacts ---")
    raw_artifacts = engine.load_raw_artifacts_from_directory("data/raw/disclosures")
    print(f"Loaded {len(raw_artifacts)} raw disclosure artifacts from data/raw/disclosures/")

    # 2. Normalize Artifacts
    print("\n--- 2. Normalizing Artifacts into Canonical fact_event Schema ---")
    normalized_events = []
    for art in raw_artifacts:
        ev = engine.normalize_artifact(art)
        if ev:
            normalized_events.append(ev)
    print(f"Successfully normalized {len(normalized_events)} disclosure events.")

    # 3. Deduplicate Syndicated Articles
    print("\n--- 3. Deduplication & Multi-Source Syndicate Resolution ---")
    deduped_events, dedup_audit = engine.deduplicate_and_resolve_syndicate(normalized_events)
    print(f"Events after deduplication: {len(deduped_events)} (Suppressed {len(dedup_audit)} syndicated duplicates)")
    for d in dedup_audit:
        print(f"  - [{d['symbol']} {d['date']}] Retained: {d['retained_event_id']} (Reason: {d['reason']})")

    # 4. Ingest into DuckDB Substrate
    print("\n--- 4. Ingesting into DuckDB Substrate (fact_event) ---")
    inserted = engine.ingest_events_into_duckdb(deduped_events)
    print(f"Inserted {inserted} new historical disclosure events into fact_event.")

    # Check total records in DuckDB fact_event
    con = duckdb.connect(db_path, read_only=True)
    total_db_events = con.execute("SELECT count(*) FROM fact_event").fetchone()[0]
    subtype_dist = dict(con.execute("SELECT event_subtype, count(*) FROM fact_event GROUP BY 1 ORDER BY 2 DESC").fetchall())
    con.close()
    print(f"Total events in DuckDB fact_event now: {total_db_events}")
    print("Event Subtype Breakdown in DuckDB:")
    for k, v in subtype_dist.items():
        print(f"  - {k}: {v}")

    # 5. Evaluate All 73 Layer-E Historical Setups
    print("\n--- 5. Evaluating Historical State Coverage for All 73 Layer-E Setups ---")
    layer_e_path = "scratch/zzz10_results.parquet"
    if not os.path.exists(layer_e_path):
        layer_e_path = "scratch/zzz82_oos_results.parquet"
    layer_e_df = pd.read_parquet(layer_e_path)

    evaluated_df, coverage_summary = engine.evaluate_all_73_layer_e_setups(layer_e_df)

    print("\n--- 6. Coverage Comparison: Before vs. After Ingestion ---")
    b = coverage_summary["before_ingestion"]
    a = coverage_summary["after_ingestion"]
    rec = coverage_summary["reconciliation_of_former_49_c0"]
    print(f"{'Metric':<35} | {'Before (ZZZ.10.1)':>18} | {'After (ZZZ.10.2)':>18}")
    print("-" * 75)
    print(f"{'Total Layer-E Setups':<35} | {b['total_layer_e_setups']:>18} | {a['total_layer_e_setups']:>18}" if 'total_layer_e_setups' in b else f"{'Total Layer-E Setups':<35} | {73:>18} | {73:>18}")
    print(f"{'EVENT_PRESENT Count':<35} | {b['event_present']:>18} | {a['event_present']:>18}")
    print(f"{'NO_EVIDENCE_IN_DATASET Count':<35} | {b['no_evidence_in_dataset']:>18} | {a['no_evidence_in_dataset']:>18}")
    print(f"{'VERIFIED_NO_EVENT Count':<35} | {b['verified_no_event']:>18} | {a['verified_no_event']:>18}")
    print(f"{'Coverage Rate':<35} | {b['coverage_rate']*100:>17.2f}% | {a['coverage_rate']*100:>17.2f}%")
    print(f"\nFormer 49 C0 Setups Reconciliation:")
    print(f"  - Now with Verified Evidence (EVENT_PRESENT): {rec['now_event_present']} / {rec['total_former_c0']} ({rec['newly_covered_percentage']*100:.1f}%)")
    print(f"  - Remaining NO_EVIDENCE_IN_DATASET: {rec['remains_no_evidence']} / {rec['total_former_c0']}")

    # 7. Selection Bias Audit
    print("\n--- 7. Selection Bias & Exposure Parity Audit ---")
    bias_audit = engine.audit_selection_bias(evaluated_df)
    print(f"Commodity Coverage Rate: {bias_audit['commodity_coverage_rate']*100:.2f}%")
    print(f"Non-Commodity Coverage Rate: {bias_audit['non_commodity_coverage_rate']*100:.2f}%")
    print(f"Coverage Parity Delta: {bias_audit['coverage_parity_delta']*100:.2f}%")
    print(f"Selection Bias Risk Assessment: {bias_audit['selection_bias_risk']}")

    # 8. Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    out_parquet = "scratch/zzz102_disclosure_events.parquet"
    out_json = "scratch/zzz102_coverage_summary.json"

    evaluated_df.to_parquet(out_parquet, index=False)

    summary_payload = {
        "metadata": {
            "batch": "ZZZ.10.2",
            "experiment": "Historical Disclosure Ingestion & Coverage Expansion",
            "decision": "PASS — HISTORICAL COVERAGE MATERIALLY IMPROVED" if a["coverage_rate"] > 0.60 else "CONDITIONAL — COVERAGE IMPROVED BUT MATERIAL GAPS REMAIN",
            "evaluated_setups": 73,
            "total_raw_artifacts": len(raw_artifacts),
            "deduplicated_events": len(deduped_events),
            "total_events_in_duckdb": total_db_events
        },
        "coverage_comparison": coverage_summary,
        "selection_bias_audit": bias_audit,
        "subtype_distribution": subtype_dist,
        "deduplication_audit": dedup_audit
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2)

    print(f"\nSaved evaluation dataframe to {out_parquet}")
    print(f"Saved coverage summary JSON to {out_json}")
    print("\n" + "=" * 80)
    print("BATCH ZZZ.10.2 RUN COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

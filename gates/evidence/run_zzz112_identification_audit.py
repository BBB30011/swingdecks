"""
scratch/run_zzz112_identification_audit.py

Runner script for Batch ZZZ.11.2: Identification Audit & Coverage-Independent Control Construction.
Executes observation-level auditing, replicates ZZZ.11.1, audits zero-differential tickers,
and produces all required parquet and JSON artifacts.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.identification_audit_engine import IdentificationAuditEngine

def main():
    print("================================================================================")
    print("STARTING BATCH ZZZ.11.2: IDENTIFICATION AUDIT & CONTROL CONSTRUCTION")
    print("================================================================================")
    
    parquet_path = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "scratch/zzz81_ablation_results.parquet"
    full_df = pd.read_parquet(parquet_path)
    print(f"Loaded dataset from {parquet_path}: Shape {full_df.shape}")
    
    engine = IdentificationAuditEngine("data/duckdb/intelligence.duckdb")
    
    # 1. Replicate ZZZ.11.1
    print("\n--- Objective 1: Replicate ZZZ.11.1 Baseline ---")
    rep_res = engine.replicate_zzz111_baseline(full_df)
    print(f"Full Sample Diff Excess H5: +{rep_res['full_sample_diff_excess_h5']*100:.2f} pp (p = {rep_res['full_sample_p_val']:.4f})")
    print(f"Commodity Only Diff Excess H5: +{rep_res['commodity_only_diff_excess_h5']*100:.2f} pp (p = {rep_res['commodity_only_p_val']:.4f})")
    print(f"Primary Only Mean Excess H5: +{rep_res['primary_only_mean_excess_h5']*100:.2f}%")
    
    # 2. Observation-Level Audit Trail
    print("\n--- Generating Observation-Level Audit Trail ---")
    audit_df = engine.generate_observation_level_audit_trail(full_df)
    print(f"Generated Audit Trail DataFrame: Shape {audit_df.shape}")
    
    # 3. Audit Six Zero-Differential Tickers
    print("\n--- Objective 2: Audit Six Zero-Differential Tickers ---")
    zero_audit = engine.audit_six_zero_differential_tickers(audit_df)
    print(f"Root Cause: {zero_audit['root_cause_classification']}")
    for sym, details in zero_audit["ticker_audits"].items():
        print(f"  {sym:5s}: Ev N={details['evidence_present_N']:2d}, Unobs N={details['unobserved_N']:2d} -> Actual Delta = {details['actual_within_ticker_delta_pp']:+.2f} pp")
        
    # 4. Construct Source-Available Control
    print("\n--- Objective 3: Construct Source-Available Control ---")
    ctrl_res = engine.construct_source_available_control()
    print(f"Control Status: {ctrl_res['control_status']}")
    
    # 5. Coverage-Matched Control Experiment
    print("\n--- Objective 4: Coverage-Matched Control Experiment ---")
    matched_res = engine.run_coverage_matched_control_experiment(audit_df)
    print(f"Total Matched Pairs: {matched_res['total_matched_pairs']}")
    
    # 6. Ticker Leave-One-Out Audit
    print("\n--- Objective 11: Ticker Leave-One-Out Audit ---")
    loo_res = engine.run_ticker_leave_one_out_audit(audit_df)
    print(f"Effect Range: {loo_res['min_effect_pp']:.2f} pp to {loo_res['max_effect_pp']:.2f} pp (Median: {loo_res['median_effect_pp']:.2f} pp)")
    print(f"Positive Count: {loo_res['positive_count']}/12, Statistically Significant Count: {loo_res['statistically_significant_count']}/12")
    
    # 7. Date Robustness
    print("\n--- Objective 10: Date Concentration Robustness ---")
    date_res = engine.coverage_engine.run_date_concentration_robustness(audit_df.rename(columns={"target_H5": "target_h5", "decision_date": "target_date", "excess_H5": "excess_h5_vs_peers", "evidence_state": "has_company_specific_event"}).assign(has_company_specific_event=lambda x: x["has_company_specific_event"] == "EVIDENCE_PRESENT"))
    
    # 8. Missingness Analysis
    print("\n--- Objective 8: Missingness Analysis ---")
    miss_res = engine.coverage_engine.run_missingness_mechanism_analysis(
        audit_df.rename(columns={"evidence_state": "has_company_specific_event", "decision_date": "target_date"}).assign(has_company_specific_event=lambda x: x["has_company_specific_event"] == "EVIDENCE_PRESENT"),
        full_df
    )
    
    # 9. Source Tier Sensitivity
    print("\n--- Objective 12: Source Authority Sensitivity ---")
    source_sens = engine.discrimination_engine.run_source_quality_sensitivity(full_df)
    
    # 10. Red Team 24-Dimension Audit
    print("\n--- Red Team 24-Dimension Audit ---")
    redteam_res = engine.run_24_dimension_red_team_audit(audit_df)
    print(f"Red Team Verdict: {redteam_res['overall_status']} ({redteam_res['passed_checks']}/{redteam_res['total_checks']} passed)")
    
    # Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # A. Observation Level Parquet
    audit_parquet_out = "scratch/zzz112_observation_level_audit.parquet"
    audit_df.to_parquet(audit_parquet_out, index=False)
    print(f"\n[ARTIFACT] Saved observation audit parquet to {audit_parquet_out}")
    
    # B. Control Candidates Parquet
    ctrl_parquet_out = "scratch/zzz112_control_candidates.parquet"
    audit_df[audit_df["evidence_state"] == "NO_EVIDENCE_IN_DATASET"].to_parquet(ctrl_parquet_out, index=False)
    print(f"[ARTIFACT] Saved control candidates parquet to {ctrl_parquet_out}")
    
    # C. Matching Results JSON
    matching_out = "scratch/zzz112_matching_results.json"
    with open(matching_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "matching_results": matched_res,
            "date_robustness": date_res,
            "replication_baseline": rep_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved matching results JSON to {matching_out}")
    
    # D. Missingness Analysis JSON
    miss_out = "scratch/zzz112_missingness_analysis.json"
    with open(miss_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "missingness_analysis": miss_res,
            "missingness_pattern": "OBSERVED_SECTOR_DEPENDENCE"
        }, f, indent=2)
    print(f"[ARTIFACT] Saved missingness analysis JSON to {miss_out}")
    
    # E. Source Sensitivity JSON
    source_out = "scratch/zzz112_source_sensitivity.json"
    with open(source_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "source_sensitivity": source_sens,
            "yfinance_classification": "MARKET_DATA_PROVIDER",
            "tier_4_quarantine": "EXCLUDED"
        }, f, indent=2)
    print(f"[ARTIFACT] Saved source sensitivity JSON to {source_out}")
    
    # F. Ticker Audit JSON
    ticker_out = "scratch/zzz112_ticker_audit.json"
    with open(ticker_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "leave_one_out_audit": loo_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved ticker audit JSON to {ticker_out}")
    
    # G. Zero Differential Audit JSON
    zero_out = "scratch/zzz112_zero_differential_audit.json"
    with open(zero_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "zero_differential_audit": zero_audit
        }, f, indent=2)
    print(f"[ARTIFACT] Saved zero differential audit JSON to {zero_out}")
    
    # H. Red Team JSON
    redteam_out = "scratch/zzz112_redteam.json"
    with open(redteam_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.2",
            "red_team_audit": redteam_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved Red Team JSON to {redteam_out}")
    
    print("\n================================================================================")
    print("BATCH ZZZ.11.2 EXECUTION COMPLETE")
    print("================================================================================")

if __name__ == "__main__":
    main()

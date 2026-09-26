"""
scratch/run_zzz111_coverage_aware_discrimination.py

Runner script for Batch ZZZ.11.1: Coverage-Aware Company-Specific Information Discrimination.
Executes all validation layers and produces JSON and Parquet artifacts.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.coverage_aware_discrimination_engine import CoverageAwareDiscriminationEngine

def main():
    print("================================================================================")
    print("STARTING BATCH ZZZ.11.1: COVERAGE-AWARE COMPANY-SPECIFIC DISCRIMINATION")
    print("================================================================================")
    
    # Load 3000-row baseline dataset with frozen 73 Layer-E setups
    parquet_path = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "scratch/zzz81_ablation_results.parquet"
    full_df = pd.read_parquet(parquet_path)
    print(f"Loaded dataset from {parquet_path}: Shape {full_df.shape}")
    
    engine = CoverageAwareDiscriminationEngine("data/duckdb/intelligence.duckdb")
    
    # 1. Layer A: Replicate ZZZ.11 Baseline
    print("\n--- Running Layer A: Replication of ZZZ.11 Baseline ---")
    rep_res = engine.replicate_zzz11_baseline(full_df)
    c1 = rep_res["c1_metrics"]
    c0 = rep_res["c0_unobserved_metrics"]
    print(f"C1 Evidence Present: N={c1['N']}, Mean H5={c1['mean_h5']*100:.2f}%, Mean Excess H5={c1['mean_excess_h5']*100:.2f}%, WinRate={c1['win_rate_excess_h5']*100:.2f}%")
    print(f"C0 Unobserved:       N={c0['N']}, Mean H5={c0['mean_h5']*100:.2f}%, Mean Excess H5={c0['mean_excess_h5']*100:.2f}%, WinRate={c0['win_rate_excess_h5']*100:.2f}%")
    print(f"Excess Return Delta: +{rep_res['diff_excess_h5']*100:.2f} percentage points (Permutation p = {rep_res['p_excess_c1_vs_c0_unobs']:.4f})")
    print(f"Raw Return Delta:    +{rep_res['diff_raw_h5']*100:.2f} percentage points (Permutation p = {rep_res['p_raw_c1_vs_c0_unobs']:.4f})")
    
    # Get matched DataFrame
    matched_df = engine.discrimination_engine.run_matched_discrimination_experiment(full_df)["matched_df"]
    
    # 2. Layer B: Coverage-Stratified Analysis
    print("\n--- Running Layer B: Coverage-Stratified Analysis ---")
    cov_res = engine.run_coverage_stratified_analysis(matched_df)
    print(f"Stratified Summary: {cov_res['summary']}")
    
    # 3. Layer C: Source-Available Control
    print("\n--- Running Layer C: Source-Available Control Audit ---")
    ctrl_res = engine.evaluate_source_available_control(matched_df)
    print(f"Control Status: {ctrl_res['control_status']}")
    print(f"Rationale: {ctrl_res['rationale']}")
    
    # 4. Layer D: Within-Ticker Analysis
    print("\n--- Running Layer D: Within-Ticker Control Analysis ---")
    within_res = engine.run_within_ticker_analysis(matched_df)
    print(f"Within-Ticker Status: {within_res['status']}")
    print(f"Tickers with both states: {within_res['tickers_with_both_states_count']}")
    
    # 5. Missingness Mechanism Analysis
    print("\n--- Running Missingness Mechanism Analysis ---")
    miss_res = engine.run_missingness_mechanism_analysis(matched_df, full_df)
    print(f"Classification: {miss_res['classification']}")
    print(f"Commodity Coverage Rate: {miss_res['commodity_coverage_rate']*100:.2f}% vs Non-Commodity: {miss_res['non_commodity_coverage_rate']*100:.2f}% (Delta = {miss_res['coverage_imbalance_pp']:.2f} pp)")
    
    # 6. Commodity Sensitivity
    print("\n--- Running Commodity / Non-Commodity Sensitivity ---")
    comm_res = engine.run_commodity_sensitivity(matched_df)
    print(f"Commodity Only Diff: +{comm_res['commodity_only']['diff_excess_h5']*100:.2f} pp (p = {comm_res['commodity_only']['permutation_p']:.4f})")
    print(f"Non-Commodity: {comm_res['non_commodity_only']}")
    
    # 7. Date Concentration Robustness
    print("\n--- Running Date Concentration Robustness ---")
    date_res = engine.run_date_concentration_robustness(matched_df)
    for k, v in date_res.items():
        print(f"  {k:20s}: Diff Excess H5 = +{v['diff_excess_h5']*100:.2f} pp (p = {v['permutation_p']:.4f}, N = {v['total_N']})")
        
    # 8. Ticker Concentration & Leave-One-Out
    print("\n--- Running Ticker Concentration & Leave-One-Out Sensitivity ---")
    ticker_res = engine.run_ticker_concentration_and_leave_one_out(matched_df)
    print(f"Worst Case Drop: ex-{ticker_res['worst_case_drop']['dropped_symbol']} -> Diff = +{ticker_res['worst_case_drop']['diff_excess_h5']*100:.2f} pp (p = {ticker_res['worst_case_drop']['permutation_p']:.4f})")
    print(f"Best Case Drop:  ex-{ticker_res['best_case_drop']['dropped_symbol']} -> Diff = +{ticker_res['best_case_drop']['diff_excess_h5']*100:.2f} pp (p = {ticker_res['best_case_drop']['permutation_p']:.4f})")
    
    # 9. Multi-Horizon Robustness Matrix
    print("\n--- Running Multi-Horizon Robustness Matrix ---")
    robustness_matrix = engine.run_multi_horizon_robustness_matrix(matched_df)
    
    # 10. Source Tier Sensitivity
    print("\n--- Running Source Tier Sensitivity ---")
    source_sens = engine.discrimination_engine.run_source_quality_sensitivity(full_df)
    
    # 11. Red Team 18-Dimension Audit
    print("\n--- Running 18-Dimension Red Team Audit ---")
    redteam_res = engine.run_18_dimension_red_team_audit(matched_df)
    print(f"Red Team Verdict: {redteam_res['overall_status']} ({redteam_res['passed_checks']}/{redteam_res['total_checks']} passed)")
    
    # Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # A. Results Parquet
    parquet_out = "scratch/zzz111_results.parquet"
    matched_df.to_parquet(parquet_out, index=False)
    print(f"\n[ARTIFACT] Saved results parquet to {parquet_out}")
    
    # B. Coverage Control JSON
    cov_ctrl_out = "scratch/zzz111_coverage_control.json"
    with open(cov_ctrl_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.1",
            "replication_zzz11": rep_res,
            "coverage_stratification": cov_res["summary"],
            "source_available_control": ctrl_res,
            "within_ticker_analysis": within_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved coverage control JSON to {cov_ctrl_out}")
    
    # C. Missingness Analysis JSON
    miss_out = "scratch/zzz111_missingness_analysis.json"
    with open(miss_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.1",
            "missingness_mechanism": miss_res,
            "commodity_sensitivity": comm_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved missingness analysis JSON to {miss_out}")
    
    # D. Matching Results JSON
    match_out = "scratch/zzz111_matching_results.json"
    with open(match_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.1",
            "date_concentration_robustness": date_res,
            "ticker_concentration_and_leave_one_out": ticker_res,
            "multi_horizon_robustness_matrix": robustness_matrix
        }, f, indent=2)
    print(f"[ARTIFACT] Saved matching results JSON to {match_out}")
    
    # E. Source Sensitivity JSON
    source_out = "scratch/zzz111_source_sensitivity.json"
    with open(source_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.1",
            "source_tier_sensitivity": source_sens,
            "yfinance_classification": "MARKET_DATA_PROVIDER",
            "tier_4_quarantine_status": "QUARANTINED"
        }, f, indent=2)
    print(f"[ARTIFACT] Saved source sensitivity JSON to {source_out}")
    
    # F. Red Team JSON
    redteam_out = "scratch/zzz111_redteam.json"
    with open(redteam_out, "w", encoding="utf-8") as f:
        json.dump({
            "batch_id": "BATCH-ZZZ.11.1",
            "red_team_audit": redteam_res
        }, f, indent=2)
    print(f"[ARTIFACT] Saved Red Team JSON to {redteam_out}")
    
    print("\n================================================================================")
    print("BATCH ZZZ.11.1 EXECUTION COMPLETE")
    print("================================================================================")

if __name__ == "__main__":
    main()

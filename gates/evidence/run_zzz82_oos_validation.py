"""
scratch/run_zzz82_oos_validation.py

Runner script for Batch ZZZ.8.2: Temporal & Cross-Sectional OOS Validation.
Executes Tests A through K and generates:
- scratch/zzz82_oos_results.parquet
- scratch/zzz82_oos_summary.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.oos_validation_engine import OOSValidationEngine

def main():
    print("=" * 80)
    print("BATCH ZZZ.8.2 — TEMPORAL & CROSS-SECTIONAL OOS VALIDATION")
    print("=" * 80)
    
    input_parquet = "scratch/zzz81_ablation_results.parquet"
    if not os.path.exists(input_parquet):
        input_parquet = "scratch/zzz8_experiment_results.parquet"
        
    df = pd.read_parquet(input_parquet)
    print(f"Loaded {len(df)} historical observations from {input_parquet}")
    
    engine = OOSValidationEngine(df, random_seed=42)
    
    # Frozen Contract
    contract = engine.get_frozen_signal_contract()
    print("\n--- 1. Frozen Signal Contract ---")
    print(json.dumps(contract, indent=2))
    
    # Test A: Temporal Holdout (70/30)
    print("\n--- 2. Test A: Temporal Holdout (70/30 Split) ---")
    test_a = engine.run_test_a_temporal_holdout(split_ratio=0.70)
    print(json.dumps(test_a, indent=2, default=str))
    
    # Test B: Commodity vs Non-Commodity
    print("\n--- 3. Test B: Commodity vs Non-Commodity ---")
    test_b = engine.run_test_b_commodity_vs_non_commodity()
    print(test_b[["Exposure_Category", "N", "Pct_Trades", "H3_Mean", "H5_Mean", "H10_Mean", "H20_Mean", "H5_WR"]])
    
    # Test C: Leave-One-Sector-Out
    print("\n--- 4. Test C: Leave-One-Sector-Out ---")
    test_c = engine.run_test_c_leave_one_sector_out()
    print(test_c["Table"][["Excluded_Sector", "N_Remaining", "H3_Mean", "H5_Mean", "H10_Mean", "Delta_H5_vs_Full"]])
    print("Worst Sector LOSO:", test_c["Worst_Case_Sector"])
    
    # Test D: Leave-One-Ticker-Out
    print("\n--- 5. Test D: Leave-One-Ticker-Out ---")
    test_d = engine.run_test_d_leave_one_ticker_out()
    print(test_d["Table"][["Excluded_Symbol", "N_Remaining", "H3_Mean", "H5_Mean", "H10_Mean", "Delta_H5_vs_Full"]])
    print("Worst Ticker LOTO:", test_d["Worst_Case_Ticker"])
    
    # Test E: Date Concentration
    print("\n--- 6. Test E: Date Concentration ---")
    test_e = engine.run_test_e_date_concentration()
    print("Exclusions:")
    print(json.dumps(test_e["Exclusions"], indent=2))
    print(f"Top 1 Date Pct: {test_e['Top_1_Date_Contribution_Pct']:.2f}%")
    print(f"Top 3 Dates Pct: {test_e['Top_3_Date_Contribution_Pct']:.2f}%")
    print(f"Top 5 Dates Pct: {test_e['Top_5_Date_Contribution_Pct']:.2f}%")
    
    # Test F: Commodity Concentration
    print("\n--- 7. Test F: Commodity Concentration ---")
    test_f = engine.run_test_f_commodity_concentration()
    print("Full Sample H5:", test_f["Full_Sample"]["Stats"]["H5"]["mean"])
    print("Commodity H5:", test_f["Commodity_Only"]["Stats"]["H5"]["mean"])
    print("Non-Commodity H5:", test_f["Non_Commodity_Only"]["Stats"]["H5"]["mean"])
    print("Verdict:", test_f["Verdict"])
    
    # Test G: Interaction Audit
    print("\n--- 8. Test G: Component Interaction Audit ---")
    test_g = engine.run_test_g_interaction_audit()
    print(test_g[["Configuration", "N", "H3_Mean", "H5_Mean", "H10_Mean", "H20_Mean", "H5_WR"]])
    
    # Test H: Matched Controls
    print("\n--- 9. Test H: Matched Controls ---")
    test_h = engine.run_test_h_matched_controls(n_iterations=2000)
    print("Layer E Observed:", test_h["Layer_E_Observed"])
    print("Date Matched:", test_h["Date_Matched_Control"])
    print("Ticker Matched:", test_h["Ticker_Matched_Control"])
    print("Cross Ticker Control:", test_h["Cross_Ticker_Non_Signal_Control"])
    
    # Test I: Statistical Robustness
    print("\n--- 10. Test I: Statistical Robustness (Date-Clustered Bootstrap 10k & Permutation 5k) ---")
    test_i = engine.run_test_i_statistical_robustness(n_bootstrap=10000, n_permutation=5000)
    print(test_i)
    
    # Test J: Regime & Date Structure
    print("\n--- 11. Test J: Regime & Date Structure ---")
    test_j = engine.run_test_j_regime_and_date_structure()
    print("Calendar Quarters:")
    print(test_j["Calendar_Quarters"])
    print("Signal Density:", test_j["Signal_Density"])
    
    # Test K: Failure Analysis
    print("\n--- 12. Test K: Failure Analysis ---")
    test_k = engine.run_test_k_failure_analysis()
    print(json.dumps(test_k, indent=2))
    
    # Save Parquet
    out_parquet = "scratch/zzz82_oos_results.parquet"
    engine.df.to_parquet(out_parquet, index=False)
    print(f"\nSaved parquet to {out_parquet}")
    
    # Summary JSON
    summary = {
        "metadata": {
            "batch": "ZZZ.8.2",
            "experiment": "Temporal & Cross-Sectional OOS Validation",
            "observations_total": len(df),
            "baseline_candidates": int(df["sel_baseline"].sum()),
            "layer_e_candidates": int(df["sel_layer_e"].sum()),
            "random_seed": 42
        },
        "contract": contract,
        "test_a_temporal_holdout": test_a,
        "test_b_commodity_vs_non_commodity": test_b.to_dict(orient="records"),
        "test_c_leave_one_sector_out": {
            "table": test_c["Table"].to_dict(orient="records"),
            "worst_case": test_c["Worst_Case_Sector"],
            "best_case": test_c["Best_Case_Sector"],
            "median_h5": test_c["Median_LOSO_H5"],
            "median_h10": test_c["Median_LOSO_H10"]
        },
        "test_d_leave_one_ticker_out": {
            "table": test_d["Table"].to_dict(orient="records"),
            "worst_case": test_d["Worst_Case_Ticker"],
            "best_case": test_d["Best_Case_Ticker"],
            "median_h5": test_d["Median_LOTO_H5"],
            "median_h10": test_d["Median_LOTO_H10"]
        },
        "test_e_date_concentration": test_e,
        "test_f_commodity_concentration": test_f,
        "test_g_interaction_audit": test_g.to_dict(orient="records"),
        "test_h_matched_controls": test_h,
        "test_i_statistical_robustness": test_i.to_dict(orient="records"),
        "test_j_regime_and_date_structure": {
            "calendar_quarters": test_j["Calendar_Quarters"].to_dict(orient="records"),
            "signal_density": test_j["Signal_Density"]
        },
        "test_k_failure_analysis": test_k
    }
    
    out_json = "scratch/zzz82_oos_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved summary JSON to {out_json}")

if __name__ == "__main__":
    main()

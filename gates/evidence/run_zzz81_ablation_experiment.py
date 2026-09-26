"""
scratch/run_zzz81_ablation_experiment.py

Runner script for Batch ZZZ.8.1: Controlled Ablation & Selection Robustness Experiment.
Executes Experiments 1 to 10 and produces machine-readable artifacts:
- scratch/zzz81_ablation_results.parquet
- scratch/zzz81_ablation_summary.json
"""

import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ablation_engine import AblationEngine

def main():
    print("=" * 80)
    print("BATCH ZZZ.8.1 — ABLATION & SELECTION ROBUSTNESS EXPERIMENT")
    print("=" * 80)
    
    input_parquet = "scratch/zzz8_experiment_results.parquet"
    if not os.path.exists(input_parquet):
        print(f"ERROR: Input parquet {input_parquet} not found!")
        sys.exit(1)
        
    df = pd.read_parquet(input_parquet)
    print(f"Loaded {len(df)} historical observations from {input_parquet}")
    
    engine = AblationEngine(df, random_seed=42)
    
    # 1. Layer E Contract
    print("\n--- 1. Reconstructing Frozen Layer E Contract ---")
    contract_info = engine.get_layer_e_contract()
    print(json.dumps(contract_info, indent=2))
    
    # 2. Experiment 1: Single Component Ablation
    print("\n--- 2. Running Experiment 1: Single Component Addition ---")
    exp1_df = engine.run_experiment_1_single_ablation()
    print(exp1_df[["Configuration", "N", "Selection_Rate", "H5_Mean", "H10_Mean", "Incremental_H5_vs_D", "H5_WR"]])
    
    # 3. Experiment 2: Leave-One-Component-Out (Primary Ablation)
    print("\n--- 3. Running Experiment 2: Leave-One-Component-Out ---")
    exp2_df = engine.run_experiment_2_leave_one_out()
    print(exp2_df[["Configuration", "N", "Delta_N_vs_FULL", "H5_Mean", "H10_Mean", "Contribution_H5", "Contribution_H10", "H5_WR"]])
    
    # 4. Experiment 4: Sequential Build-Up Funnel
    print("\n--- 4. Running Experiment 4: Sequential Build-Up Funnel ---")
    exp4_df = engine.run_experiment_4_sequential_buildup()
    print(exp4_df)
    
    # 5. Experiment 5: Matched-Selection Control
    print("\n--- 5. Running Experiment 5: Matched-Selection Control ---")
    exp5_res = engine.run_experiment_5_matched_selection_control(n_iterations=2000)
    print("Layer E:", exp5_res["Layer_E"])
    print("Random Matched:", exp5_res["Random_Matched"])
    print("Date Matched:", exp5_res["Date_Matched"])
    print("Ticker Matched:", exp5_res["Ticker_Matched"])
    
    # 6. Experiment 6: Ticker Concentration
    print("\n--- 6. Running Experiment 6: Ticker Concentration & LOTO ---")
    exp6_res = engine.run_experiment_6_ticker_concentration()
    print("Ticker Breakdown:")
    print(exp6_res["Ticker_Breakdown"])
    print("Leave-One-Ticker-Out:")
    print(exp6_res["Leave_One_Ticker_Out"])
    print("Worst-Case LOTO:", exp6_res["Worst_Case_LOTO"])
    
    # 7. Experiment 7: Sector Concentration
    print("\n--- 7. Running Experiment 7: Sector Concentration & LOSO ---")
    exp7_res = engine.run_experiment_7_sector_concentration()
    print("Sector Breakdown:")
    print(exp7_res["Sector_Breakdown"])
    print("Leave-One-Sector-Out:")
    print(exp7_res["Leave_One_Sector_Out"])
    print("Worst-Case LOSO:", exp7_res["Worst_Case_LOSO"])
    
    # 8. Experiment 8: Date Concentration
    print("\n--- 8. Running Experiment 8: Date Concentration ---")
    exp8_res = engine.run_experiment_8_date_concentration()
    print("Top 10 Dates:")
    print(exp8_res["Date_Group_Top_10"])
    print("Exclusions Summary:")
    print(json.dumps(exp8_res["Exclusions"], indent=2))
    print(f"Top 1 Date Return Pct: {exp8_res['Top_1_Date_Pct']:.2f}%")
    print(f"Top 3 Dates Return Pct: {exp8_res['Top_3_Dates_Pct']:.2f}%")
    print(f"Top 5 Dates Return Pct: {exp8_res['Top_5_Dates_Pct']:.2f}%")
    
    # 9. Experiment 9: Regime Analysis
    print("\n--- 9. Running Experiment 9: Regime Robustness ---")
    exp9_res = engine.run_experiment_9_regime_robustness()
    print(json.dumps({k: v for k, v in exp9_res.items() if k != 'Table'}, indent=2))
    
    # 10. Experiment 10: Complete Horizon Profile
    print("\n--- 10. Running Experiment 10: Horizon Profile ---")
    exp10_df = engine.run_experiment_10_horizon_shape()
    print(exp10_df)
    
    # 11. Statistical Validation (Bootstrap & Permutation)
    print("\n--- 11. Running Clustered Bootstrap & Permutation Tests (10k/5k) ---")
    stat_df = engine.run_statistical_validation(n_bootstrap=10000, n_permutation=5000)
    print(stat_df)
    
    # Save Results Parquet
    out_parquet = "scratch/zzz81_ablation_results.parquet"
    engine.df.to_parquet(out_parquet, index=False)
    print(f"\nSaved full results to {out_parquet}")
    
    # Construct Summary JSON
    summary = {
        "metadata": {
            "batch": "ZZZ.8.1",
            "experiment": "Controlled Ablation & Selection Robustness",
            "observations_total": len(df),
            "baseline_candidates": int(df["sel_baseline"].sum()),
            "layer_d_candidates": int(df["sel_layer_d"].sum()),
            "layer_e_candidates": int(df["sel_layer_e"].sum()),
            "random_seed": 42
        },
        "layer_e_contract": contract_info,
        "experiment_1_single_ablation": exp1_df.to_dict(orient="records"),
        "experiment_2_leave_one_out": exp2_df.to_dict(orient="records"),
        "experiment_4_sequential_buildup": exp4_df.to_dict(orient="records"),
        "experiment_5_matched_controls": exp5_res,
        "experiment_6_ticker_concentration": {
            "ticker_breakdown": exp6_res["Ticker_Breakdown"].to_dict(orient="records"),
            "leave_one_ticker_out": exp6_res["Leave_One_Ticker_Out"].to_dict(orient="records"),
            "worst_case_loto": exp6_res["Worst_Case_LOTO"]
        },
        "experiment_7_sector_concentration": {
            "sector_breakdown": exp7_res["Sector_Breakdown"].to_dict(orient="records"),
            "leave_one_sector_out": exp7_res["Leave_One_Sector_Out"].to_dict(orient="records"),
            "worst_case_loso": exp7_res["Worst_Case_LOSO"]
        },
        "experiment_8_date_concentration": {
            "top_1_date_pct": exp8_res["Top_1_Date_Pct"],
            "top_3_dates_pct": exp8_res["Top_3_Dates_Pct"],
            "top_5_dates_pct": exp8_res["Top_5_Dates_Pct"],
            "exclusions": exp8_res["Exclusions"]
        },
        "experiment_9_regime_robustness": {
            "status": exp9_res["Status"],
            "explanation": exp9_res.get("Explanation", "")
        },
        "experiment_10_horizon_shape": exp10_df.to_dict(orient="records"),
        "statistical_validation": stat_df.to_dict(orient="records")
    }
    
    out_json = "scratch/zzz81_ablation_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved summary metrics to {out_json}")
    print("\nExecution complete.")

if __name__ == "__main__":
    main()

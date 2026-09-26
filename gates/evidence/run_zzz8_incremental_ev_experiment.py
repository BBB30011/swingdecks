import os
import sys
import json
import numpy as np
import pandas as pd
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.multi_agent_experiment_engine import MultiAgentExperimentEngine

def run_zzz8_experiment():
    print("Loading data from scratch/zzz62_observations.parquet and scratch/zzz71_candidate_attributions.parquet...", flush=True)
    df62 = pd.read_parquet("scratch/zzz62_observations.parquet")
    df71 = pd.read_parquet("scratch/zzz71_candidate_attributions.parquet")
    
    # Merge datasets on symbol and date
    merge_cols = [c for c in df71.columns if c not in df62.columns or c in ["symbol", "date"]]
    df_merged = pd.merge(df62, df71[merge_cols], on=["symbol", "date"], how="inner")
    print(f"Successfully merged {len(df_merged)} observations.", flush=True)
    
    # Initialize and execute Multi-Agent Engine
    print("Evaluating 6-layer Multi-Agent Ladder...", flush=True)
    engine = MultiAgentExperimentEngine(df_merged, random_seed=42)
    df_evaluated = engine.evaluate_layers()
    
    # Compute Layer Metrics
    print("Computing metrics across all layers and horizons (H1, H3, H5, H10, H20)...", flush=True)
    layer_metrics = engine.compute_layer_metrics()
    
    # Compute Incremental EV
    print("Computing Step-by-Step and Full Incremental EV...", flush=True)
    incremental_ev = engine.compute_incremental_ev(layer_metrics)
    
    # Run Bootstrap & Permutation Validation
    print("Running IID Bootstrap, Date-Clustered Bootstrap (10,000 resamples), and Permutation Tests (5,000 perms)...", flush=True)
    bootstrap_results = engine.run_bootstrap_validation(n_iterations=10000)
    
    # Run Robustness & Concentration Analysis
    print("Running Ticker Concentration and Date Clustering Analysis...", flush=True)
    robustness_results = engine.compute_robustness_and_concentration()
    
    # Save Evaluated Parquet
    out_parquet = "scratch/zzz8_experiment_results.parquet"
    df_evaluated.to_parquet(out_parquet, index=False)
    print(f"Saved evaluated experiment dataset to {out_parquet}", flush=True)
    
    # Combine everything into Summary JSON
    summary = {
        "metadata": {
            "experiment_id": "BATCH_ZZZ_8_INCREMENTAL_EV_EXPERIMENT",
            "timestamp": "2026-09-14T14:15:00Z",
            "total_observations": len(df_evaluated),
            "n_baseline_candidates": int(df_evaluated["sel_baseline"].sum()),
            "n_layer_a_candidates": int(df_evaluated["sel_layer_a"].sum()),
            "n_layer_b_candidates": int(df_evaluated["sel_layer_b"].sum()),
            "n_layer_c_candidates": int(df_evaluated["sel_layer_c"].sum()),
            "n_layer_d_candidates": int(df_evaluated["sel_layer_d"].sum()),
            "n_layer_e_candidates": int(df_evaluated["sel_layer_e"].sum())
        },
        "layer_metrics": layer_metrics,
        "incremental_ev": incremental_ev,
        "statistical_validation": bootstrap_results,
        "robustness_and_concentration": robustness_results
    }
    
    out_json = "scratch/zzz8_experiment_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"Saved complete experiment summary to {out_json}", flush=True)
    
    # Print Executive Comparison Table
    print("\n" + "="*110)
    print(f"{'Layer':<10} | {'Architecture':<20} | {'N':<6} | {'Sel Rate':<9} | {'H1 (%)':<8} | {'H3 (%)':<8} | {'H5 (%)':<8} | {'H10 (%)':<8} | {'H20 (%)':<8} | {'H5 Win%':<8} | {'Status'}")
    print("="*110)
    
    names_map = {
        "Baseline": ("Agent 1 (Alone)", "Baseline"),
        "Layer_A": ("A1 + Peer Context", "Layer A"),
        "Layer_B": ("A1 + Differential", "Layer B"),
        "Layer_C": ("A1 + A2 + Red Team", "Layer C"),
        "Layer_D": ("A1 + A2 + RT + A3", "Layer D"),
        "Layer_E": ("Full 3-Agent", "Layer E")
    }
    
    for l_key in ["Baseline", "Layer_A", "Layer_B", "Layer_C", "Layer_D", "Layer_E"]:
        m = layer_metrics[l_key]
        arch, label = names_map[l_key]
        n = m["n"]
        sel_rate = f"{m['selection_rate']*100:.1f}%"
        h1 = f"{m['horizons']['H1']['mean']*100:+.2f}%"
        h3 = f"{m['horizons']['H3']['mean']*100:+.2f}%"
        h5 = f"{m['horizons']['H5']['mean']*100:+.2f}%"
        h10 = f"{m['horizons']['H10']['mean']*100:+.2f}%"
        h20 = f"{m['horizons']['H20']['mean']*100:+.2f}%"
        win5 = f"{m['horizons']['H5']['win_rate']*100:.1f}%"
        
        status = "PASS" if m["horizons"]["H5"]["mean"] > 0 else "FAIL"
        print(f"{label:<10} | {arch:<20} | {n:<6} | {sel_rate:<9} | {h1:<8} | {h3:<8} | {h5:<8} | {h10:<8} | {h20:<8} | {win5:<8} | {status}")
    print("="*110)

if __name__ == "__main__":
    run_zzz8_experiment()

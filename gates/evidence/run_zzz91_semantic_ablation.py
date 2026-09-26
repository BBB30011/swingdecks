"""
scratch/run_zzz91_semantic_ablation.py

Runner script for Batch ZZZ.9.1: Semantic Attribution Ablation & Causal-Discipline Audit.
Executes the A0-A5 nested ablation hierarchy, matched controls, permutation tests,
future injection test, and universe scope audit.
Exports machine-readable parquet and summary JSON artifacts.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.semantic_ablation_engine import SemanticAblationEngine

def main():
    print("=" * 80)
    print("BATCH ZZZ.9.1 — SEMANTIC ATTRIBUTION ABLATION & CAUSAL-DISCIPLINE AUDIT")
    print("=" * 80)
    
    input_parquet = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(input_parquet):
        input_parquet = "scratch/zzz81_ablation_results.parquet"
        
    df = pd.read_parquet(input_parquet)
    print(f"\nLoaded {len(df)} historical observations from {input_parquet}")
    layer_e_count = int(df["sel_layer_e"].sum()) if "sel_layer_e" in df.columns else 0
    print(f"Layer E Candidates present: {layer_e_count}")
    
    engine = SemanticAblationEngine()
    
    # 1. Universe Scope Audit
    print("\n--- 1. Auditing Universe Scope ---")
    universe_audit = engine.audit_universe_scope(df)
    print(f"Pilot Universe Count: {universe_audit['pilot_universe_count']}")
    print(f"Out of Universe Exceptions: {universe_audit['out_of_universe_symbols']} (Count: {universe_audit['universe_scope_exception_count']})")
    print(f"UNTR Classification: {universe_audit['untr_classification']}")
    print(f"Scope Status: {universe_audit['scope_audit_status']}")
    
    # 2. Future Injection Leakage Test
    print("\n--- 2. Executing Future Event Injection Leakage Test ---")
    sample_cand = df[df["symbol"] == "ADRO"].iloc[0].to_dict()
    day_universe = df[df["date"] == sample_cand["date"]].to_dict(orient="records")
    injection_audit = engine.run_future_injection_audit(sample_cand, day_universe, future_delta_days=2)
    print(f"Candidate T: {injection_audit['candidate_timestamp_t']}")
    print(f"Future Injected Event at: {injection_audit['future_event_injected_at']}")
    print(f"Found in Reconstruction at T: {injection_audit['future_event_found_at_t']}")
    print(f"Leakage Test Status: {injection_audit['leakage_status']}")
    
    # 3. Execute Nested Ablation A0 -> A5
    print("\n--- 3. Executing Nested Ablation A0 -> A5 ---")
    ablation_results = engine.run_nested_ablation(df)
    
    print("\n--- ABLATION PERFORMANCE LADDER (A0 -> A5) ---")
    print(f"{'Layer':<6} | {'Description':<40} | {'N':>4} | {'H1 Mean':>8} | {'H3 Mean':>8} | {'H5 Mean':>8} | {'H10 Mean':>8} | {'H20 Mean':>8} | {'WinRate':>7}")
    print("-" * 115)
    for l in ablation_results["layers"]:
        print(f"{l['layer_name']:<6} | {l['description']:<40} | {l['N']:>4} | {l['mean_h1']*100:>7.2f}% | {l['mean_h3']*100:>7.2f}% | {l['mean_h5']*100:>7.2f}% | {l['mean_h10']*100:>7.2f}% | {l['mean_h20']*100:>7.2f}% | {l['win_rate_h5']*100:>6.1f}%")
        
    print("\n--- INCREMENTAL DELTAS (STEP-BY-STEP LIFT) ---")
    print(f"{'Step':<20} | {'Delta N':>8} | {'Delta H1':>8} | {'Delta H3':>8} | {'Delta H5':>8} | {'Delta H10':>8} | {'Delta H20':>8} | {'Delta WinRate':>13}")
    print("-" * 100)
    for d in ablation_results["deltas"]:
        print(f"{d['step']:<20} | {d['delta_N']:>8} | {d['delta_H1']*100:>+7.2f}% | {d['delta_H3']*100:>+7.2f}% | {d['delta_H5']*100:>+7.2f}% | {d['delta_H10']*100:>+7.2f}% | {d['delta_H20']*100:>+7.2f}% | {d['delta_win_rate']*100:>+12.1f}%")
        
    tot = ablation_results["total_delta"]
    print("-" * 100)
    print(f"{tot['step']:<20} | {tot['delta_N']:>8} | {tot['delta_H1']*100:>+7.2f}% | {tot['delta_H3']*100:>+7.2f}% | {tot['delta_H5']*100:>+7.2f}% | {tot['delta_H10']*100:>+7.2f}% | {tot['delta_H20']*100:>+7.2f}% | {tot['delta_win_rate']*100:>+12.1f}%")
    
    print("\n--- STATISTICAL TESTS & PERMUTATION P-VALUES ---")
    for k, v in ablation_results["permutation_p_values"].items():
        print(f"{k}: p = {v:.4f}")
        
    print("\n--- MATCHED-SELECTION CONTROLS ---")
    for k, v in ablation_results["controls"].items():
        if "p_value" in k:
            print(f"{k}: p = {v:.4f}")
        else:
            print(f"{k}: mean = {v*100:+.2f}%")
            
    # 4. Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    out_parquet = "scratch/zzz91_ablation_results.parquet"
    out_json = "scratch/zzz91_ablation_summary.json"
    
    ablation_results["summary_df"].to_parquet(out_parquet, index=False)
    
    # Format JSON clean output
    json_data = {
        "metadata": {
            "batch": "ZZZ.9.1",
            "experiment": "Semantic Attribution Ablation & Causal-Discipline Audit",
            "universe_scope": universe_audit,
            "future_injection_audit": injection_audit,
            "random_seed": 42
        },
        "layers": ablation_results["layers"],
        "deltas": ablation_results["deltas"],
        "total_delta": ablation_results["total_delta"],
        "permutation_p_values": ablation_results["permutation_p_values"],
        "controls": ablation_results["controls"]
    }
    
    with open(out_json, "w") as f:
        json.dump(json_data, f, indent=2)
        
    print(f"\nSaved parquet artifact to {out_parquet}")
    print(f"Saved summary JSON artifact to {out_json}")
    print("\n" + "=" * 80)
    print("BATCH ZZZ.9.1 RUN COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

"""
scratch/run_zzz10_company_specific_discrimination.py

Runner script for Batch ZZZ.10: Company-Specific Information Discrimination.
Executes matched exposure comparisons (C0, C1, C2, C3), future injection audits (T+1, T+2, T+5),
evaluates differential excess returns over peers, and generates summary artifacts.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.company_specific_discrimination_engine import CompanySpecificDiscriminationEngine, EXPOSURE_GROUPS

def main():
    print("=" * 80)
    print("BATCH ZZZ.10 — COMPANY-SPECIFIC INFORMATION DISCRIMINATION")
    print("=" * 80)
    
    input_parquet = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(input_parquet):
        input_parquet = "scratch/zzz81_ablation_results.parquet"
        
    df = pd.read_parquet(input_parquet)
    print(f"\nLoaded {len(df)} historical observations from {input_parquet}")
    layer_e_count = int(df["sel_layer_e"].sum()) if "sel_layer_e" in df.columns else 0
    print(f"Layer E Candidates present: {layer_e_count}")
    
    engine = CompanySpecificDiscriminationEngine()
    
    # 1. Multi-Horizon Future Injection Test (T+1, T+2, T+5)
    print("\n--- 1. Executing Future Event Injection Audit (T+1, T+2, T+5) ---")
    sample_cand = df[df["symbol"] == "ADRO"].iloc[0].to_dict()
    inj_res = engine.run_future_injection_audit_suite(sample_cand, future_deltas=[1, 2, 5])
    for r in inj_res["audit_results"]:
        print(f"Injected at T+{r['future_delta_days']} ({r['injected_at']}): Found at T = {r['found_at_T']} -> Status: {r['leakage_status']}")
    print(f"Overall Future Injection Status: {inj_res['overall_status']} (Future Leaks: {inj_res['future_evidence_used_count']})")
    
    # 2. Matched Discrimination Experiment across Exposure Groups
    print("\n--- 2. Executing Matched Exposure Discrimination Experiment ---")
    results = engine.run_matched_discrimination_experiment(df)
    
    m_df = results["matched_df"]
    c0 = results["c0_metrics"]
    c1 = results["c1_metrics"]
    c0_no = results["c0_no_event_metrics"]
    c2 = results["c2_metrics"]
    c3 = results["c3_metrics"]
    
    print("\n--- PERFORMANCE ACROSS INFORMATION STATES (C0 -> C3) ---")
    print(f"{'State':<28} | {'N':>4} | {'H1 Mean':>8} | {'H3 Mean':>8} | {'H5 Mean':>8} | {'H10 Mean':>8} | {'Excess H5':>10} | {'WinRate':>7}")
    print("-" * 95)
    for m in [c0, c0_no, c1, c2, c3]:
        print(f"{m['label']:<28} | {m['N']:>4} | {m.get('mean_h1', 0)*100:>7.2f}% | {m.get('mean_h3', 0)*100:>7.2f}% | {m.get('mean_h5', 0)*100:>7.2f}% | {m.get('mean_h10', 0)*100:>7.2f}% | {m.get('mean_excess_h5', 0)*100:>+9.2f}% | {m.get('win_rate_h5', 0)*100:>6.1f}%")
        
    print("\n--- INCREMENTAL DIFFERENTIAL (C1 Event vs C0 No-Event Peer) ---")
    delta_h5 = c1["mean_h5"] - c0_no["mean_h5"] if c0_no["N"] > 0 and c1["N"] > 0 else 0.0
    delta_excess_h5 = c1["mean_excess_h5"] - c0_no["mean_excess_h5"] if c0_no["N"] > 0 and c1["N"] > 0 else 0.0
    delta_win = c1["win_rate_h5"] - c0_no["win_rate_h5"] if c0_no["N"] > 0 and c1["N"] > 0 else 0.0
    print(f"Delta H5 Return (C1 - C0_no_event): {delta_h5*100:+.2f}%")
    print(f"Delta Excess Return vs Peers (C1 - C0_no_event): {delta_excess_h5*100:+.2f}%")
    print(f"Delta Win Rate: {delta_win*100:+.1f}%")
    print(f"Permutation p-value (Absolute H5): p = {results['p_event_vs_no_event']:.4f}")
    print(f"Permutation p-value (Excess H5 vs Peers): p = {results['p_excess_event_vs_no_event']:.4f}")
    
    # 3. Information Discrimination Matrix Sample
    print("\n--- SAMPLE INFORMATION DISCRIMINATION MATRIX ---")
    sample_rows = m_df.head(10)
    print(f"{'Symbol':<6} | {'Date':<10} | {'Group':<14} | {'Has Event':<9} | {'Diff Day':>8} | {'Target H5':>9} | {'Peer H5':>8} | {'Excess H5':>9}")
    print("-" * 90)
    for _, r in sample_rows.iterrows():
        print(f"{r['target_symbol']:<6} | {r['target_date'][:10]:<10} | {r['exposure_group']:<14} | {str(r['has_company_specific_event']):<9} | {r['differential_day_return']*100:>+7.2f}% | {r['target_h5']*100:>+8.2f}% | {r['matched_peer_mean_h5']*100:>+7.2f}% | {r['excess_h5_vs_peers']*100:>+8.2f}%")
        
    # 4. Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    out_parquet = "scratch/zzz10_results.parquet"
    out_json = "scratch/zzz10_summary.json"
    
    m_df.to_parquet(out_parquet, index=False)
    
    json_summary = {
        "metadata": {
            "batch": "ZZZ.10",
            "experiment": "Company-Specific Information Discrimination",
            "future_injection_audit": inj_res,
            "exposure_groups": EXPOSURE_GROUPS,
            "random_seed": 42
        },
        "states": {
            "C0_ALL_BASELINE": c0,
            "C0_NO_EVENT_PEER": c0_no,
            "C1_COMPANY_SPECIFIC_EVENT": c1,
            "C2_AGENT2_THESIS": c2,
            "C3_RED_TEAM_PASS": c3
        },
        "incremental_deltas": {
            "delta_h5": delta_h5,
            "delta_excess_h5": delta_excess_h5,
            "delta_win_rate": delta_win,
            "p_event_vs_no_event": results["p_event_vs_no_event"],
            "p_excess_event_vs_no_event": results["p_excess_event_vs_no_event"]
        }
    }
    
    with open(out_json, "w") as f:
        json.dump(json_summary, f, indent=2)
        
    print(f"\nSaved parquet artifact to {out_parquet}")
    print(f"Saved summary JSON artifact to {out_json}")
    print("\n" + "=" * 80)
    print("BATCH ZZZ.10 RUN COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()

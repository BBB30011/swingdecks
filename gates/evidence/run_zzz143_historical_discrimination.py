"""
scratch/run_zzz143_historical_discrimination.py

Execution runner for Batch ZZZ.14.3: Agent 2 Historical Discrimination Pilot.
Executes HistoricalDiscriminationEngine, verifies thesis freeze pre-outcome,
evaluates nested information layers A0->A5, stratifications, and concentration,
and writes all 9 required artifacts to scratch/.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_discrimination_engine import HistoricalDiscriminationEngine

def main():
    print("=" * 80)
    print("STARTING BATCH ZZZ.14.3: AGENT 2 HISTORICAL DISCRIMINATION PILOT")
    print("=" * 80)

    engine = HistoricalDiscriminationEngine()
    results = engine.execute_full_pilot_analysis()

    df_obs = results["df_obs"]
    layer_results = results["layer_results"]
    strat_results = results["strat_results"]
    conc_results = results["conc_results"]
    elig_results = results["elig_results"]
    statistical_results = results["statistical_results"]
    red_team_results = results["red_team_results"]

    print(f"\n[OK] Historical Replay & Discrimination Complete across {len(df_obs)} observations.")

    # 1. Layer Results Table
    print("\n" + "=" * 90)
    print("PRIMARY ANALYSIS: NESTED INFORMATION LAYERS (A0 -> A5) — ENDPOINT: H5 PEER-EXCESS")
    print("=" * 90)
    print(f"{'Layer':<6} | {'Information Layer':<28} | {'N':>4} | {'H5 Mean':>9} | {'H5 Median':>9} | {'95% CI':>20} | {'Incremental Delta':>18} | {'Status':<25}")
    print("-" * 135)
    for l in layer_results["layers"]:
        ci_str = f"[{l['ci_95_pct'][0]:+.2f}%, {l['ci_95_pct'][1]:+.2f}%]" if not np.isnan(l['ci_95_pct'][0]) else "N/A"
        inc_str = f"{l['incremental_vs_previous_pp']:+.2f} pp" if l['incremental_vs_previous_pp'] is not None else "—"
        print(f"{l['layer']:<6} | {l['information']:<28} | {l['N']:>4} | {l['h5_peer_excess_mean_pct']:+8.2f}% | {l['h5_peer_excess_median_pct']:+8.2f}% | {ci_str:>20} | {inc_str:>18} | {l['status']:<25}")

    # 2. Stratification Table
    print("\n" + "=" * 90)
    print("STRATIFICATION RESULTS (PRIMARY ENDPOINT: H5 PEER-EXCESS)")
    print("=" * 90)
    print(f"{'Stratum':<35} | {'N':>4} | {'H5 Mean':>9} | {'H5 Median':>9} | {'95% CI':>20} | {'Raw H5 Mean':>12} | {'Status':<15}")
    print("-" * 115)
    for s in strat_results["stratifications"]:
        ci_str = f"[{s['ci_95'][0]:+.2f}%, {s['ci_95'][1]:+.2f}%]" if not np.isnan(s['ci_95'][0]) else "N/A"
        print(f"{s['stratum']:<35} | {s['N']:>4} | {s['h5_peer_excess_mean_pct']:+8.2f}% | {s['h5_peer_excess_median_pct']:+8.2f}% | {ci_str:>20} | {s['raw_h5_mean_pct']:+10.2f}% | {s['status']:<15}")

    # 3. Concentration Audit
    print("\n" + "=" * 90)
    print("CONCENTRATION & SENSITIVITY AUDIT")
    print("=" * 90)
    print(f"Top 1 Date Contribution: {conc_results['top_1_date'].get('decision_date', 'N/A')} (Mean H5: {conc_results['top_1_date'].get('mean', 0.0)*100:+.2f}%)")
    print("Top 3 Dates Contribution:")
    for d in conc_results["top_3_dates"]:
        print(f"  - {d['decision_date']}: N={d['count']}, Mean H5={d['mean']*100:+.2f}%")

    # 4. Red Team Audit
    print("\n" + "=" * 90)
    print("20-POINT RED TEAM VALIDATION AUDIT")
    print("=" * 90)
    for c in red_team_results["checks"]:
        print(f"[{c['status']}] {c['check_id']}: {c['name']}")

    print("\n" + "=" * 90)
    print(f"FINAL PILOT VERDICT: {statistical_results['hypothesis_test_result']}")
    print(f"OVERALL RED TEAM VERDICT: {red_team_results['overall_red_team_verdict']}")
    print("=" * 90)

if __name__ == "__main__":
    main()

"""
scratch/run_zzz1434_matched_event_cluster.py

Runner script for Batch ZZZ.14.3.4 Pre-T Matched Counterfactual & Event-Cluster Attribution Gate.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json
import pandas as pd

from core.matched_event_cluster_engine import MatchedEventClusterEngine

def main():
    print("=== STARTING BATCH ZZZ.14.3.4 MATCHED EVENT CLUSTER PIPELINE ===")
    engine = MatchedEventClusterEngine()
    manifest = engine.run_full_pipeline()

    print("\n=== BASELINE REPLICATION (GATE A) ===")
    print(f"Treatment Mean: {manifest['baseline_replication']['treatment_mean_h5_excess_pct']:+.4f}%")
    print(f"Control Mean: {manifest['baseline_replication']['control_mean_h5_excess_pct']:+.4f}%")
    print(f"Differential: {manifest['baseline_replication']['differential_mean_pp']:+.4f} pp (Expected: +3.1037 pp, Delta: {manifest['baseline_replication']['replication_delta_pp']:.6f} pp)")

    print("\n=== MATCHING SUMMARY (M1) ===")
    print(f"Matched Pairs: {manifest['matched_summary']['matched_pairs_count']}")
    print(f"Matched Diff: {manifest['matched_summary']['matched_differential_pp']:+.4f} pp (Attenuation: {manifest['matched_summary']['attenuation_pct']:.2f}%)")

    print("\n=== EVENT DEPENDENCE & CLUSTER AUDIT (E1 & M2) ===")
    print(f"Unique Events: {manifest['event_dependence_summary']['unique_events_count']}")
    print(f"Max Event Reuse: {manifest['event_dependence_summary']['max_event_reuse_id']} (Count: {manifest['event_dependence_summary']['max_event_reuse_count']})")
    print(f"E1 Event-Cluster Coef: {manifest['e1_event_cluster_summary']['evidence_coef_pp']:+.4f} pp (Robust SE: {manifest['e1_event_cluster_summary']['cluster_robust_se_pp']:.4f}, p: {manifest['e1_event_cluster_summary']['p_value']:.4f})")
    print(f"M2 Matched Event-Cluster Coef: {manifest['m2_matched_event_cluster_summary']['evidence_coef_pp']:+.4f} pp (Robust SE: {manifest['m2_matched_event_cluster_summary']['cluster_robust_se_pp']:.4f}, p: {manifest['m2_matched_event_cluster_summary']['p_value']:.4f})")

    print("\n=== EVENT EQUALIZED SENSITIVITY (E2) ===")
    print(f"Event Equalized Diff: {manifest['e2_event_equalized_summary']['event_equalized_differential_pp']:+.4f} pp")

    print("\n=== LEAVE-ONE-EVENT-OUT (E3) ===")
    print(f"Iterations: {manifest['e3_leave_one_event_out_summary']['total_iterations']}")
    print(f"Range: [{manifest['e3_leave_one_event_out_summary']['min_differential_pp']:+.4f} pp, {manifest['e3_leave_one_event_out_summary']['max_differential_pp']:+.4f} pp]")
    print(f"Median: {manifest['e3_leave_one_event_out_summary']['median_differential_pp']:+.4f} pp, Sign Changes: {manifest['e3_leave_one_event_out_summary']['sign_changes_count']}")

    print("\n=== RED TEAM 25 ATTACKS (GATE I) ===")
    print(f"Passed: {manifest['redteam_attacks_summary']['passed_attacks']}/{manifest['redteam_attacks_summary']['total_attacks']}")

    print("\n=== REPRODUCIBILITY (GATE H) ===")
    print(f"Status: {manifest['reproducibility_summary']['status']}")

    print("\n=== GATES SUMMARY ===")
    print(json.dumps(manifest["gates"], indent=2))

    print("\n=== RESULT MATRIX PREVIEW ===")
    df_res = pd.read_csv("reports/zzz14_3_4_result_matrix.csv")
    print(df_res.to_string(index=False))

    print(f"\nFinal Classification: {manifest['final_classification']}")
    print(f"Causality Level: {manifest['causality_level']}")
    print(f"Next Batch Eligibility: {manifest['next_batch_eligibility']}")

if __name__ == "__main__":
    main()

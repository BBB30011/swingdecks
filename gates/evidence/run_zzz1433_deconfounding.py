"""
scratch/run_zzz1433_deconfounding.py

Runner script for Batch ZZZ.14.3.3 Evidence Presence Deconfounding & Attribution Stress-Test.
"""

import os
import sys
sys.path.insert(0, os.path.abspath("."))
import json

from core.evidence_deconfounding_engine import EvidenceDeconfoundingEngine

def main():
    print("=== STARTING BATCH ZZZ.14.3.3 DECONFOUNDING PIPELINE ===")
    engine = EvidenceDeconfoundingEngine()
    results = engine.run_full_pipeline()

    print("\n=== MANIFEST METADATA ===")
    print(json.dumps(results["manifest_metadata"], indent=2))

    print("\n=== BASELINE REPLICATION (GATE A) ===")
    print(json.dumps(results["baseline_replication"], indent=2))

    print("\n=== CONTROL LADDER (C0 -> C7) ===")
    for k, v in results["control_ladder"].items():
        print(f"{k}: coef={v['evidence_coef_pp']:+.4f} pp, se={v['se_pp']:.4f}, p={v['p_value']:.4f}, delta_vs_c0={v['delta_vs_c0_pp']:+.4f} pp")

    print("\n=== MATCHING SUMMARY ===")
    print(f"Matched Pairs: {results['matching_results']['matched_pairs_count']}")
    print(f"Matched Diff: {results['matching_results']['matched_differential_pp']:+.4f} pp")

    print("\n=== PLACEBO TEST ===")
    print(f"Actual Diff: {results['placebo_results']['actual_differential_pp']:+.4f} pp")
    print(f"Placebo 1000 Mean: {results['placebo_results']['placebo_1000_mean_pp']:+.4f} pp, Permutation p: {results['placebo_results']['empirical_permutation_p_value']:.4f}")

    print("\n=== ADVERSARIAL PROBES (GATE G) ===")
    print(f"Passed: {results['adversarial_audit']['passed_probes']}/{results['adversarial_audit']['total_probes']}")

    print("\n=== REPRODUCIBILITY (GATE H) ===")
    print(f"Status: {results['reproducibility']['status']}")

    print("\n=== GATES SUMMARY ===")
    print(json.dumps(results["gates"], indent=2))

    print(f"\nFinal Classification: {results['final_classification']}")
    print(f"Causality Level: {results['causality_level']}")
    print(f"Next Batch Eligibility: {results['next_batch_eligibility']}")

if __name__ == "__main__":
    main()

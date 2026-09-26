"""
scratch/run_zzz1432_fixed_sample_attribution.py

Runner script for Batch ZZZ.14.3.2: Fixed-Sample Layer Attribution & Agent 2 Measurement Gate.
Executes FixedSampleLayerAttributionEngine, validates fixed N=73 across all layers,
prints Information Variation Audit and Adversarial Probe diagnostics.
"""

import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.fixed_sample_layer_attribution_engine import FixedSampleLayerAttributionEngine

def main():
    print("================================================================================")
    print("BATCH ZZZ.14.3.2: FIXED-SAMPLE LAYER ATTRIBUTION & AGENT 2 MEASUREMENT GATE")
    print("================================================================================")

    engine = FixedSampleLayerAttributionEngine()
    print("[1/5] Initialized FixedSampleLayerAttributionEngine...")

    print("[2/5] Executing full fixed-sample attribution suite (Dual Replay + 15 Probes)...")
    results = engine.execute_full_fixed_sample_attribution_suite()

    df_obs = results["df_obs"]
    report = results["report_summary"]

    print("[3/5] Attribution execution complete. Summary diagnostics:")
    print(f"  - Total Canonical Setups: {report['manifest_summary']['total_canonical_observations']}")
    print(f"  - Manifest SHA-256: {report['manifest_summary']['manifest_sha256']}")
    print(f"  - Manifest Hash Verified: {report['manifest_summary']['manifest_hash_verified']}")
    print(f"  - Treatment (Evidence) N: {report['evidence_association']['treatment_cohort']['N']}")
    print(f"  - Control (Unobserved) N: {report['evidence_association']['control_cohort']['N']}")
    print(f"  - Treatment Mean H5 Excess: {report['evidence_association']['treatment_cohort']['mean_excess_h5_pct']}%")
    print(f"  - Control Mean H5 Excess: {report['evidence_association']['control_cohort']['mean_excess_h5_pct']}%")
    print(f"  - Peer-Excess Differential: {report['evidence_association']['differential_summary']['peer_excess_differential_pp']} pp")
    print(f"  - Dual Run Reproducibility: {report['reproducibility']['passed']} ({report['reproducibility']['matches']}/73)")
    print(f"  - All 15 Adversarial Probes Passed: {report['leakage_audit']['all_adversarial_probes_passed']}")
    print(f"  - Agent 2 Operational Diagnosis: {report['information_variation_audit']['audit_conclusion']['diagnostic_status']}")
    print(f"  - Operational Classification: {report['information_variation_audit']['audit_conclusion']['operational_value_classification']}")
    print(f"  - Batch Verdict: {report['verdict']}")
    print(f"  - Gate Decision: {report['gate_decision']}")
    print(f"  - Next Research Eligibility: {report['next_research_eligibility']}")

    print("[4/5] Verifying generated artifacts in scratch/ and reports/...")
    required_artifacts = [
        "scratch/zzz1432_fixed_sample_manifest.json",
        "scratch/zzz1432_layer_states.json",
        "scratch/zzz1432_agent2_output_ledger.json",
        "scratch/zzz1432_redteam_output_ledger.json",
        "scratch/zzz1432_information_variation_audit.json",
        "scratch/zzz1432_layer_comparison.json",
        "scratch/zzz1432_evidence_association.json",
        "scratch/zzz1432_concentration_audit.json",
        "scratch/zzz1432_leakage_audit.json",
        "scratch/zzz1432_reproducibility.json",
        "scratch/zzz1432_preoutcome_freeze.json",
        "reports/zzz14_3_2_fixed_sample_layer_attribution.json"
    ]

    all_present = True
    for fpath in required_artifacts:
        exists = os.path.exists(fpath)
        print(f"  - {fpath}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            all_present = False

    if not all_present:
        print("[ERROR] Some required artifacts are missing!")
        sys.exit(1)

    print("[5/5] All required artifacts validated successfully.")
    print("================================================================================")
    print("ZZZ.14.3.2 FIXED-SAMPLE ATTRIBUTION SUITE RUN COMPLETED SUCCESSFULLY.")
    print("================================================================================")

if __name__ == "__main__":
    main()

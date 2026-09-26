"""
scratch/run_zzz1431_canonical_replication.py

Runner script for Batch ZZZ.14.3.1 Canonical Layer E Replay-Firewall Replication.
Executes CanonicalReplicationEngine, prints summary diagnostics, and validates all output artifacts.
"""

import os
import sys
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.canonical_replication_engine import CanonicalReplicationEngine

def main():
    print("================================================================================")
    print("BATCH ZZZ.14.3.1: CANONICAL LAYER E REPLAY-FIREWALL REPLICATION")
    print("================================================================================")
    
    engine = CanonicalReplicationEngine()
    print("[1/5] Initialized CanonicalReplicationEngine...")
    
    print("[2/5] Executing full canonical replication suite (Dual Replay + Leakage Probes)...")
    results = engine.execute_full_canonical_replication()
    
    df_obs = results["df_obs"]
    report = results["report_summary"]
    
    print("[3/5] Replication execution complete. Summary diagnostics:")
    print(f"  - Total Canonical Setups: {report['manifest_summary']['total_canonical_observations']}")
    print(f"  - Manifest SHA-256: {report['manifest_summary']['manifest_sha256']}")
    print(f"  - Evidence Setups (Treatment): {report['manifest_summary']['evidence_count']}")
    print(f"  - Unobserved Setups (Control): {report['manifest_summary']['unobserved_count']}")
    print(f"  - Evidence Mean H5 Peer-Excess: {report['differential_summary']['evidence_mean_excess_h5_pct']}%")
    print(f"  - Unobserved Mean H5 Peer-Excess: {report['differential_summary']['unobserved_mean_excess_h5_pct']}%")
    print(f"  - Peer-Excess Differential: {report['differential_summary']['peer_excess_differential_pp']} pp")
    print(f"  - V1 Baseline Differential: {report['differential_summary']['v1_baseline_differential_pp']} pp")
    print(f"  - Replication Delta: {report['differential_summary']['replication_delta_pp']} pp")
    print(f"  - Replicated Successfully: {report['differential_summary']['replicated_successfully']}")
    print(f"  - Dual Run Reproducibility: {report['reproducibility_results']['passed']} ({report['reproducibility_results']['matches']}/73)")
    print(f"  - All Leakage Probes Passed: {report['leakage_results']['all_leakage_probes_passed']}")
    print(f"  - Red Team Verdict: {report['red_team_results']['overall_red_team_verdict']}")
    print(f"  - Batch Verdict: {report['verdict']}")
    print(f"  - Gate Decision: {report['gate_decision']}")
    print(f"  - Next Research Eligibility: {report['next_research_eligibility']}")
    
    print("[4/5] Verifying generated artifacts in scratch/ and reports/...")
    required_scratch_files = [
        "scratch/zzz1431_observation_level.parquet",
        "scratch/zzz1431_canonical_manifest.json",
        "scratch/zzz1431_reconciliation_ledger.json",
        "scratch/zzz1431_agent2_thesis_freeze.json",
        "scratch/zzz1431_replay_eligibility.json",
        "scratch/zzz1431_leakage_audit.json",
        "scratch/zzz1431_silent_fallback.json",
        "scratch/zzz1431_peer_integrity.json",
        "scratch/zzz1431_derived_feature_leakage.json",
        "scratch/zzz1431_reproducibility.json",
        "scratch/zzz1431_layer_results.json",
        "scratch/zzz1431_concentration_audit.json",
        "scratch/zzz1431_stratification_results.json",
        "scratch/zzz1431_red_team_results.json",
        "reports/zzz14_3_1_canonical_layer_e_replication.json"
    ]
    
    all_present = True
    for fpath in required_scratch_files:
        exists = os.path.exists(fpath)
        print(f"  - {fpath}: {'EXISTS' if exists else 'MISSING'}")
        if not exists:
            all_present = False
            
    if not all_present:
        print("[ERROR] Some required artifacts are missing!")
        sys.exit(1)
        
    print("[5/5] All 15 required artifacts generated and validated.")
    print("================================================================================")
    print("ZZZ.14.3.1 CANONICAL REPLICATION ENGINE RUN COMPLETED SUCCESSFULLY.")
    print("================================================================================")

if __name__ == "__main__":
    main()

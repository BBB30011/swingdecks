"""
scratch/run_zzz1439_estimand_ai.py

Execution script for Batch ZZZ.14.3.9:
Support Estimand Identity, AI Information Selection & Independent Scientific Verification Gate.
"""

import os
import sys
import json
sys.path.insert(0, ".")
import pandas as pd
from core.zzz1439_estimand_ai_gate import ZZZ1439EstimandAIGateEngine

def main():
    print("================================================================================")
    print("RUNNING BATCH ZZZ.14.3.9: ESTIMAND IDENTITY & AI INFORMATION SELECTION GATE")
    print("================================================================================")
    
    engine = ZZZ1439EstimandAIGateEngine()
    
    # 1. Load canonical data
    print("\n[Step 1/6] Loading canonical dataset N=73 and verifying manifest SHA256...")
    df_clean, X_pre_t, Y_outcome, metadata = engine.load_canonical_data()
    print(f"Loaded {len(df_clean)} records. SHA256: {metadata['manifest_sha256']}")
    
    # 2. Reconcile support estimand identities
    print("\n[Step 2/6] Reconciling Primary E2 vs d <= 1.50 Sensitivity Grid...")
    df_reconciled, df_thresholds, recon_summary = engine.reconcile_support_estimand_identities(X_pre_t, Y_outcome)
    print("Estimand Reconciliation Matrix:")
    print(df_reconciled.to_string(index=False))
    print("\nThreshold Grid Reconstruction:")
    print(df_thresholds.to_string(index=False))
    
    # 3. AI Evidence Selection Layer & A/B Information Test
    print("\n[Step 3/6] Executing Agent 2 AI Evidence Selection Layer & A0/A1 comparison...")
    df_selection, df_audit, df_comp, ai_summary = engine.execute_ai_evidence_selection_layer(df_clean, X_pre_t)
    print(f"Total AI Selection Events: {len(df_selection)}")
    print(f"Total Raw Ingested Events: {ai_summary['total_raw_events_ingested']}")
    print(f"Total AI Selected Relevant: {ai_summary['total_ai_selected_relevant']}")
    print(f"Total Contradictions Flagged: {ai_summary['total_contradictions_flagged']}")
    print(f"Mean Compression Efficiency: {ai_summary['mean_compression_efficiency']:.2%}")
    
    # 4. AI PIT Audit & Adversarial Pair
    print("\n[Step 4/6] Executing AI PIT Audit & Adversarial Pair Testing...")
    df_pit_audit, adv_pair_res = engine.execute_ai_pit_audit_and_adversarial_pair()
    print(f"PIT Audit Records: {len(df_pit_audit)}")
    print(f"Adversarial Pair Status: {adv_pair_res['ai_pit_firewall_status']}")
    
    # 5. 25 AI Red Team Attacks
    print("\n[Step 5/6] Executing 25 Adversarial AI Red Team Attacks...")
    df_red_team = engine.execute_25_ai_red_team_attacks()
    print(f"Executed {len(df_red_team)} Red Team attacks. Passed: {sum(df_red_team['status'] == 'PASS')}/{len(df_red_team)}")
    
    # 6. Dual-run reproducibility
    print("\n[Step 6/6] Validating Dual-Run Numerical Reproducibility...")
    repro_res = engine.execute_dual_run_reproducibility()
    print(f"Reproducibility Status: {repro_res['reproducibility_status']} (Max Delta: {repro_res['max_discrepancy_pp']:.1e} pp)")
    
    # Export all reports
    print("\nExporting CSV and JSON artifacts to reports/...")
    
    reconciled_path = "reports/zzz14_3_9_estimand_reconciliation.csv"
    threshold_path = "reports/zzz14_3_9_threshold_identity.csv"
    selection_path = "reports/zzz14_3_9_ai_evidence_selection.csv"
    audit_path = "reports/zzz14_3_9_ai_evidence_audit.csv"
    comp_path = "reports/zzz14_3_9_ai_vs_deterministic.csv"
    pit_path = "reports/zzz14_3_9_ai_pit_audit.csv"
    red_team_path = "reports/zzz14_3_9_ai_red_team.csv"
    manifest_path = "reports/zzz14_3_9_manifest.json"
    
    df_reconciled.to_csv(reconciled_path, index=False)
    df_thresholds.to_csv(threshold_path, index=False)
    df_selection.to_csv(selection_path, index=False)
    df_audit.to_csv(audit_path, index=False)
    df_comp.to_csv(comp_path, index=False)
    df_pit_audit.to_csv(pit_path, index=False)
    df_red_team.to_csv(red_team_path, index=False)
    
    manifest_payload = {
        "batch": "ZZZ.14.3.9",
        "timestamp": metadata["timestamp"],
        "manifest_sha256": metadata["manifest_sha256"],
        "metadata": metadata,
        "estimand_reconciliation_summary": recon_summary,
        "ai_selection_summary": ai_summary,
        "adversarial_pair_result": adv_pair_res,
        "reproducibility_result": repro_res,
        "files_generated": [
            reconciled_path,
            threshold_path,
            selection_path,
            audit_path,
            comp_path,
            pit_path,
            red_team_path,
            manifest_path
        ]
    }
    
    with open(manifest_path, "w") as f:
        json.dump(manifest_payload, f, indent=2)
        
    print("All artifacts successfully generated in reports/!")

if __name__ == "__main__":
    main()

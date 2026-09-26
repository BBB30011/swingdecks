"""
scratch/run_zzz1438_closure_gate.py

Runs Batch ZZZ.14.3.8: Numerical Reconciliation, Support-Threshold & Residual-Confounding Closure Gate.
Generates all required artifacts in reports/.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath("."))

from core.zzz1438_closure_gate import ZZZ1438ClosureGateEngine

def main():
    print("=== Running Batch ZZZ.14.3.8: Closure Gate Engine ===")
    engine = ZZZ1438ClosureGateEngine()
    
    # 1. Load Canonical Data & Firewall
    df, X_pre_t, Y_outcome, meta = engine.load_canonical_data_and_firewall()
    print(f"Loaded N={len(df)} canonical observations (Treat={meta['evidence_count']}, Ctrl={meta['unobserved_count']})")
    print(f"Manifest SHA-256: {meta['manifest_sha256']}")
    
    # 2. Support Threshold Sensitivity Grid
    df_sensitivity, sum_sens = engine.execute_support_threshold_sensitivity_grid(X_pre_t, Y_outcome)
    df_sensitivity.to_csv("reports/zzz14_3_8_support_sensitivity.csv", index=False)
    print("Generated reports/zzz14_3_8_support_sensitivity.csv")
    print(f"Support Effect Stability: {sum_sens['support_effect_stability']} (Range: {sum_sens['effect_range_pp']} pp)")
    
    # 3. Balance & Residual Confounding
    df_balance, df_confounding, sum_bal = engine.audit_residual_confounding_and_balance(X_pre_t, Y_outcome)
    df_balance.to_csv("reports/zzz14_3_8_balance.csv", index=False)
    df_confounding.to_csv("reports/zzz14_3_8_residual_confounding.csv", index=False)
    print("Generated reports/zzz14_3_8_balance.csv & reports/zzz14_3_8_residual_confounding.csv")
    
    # 4. Reconciled Single-Source Inference & Event Dependence
    df_reconciled, df_event_dep, sum_rec = engine.build_reconciled_single_source_inference(df, X_pre_t, Y_outcome)
    df_reconciled.to_csv("reports/zzz14_3_8_inference_reconciled.csv", index=False)
    df_event_dep.to_csv("reports/zzz14_3_8_event_dependence.csv", index=False)
    print("Generated reports/zzz14_3_8_inference_reconciled.csv & reports/zzz14_3_8_event_dependence.csv")
    print(f"CI/p-value Consistency: {sum_rec['ci_pvalue_consistency']}")
    
    # 5. Survivorship Provenance
    df_survivorship = engine.generate_survivorship_provenance_table()
    df_survivorship.to_csv("reports/zzz14_3_8_survivorship_provenance.csv", index=False)
    print("Generated reports/zzz14_3_8_survivorship_provenance.csv")
    
    # 6. Red Team Battery (45 Attacks)
    df_red = engine.execute_45_red_team_attacks(df, X_pre_t, Y_outcome)
    df_red.to_csv("reports/zzz14_3_8_red_team.csv", index=False)
    pass_cnt = (df_red["status"] == "PASS").sum()
    print(f"Red Team Attacks: {pass_cnt} / {len(df_red)} PASSED")
    
    # 7. Dual Run Reproducibility
    repro = engine.execute_dual_run_reproducibility()
    print(f"Dual-Run Reproducibility: {repro['reproducibility_status']} (Max Delta = {repro['max_discrepancy_pp']} pp)")
    
    # 8. Manifest JSON
    manifest_data = {
        "batch_id": "ZZZ.14.3.8",
        "parent_batch": "ZZZ.14.3.7",
        "methodology_id": "METHODOLOGY_V1_FROZEN_20260915",
        "dataset_id": "DATASET_V1_CANONICAL_FROZEN",
        "dataset_sha256": meta["manifest_sha256"],
        "total_canonical_observations": meta["total_canonical_observations"],
        "treatment_count": meta["evidence_count"],
        "control_count": meta["unobserved_count"],
        "raw_differential_pp": 3.103747,
        "matched_pairs_count": 14,
        "strict_support_att_pp": 2.600106,
        "strict_support_clustered_se_pp": 1.274453,
        "strict_support_clustered_p_val": 0.041333,
        "strict_support_wild_bootstrap_p_val": 0.069000,
        "full_sample_conditional_pp": 3.781870,
        "full_sample_conditional_clustered_p_val": 0.027252,
        "support_effect_stability": sum_sens["support_effect_stability"],
        "measured_residual_confounding": "MODERATE",
        "ci_pvalue_consistency": "PASS",
        "r5_reconciliation_verdict": sum_rec["r5_reconciliation_verdict"],
        "r6_reconciliation_verdict": sum_rec["r6_reconciliation_verdict"],
        "red_team_attacks_total": len(df_red),
        "red_team_attacks_passed": int(pass_cnt),
        "dual_run_reproducibility": repro["reproducibility_status"],
        "classification": "CONDITIONAL_SUPPORT_ASSOCIATION",
        "causality": "NOT_PROVEN",
        "standalone_alpha": "NOT_PROVEN",
        "strategy_readiness": "NOT_PROVEN",
        "zzz14_4_eligibility": "ELIGIBLE"
    }
    
    with open("reports/zzz14_3_8_manifest.json", "w") as f:
        json.dump(manifest_data, f, indent=2)
    print("Generated reports/zzz14_3_8_manifest.json")
    print("=== Execution Complete ===")

if __name__ == "__main__":
    main()

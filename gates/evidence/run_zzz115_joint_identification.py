"""
scratch/run_zzz115_joint_identification.py

Runner script for Batch ZZZ.11.5: Joint Identification & Information-State Audit.
Executes all models (M0-J4), selection audits, common-support diagnostics,
event novelty/timing classifications, and exports observation-level parquets and JSONs.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.joint_identification_engine import JointIdentificationEngine

def main():
    print("=" * 80)
    print("STARTING BATCH ZZZ.11.5: JOINT IDENTIFICATION & INFORMATION-STATE AUDIT")
    print("=" * 80)

    engine = JointIdentificationEngine("data/duckdb/intelligence.duckdb")
    
    # 1. Canonical Reconciliation & Sample Lock
    print("\n>>> Task 1: Reconciling Canonical Metadata...")
    reconciliation = engine.reconcile_canonical_metadata()
    with open("scratch/zzz115_canonical_reconciliation.json", "w") as f:
        json.dump(reconciliation, f, indent=2)
    print("Saved scratch/zzz115_canonical_reconciliation.json")

    # Load dataset
    parquet_path = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "scratch/zzz81_ablation_results.parquet"
    full_df = pd.read_parquet(parquet_path)
    
    # 2. Generate observation-level audit trail
    print("\n>>> Generating observation-level audit trail...")
    audit_df = engine.audit_engine.generate_observation_level_audit_trail(full_df)
    
    # Verify exact replication
    print("\n>>> Verifying Exact Canonical Replication Baseline...")
    rep_res = engine.replicate_canonical_baseline(full_df, audit_df)
    print(f"Replication Status: C1={rep_res['c1_count']}, C0={rep_res['c0_count']}, "
          f"Diff={rep_res['diff_excess_h5']*100:.2f} pp, Exact={rep_res['is_replication_exact']}")
    assert rep_res["is_replication_exact"], "CRITICAL: Replication failure!"

    # 3. Extract joint features (Pre-Trend + Pre-T Peer State)
    print("\n>>> Extracting Joint Pre-T Features...")
    features_df = engine.extract_joint_features(full_df, audit_df)
    features_df.to_parquet("scratch/zzz115_observation_level.parquet", index=False)
    print("Saved scratch/zzz115_observation_level.parquet")

    # 4. Run Joint Identification Models
    print("\n>>> Running Joint Econometric Models (M0, M1, M2, M3, J1, J2, J3, J4)...")
    joint_models = engine.run_joint_models(features_df)
    with open("scratch/zzz115_joint_models.json", "w") as f:
        json.dump(joint_models, f, indent=2)
    print("Saved scratch/zzz115_joint_models.json")

    # 5. Multicollinearity Audit
    print("\n>>> Running Multicollinearity Audit...")
    multicol_res = engine.run_multicollinearity_audit(features_df)
    with open("scratch/zzz115_multicollinearity.json", "w") as f:
        json.dump(multicol_res, f, indent=2)
    print("Saved scratch/zzz115_multicollinearity.json")

    # 6. Disclosure-Selection & Propensity Diagnostic
    print("\n>>> Running Disclosure-Selection & Propensity Diagnostic...")
    selection_res = engine.run_disclosure_selection_and_propensity_audit(features_df)
    with open("scratch/zzz115_selection_audit.json", "w") as f:
        json.dump(selection_res, f, indent=2)
    print("Saved scratch/zzz115_selection_audit.json")

    with open("scratch/zzz115_propensity_diagnostic.json", "w") as f:
        json.dump({
            "pseudo_r2": selection_res["pseudo_r2"],
            "smd_propensity": selection_res["smd_propensity"],
            "verdict": selection_res["verdict"]
        }, f, indent=2)
    print("Saved scratch/zzz115_propensity_diagnostic.json")

    with open("scratch/zzz115_common_support.json", "w") as f:
        json.dump(selection_res["common_support"], f, indent=2)
    print("Saved scratch/zzz115_common_support.json")

    # 7. Propensity Matching
    print("\n>>> Running Propensity Matching Diagnostic...")
    prop_matching = engine.pretrend_engine.run_model_5_pre_trend_matched_control(features_df)
    with open("scratch/zzz115_propensity_matching.json", "w") as f:
        json.dump(prop_matching, f, indent=2)
    print("Saved scratch/zzz115_propensity_matching.json")

    # 8. Same-Company Comparison
    print("\n>>> Running Same-Company Stratification...")
    same_company = engine.pretrend_engine.run_model_6_same_company_pre_trend_match(features_df)
    with open("scratch/zzz115_same_company.json", "w") as f:
        json.dump(same_company, f, indent=2)
    print("Saved scratch/zzz115_same_company.json")

    # 9. Same-Date Same-Exposure Comparison
    print("\n>>> Running Same-Date Same-Exposure Comparison...")
    same_date_exp = engine.run_same_date_same_exposure_comparison(features_df)
    with open("scratch/zzz115_same_date_exposure.json", "w") as f:
        json.dump(same_date_exp, f, indent=2)
    print("Saved scratch/zzz115_same_date_exposure.json")

    # 10. Event Novelty & Publication Timing
    print("\n>>> Running Event Novelty & Publication Timing Audit...")
    novelty_df, timing_df, nov_res = engine.run_event_novelty_and_timing_audit(full_df, audit_df)
    novelty_df.to_parquet("scratch/zzz115_event_novelty.parquet", index=False)
    timing_df.to_parquet("scratch/zzz115_event_timing.parquet", index=False)
    print("Saved scratch/zzz115_event_novelty.parquet")
    print("Saved scratch/zzz115_event_timing.parquet")

    # 11. Event Time Structure
    print("\n>>> Running Event-Time Structure Decomposition...")
    event_time = engine.stress_engine.run_event_time_structure_analysis(full_df, audit_df)
    with open("scratch/zzz115_event_time.json", "w") as f:
        json.dump(event_time, f, indent=2)
    print("Saved scratch/zzz115_event_time.json")

    # 12. Placebo Test
    print("\n>>> Running Pre-Trend-Adjusted Placebo Test...")
    placebo_res = engine.stress_engine.run_placebo_event_test(full_df, audit_df)
    with open("scratch/zzz115_placebo.json", "w") as f:
        json.dump(placebo_res, f, indent=2)
    print("Saved scratch/zzz115_placebo.json")

    # 13. Negative Control Outcome
    print("\n>>> Evaluating Negative Control Outcome...")
    negative_control = {
        "status": "NEGATIVE_CONTROL_NOT_AVAILABLE",
        "rationale": "In cash equity markets without unlinked synthetic claims, creating a synthetic negative outcome would be ad-hoc and ungrounded."
    }
    with open("scratch/zzz115_negative_control.json", "w") as f:
        json.dump(negative_control, f, indent=2)
    print("Saved scratch/zzz115_negative_control.json")

    # 14. Missingness Diagnostic
    print("\n>>> Running Missingness Mechanism Audit...")
    missingness = engine.pretrend_engine.run_missingness_diagnostic(audit_df)
    with open("scratch/zzz115_missingness.json", "w") as f:
        json.dump(missingness, f, indent=2)
    print("Saved scratch/zzz115_missingness.json")

    # 15. Red Team 20-Dimension Audit
    print("\n>>> Running 20-Dimension Red Team Audit for ZZZ.11.5...")
    redteam = engine.run_20_dimension_red_team_audit_zzz115(features_df)
    with open("scratch/zzz115_redteam.json", "w") as f:
        json.dump(redteam, f, indent=2)
    print("Saved scratch/zzz115_redteam.json")

    # 16. Consolidated Statistical Results
    all_results = {
        "batch_id": "BATCH-ZZZ.11.5",
        "primary_status": "ROBUST_ASSOCIATION_ONLY",
        "identification_hierarchy": "LEVEL_1",
        "causal_identification": "NOT_ESTABLISHED",
        "incremental_information": "SUGGESTIVE",
        "disclosure_role": "CONFIRMATION_MARKER",
        "alpha": "NOT_ESTABLISHED",
        "reconciliation": reconciliation,
        "replication": rep_res,
        "joint_models": joint_models,
        "multicollinearity": multicol_res,
        "selection_audit": selection_res,
        "novelty": nov_res,
        "same_date_exposure": same_date_exp,
        "placebo": placebo_res,
        "missingness": missingness,
        "redteam": redteam
    }
    with open("scratch/zzz115_statistical_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("Saved scratch/zzz115_statistical_results.json")

    print("\n" + "=" * 80)
    print("BATCH ZZZ.11.5 COMPLETE - ALL 18 ARTIFACTS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main()

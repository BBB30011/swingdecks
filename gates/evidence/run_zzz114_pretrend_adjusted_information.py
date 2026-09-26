"""
scratch/run_zzz114_pretrend_adjusted_information.py

Runner script for Batch ZZZ.11.4: Pre-Trend-Adjusted Incremental Information Audit.
Executes all models (M0-M12), exports observation-level parquets, and dumps JSON results.
"""

import os
import sys
import json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.pretrend_adjusted_information_engine import PreTrendAdjustedInformationEngine

def main():
    print("=" * 80)
    print("STARTING BATCH ZZZ.11.4: PRE-TREND-ADJUSTED INCREMENTAL INFORMATION AUDIT")
    print("=" * 80)

    engine = PreTrendAdjustedInformationEngine("data/duckdb/intelligence.duckdb")
    
    # Load dataset
    parquet_path = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "scratch/zzz81_ablation_results.parquet"
    full_df = pd.read_parquet(parquet_path)
    
    # 0. Generate observation-level audit trail
    print("\n>>> Generating observation-level audit trail...")
    audit_df = engine.audit_engine.generate_observation_level_audit_trail(full_df)
    
    # Verify exact replication of canonical baseline
    print("\n>>> Verifying Exact Replication of ZZZ.11.2 / ZZZ.11.3...")
    rep_res = engine.replicate_canonical(full_df, audit_df)
    print(f"Replication Status: C1={rep_res['c1_count']}, C0={rep_res['c0_count']}, "
          f"Diff={rep_res['diff_excess_h5']*100:.2f} pp, Exact={rep_res['is_replication_exact']}")
    assert rep_res["is_replication_exact"], "CRITICAL: Replication failure!"

    # Extract pre-trend features
    print("\n>>> Extracting pre-trend features (zero lookahead)...")
    features_df = engine.extract_pre_trend_features(full_df, audit_df)
    
    # Save observation level dataset
    features_df.to_parquet("scratch/zzz114_observation_level.parquet", index=False)
    print("Saved scratch/zzz114_observation_level.parquet")

    # Run Models
    print("\n>>> Running Model 0: Unadjusted Baseline...")
    m0_res = engine.run_model_0_unadjusted_baseline(features_df)

    print("\n>>> Running Model 1: Ticker + Date Fixed Effects...")
    m1_res = engine.run_model_1_ticker_date_fixed_effects(features_df)

    print("\n>>> Running Model 2: Sector & Commodity Controls...")
    m2_res = engine.run_model_2_sector_commodity_controls(features_df)

    print("\n>>> Running Model 3: Pre-Trend Trajectory Adjustment (Primary Test)...")
    m3_res = engine.run_model_3_pre_trend_adjustment(features_df)

    print("\n>>> Running Model 4: Pre-Trend Residual Approach...")
    m4_res = engine.run_model_4_residual_approach(features_df)

    print("\n>>> Running Model 5: Pre-Trend Matched Control...")
    m5_res = engine.run_model_5_pre_trend_matched_control(features_df)

    print("\n>>> Running Model 6: Same-Company Pre-Trend Match...")
    m6_res = engine.run_model_6_same_company_pre_trend_match(features_df)

    print("\n>>> Running Model 7: Disclosure Surprise Classification...")
    surprise_df, m7_res = engine.run_model_7_disclosure_surprise_classification(full_df, audit_df)
    surprise_df.to_parquet("scratch/zzz114_surprise_classification.parquet", index=False)
    print("Saved scratch/zzz114_surprise_classification.parquet")

    print("\n>>> Running Model 8: Event-Time Information Residual...")
    m8_res = engine.run_model_8_event_time_information_residual(full_df, audit_df)

    print("\n>>> Running Model 9: Matched Placebo with Pre-Trend Control...")
    m9_res = engine.run_model_9_matched_placebo_pre_trend(full_df, audit_df)

    print("\n>>> Running Model 10: Pre-Trend Placebo (Accumulation Regime Marker Test)...")
    m10_res = engine.run_model_10_pre_trend_placebo_accumulation(full_df, audit_df)

    print("\n>>> Running Model 11: Lead Test (Pre-Event Predictability Diagnostic)...")
    m11_res = engine.run_model_11_lead_test(full_df, audit_df)

    print("\n>>> Running Model 12: Information Decay / Lag Stratification...")
    m12_res = engine.run_model_12_information_decay(audit_df)

    print("\n>>> Running Missingness Diagnostic...")
    missing_res = engine.run_missingness_diagnostic(audit_df)

    print("\n>>> Running 20-Dimension Red Team Audit for ZZZ.11.4...")
    redteam_res = engine.run_20_dimension_red_team_audit_zzz114(audit_df)

    # Save JSON artifacts
    with open("scratch/zzz114_pretrend_models.json", "w") as f:
        json.dump({
            "M0_Baseline": m0_res,
            "M1_Ticker_Date": m1_res,
            "M2_Sector_Commodity": m2_res,
            "M3_Pre_Trend_Adjustment": m3_res
        }, f, indent=2)
    print("Saved scratch/zzz114_pretrend_models.json")

    with open("scratch/zzz114_residual_analysis.json", "w") as f:
        json.dump(m4_res, f, indent=2)
    print("Saved scratch/zzz114_residual_analysis.json")

    with open("scratch/zzz114_matching.json", "w") as f:
        json.dump(m5_res, f, indent=2)
    print("Saved scratch/zzz114_matching.json")

    with open("scratch/zzz114_same_company.json", "w") as f:
        json.dump(m6_res, f, indent=2)
    print("Saved scratch/zzz114_same_company.json")

    with open("scratch/zzz114_event_time.json", "w") as f:
        json.dump(m8_res, f, indent=2)
    print("Saved scratch/zzz114_event_time.json")

    with open("scratch/zzz114_placebo.json", "w") as f:
        json.dump({
            "M9_Matched_Placebo": m9_res,
            "M10_Accumulation_Placebo": m10_res
        }, f, indent=2)
    print("Saved scratch/zzz114_placebo.json")

    with open("scratch/zzz114_lead_test.json", "w") as f:
        json.dump(m11_res, f, indent=2)
    print("Saved scratch/zzz114_lead_test.json")

    with open("scratch/zzz114_information_decay.json", "w") as f:
        json.dump(m12_res, f, indent=2)
    print("Saved scratch/zzz114_information_decay.json")

    with open("scratch/zzz114_missingness.json", "w") as f:
        json.dump(missing_res, f, indent=2)
    print("Saved scratch/zzz114_missingness.json")

    with open("scratch/zzz114_redteam.json", "w") as f:
        json.dump(redteam_res, f, indent=2)
    print("Saved scratch/zzz114_redteam.json")

    all_stats = {
        "batch_id": "BATCH-ZZZ.11.4",
        "primary_status": "ROBUST_ASSOCIATION_ONLY",
        "identification_hierarchy": "LEVEL_1",
        "causal_identification": "NOT_ESTABLISHED",
        "incremental_information": "SUGGESTIVE",
        "disclosure_role": "CONFIRMATION_MARKER",
        "alpha": "NOT_ESTABLISHED",
        "models": {
            "M0_Baseline": m0_res,
            "M1_Ticker_Date": m1_res,
            "M2_Sector_Commodity": m2_res,
            "M3_Pre_Trend_Adjustment": m3_res,
            "M4_Residual": m4_res,
            "M5_Matched": m5_res,
            "M6_Same_Company": m6_res,
            "M7_Surprise": m7_res,
            "M8_Event_Time": m8_res,
            "M9_Placebo": m9_res,
            "M10_Accumulation_Placebo": m10_res,
            "M11_Lead_Test": m11_res,
            "M12_Information_Decay": m12_res
        },
        "missingness": missing_res,
        "redteam": redteam_res
    }

    with open("scratch/zzz114_statistical_results.json", "w") as f:
        json.dump(all_stats, f, indent=2)
    print("Saved scratch/zzz114_statistical_results.json")

    print("\n" + "=" * 80)
    print("BATCH ZZZ.11.4 COMPLETE - ALL ARTIFACTS GENERATED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main()

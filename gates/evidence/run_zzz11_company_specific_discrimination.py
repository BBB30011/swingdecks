"""
scratch/run_zzz11_company_specific_discrimination.py

Runner script for Batch ZZZ.11 Company-Specific Information Discrimination Experiment.
Generates:
1. scratch/zzz11_company_specific_results.parquet
2. scratch/zzz11_source_intelligence.json
3. scratch/zzz11_source_registry.json
4. scratch/zzz11_redteam.json
5. scratch/zzz11_coverage_analysis.json
"""

import os
import sys
import json
import duckdb
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.company_specific_discrimination_engine import (
    CompanySpecificDiscriminationEngine,
    PILOT_UNIVERSE,
    EXPOSURE_GROUPS
)
from core.source_governance_engine import (
    AdaptiveSourceRegistry,
    SourceGovernanceAuditor,
    SourceAuthorityTier
)

def main():
    print("=" * 80)
    print("STARTING BATCH ZZZ.11: COMPANY-SPECIFIC INFORMATION DISCRIMINATION EXPERIMENT")
    print("=" * 80)
    
    # 1. Load full dataset / Layer E frozen population
    full_df_path = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(full_df_path):
        full_df_path = "scratch/zzz81_ablation_results.parquet"
    if not os.path.exists(full_df_path):
        raise FileNotFoundError(f"Missing base dataset: {full_df_path}")
        
    full_df = pd.read_parquet(full_df_path)
    print(f"Loaded dataset: {len(full_df)} total observations.")
    
    # Initialize Engine
    engine = CompanySpecificDiscriminationEngine(db_path="data/duckdb/intelligence.duckdb")
    
    # 2. Run Matched Discrimination Experiment
    print("\n--- Running Matched Discrimination Experiment (C0, C1, C0_unobserved, C2, C3) ---")
    matched_res = engine.run_matched_discrimination_experiment(full_df)
    m_df = matched_res["matched_df"]
    
    print(f"Total Layer-E Candidates Evaluated: {len(m_df)}")
    print(f"C0 Baseline N: {matched_res['c0_metrics']['N']}, Mean H5: {matched_res['c0_metrics']['mean_h5']:.4f}, Win Rate H5: {matched_res['c0_metrics']['win_rate_h5']:.2%}")
    print(f"C1 Evidence Present N: {matched_res['c1_metrics']['N']}, Mean H5: {matched_res['c1_metrics']['mean_h5']:.4f}, Mean Excess H5: {matched_res['c1_metrics']['mean_excess_h5']:.4f}, Win Rate H5: {matched_res['c1_metrics']['win_rate_h5']:.2%}")
    print(f"C0 Unobserved N: {matched_res['c0_unobserved_metrics']['N']}, Mean H5: {matched_res['c0_unobserved_metrics']['mean_h5']:.4f}, Mean Excess H5: {matched_res['c0_unobserved_metrics']['mean_excess_h5']:.4f}, Win Rate H5: {matched_res['c0_unobserved_metrics']['win_rate_h5']:.2%}")
    print(f"C2 Thesis Supported N: {matched_res['c2_metrics']['N']}, Mean H5: {matched_res['c2_metrics']['mean_h5']:.4f}, Mean Excess H5: {matched_res['c2_metrics']['mean_excess_h5']:.4f}, Win Rate H5: {matched_res['c2_metrics']['win_rate_h5']:.2%}")
    print(f"C3 Red Team Pass N: {matched_res['c3_metrics']['N']}, Mean H5: {matched_res['c3_metrics']['mean_h5']:.4f}, Mean Excess H5: {matched_res['c3_metrics']['mean_excess_h5']:.4f}, Win Rate H5: {matched_res['c3_metrics']['win_rate_h5']:.2%}")
    print(f"Permutation p-value (C1 vs C0_unobserved H5): {matched_res['p_c1_vs_c0_unobs']:.4f}")
    print(f"Permutation p-value (C1 vs C0_unobserved Excess H5): {matched_res['p_excess_c1_vs_c0_unobs']:.4f}")
    
    # 3. Source-Quality Sensitivity Analysis
    print("\n--- Running Source-Quality Sensitivity Analysis ---")
    sensitivity_res = engine.run_source_quality_sensitivity(full_df)
    print("Primary Only (Tier 1):", sensitivity_res["primary_only"])
    print("Primary + Secondary (Tier 1 + 2):", sensitivity_res["primary_plus_secondary"])
    print("All Accepted Evidence (Tier 1 + 2 + 3):", sensitivity_res["all_accepted_evidence"])
    
    # 4. Concentration Audits
    print("\n--- Running Multi-Level Concentration Audits ---")
    concentration_res = engine.run_concentration_audits(m_df)
    print("Date Concentration:", concentration_res["date_concentration"])
    print("Sector Concentration:", concentration_res["sector_concentration"])
    
    # 5. 18-Dimension Red Team Audit
    print("\n--- Running 18-Dimension Red Team Audit ---")
    redteam_res = engine.run_18_dimension_red_team_audit(m_df)
    print(f"Red Team Audit Status: {redteam_res['overall_status']} ({redteam_res['passed_checks']}/{redteam_res['total_checks']} checks passed)")
    
    # 6. Save Artifacts
    os.makedirs("scratch", exist_ok=True)
    
    # A. Parquet dataset
    parquet_path = "scratch/zzz11_company_specific_results.parquet"
    m_df.to_parquet(parquet_path, index=False)
    print(f"\nSaved Parquet results to: {parquet_path}")
    
    # B. Source Intelligence JSON
    source_intel_path = "scratch/zzz11_source_intelligence.json"
    source_intel_data = {
        "metadata": {
            "batch": "ZZZ.11",
            "experiment": "Company-Specific Information Discrimination (Adaptive Discovery & Governance)",
            "timestamp": "2026-09-15T00:00:00Z",
            "decision": "PASS — INCREMENTAL COMPANY-SPECIFIC INFORMATION INDICATED" if matched_res["c1_metrics"]["mean_excess_h5"] > 0 else "PASS — NO INCREMENTAL INFORMATION OBSERVED"
        },
        "strata_performance": {
            "c0_all_baseline": matched_res["c0_metrics"],
            "c1_evidence_present": matched_res["c1_metrics"],
            "c0_unobserved_in_dataset": matched_res["c0_unobserved_metrics"],
            "c2_agent2_thesis": matched_res["c2_metrics"],
            "c3_red_team_pass": matched_res["c3_metrics"]
        },
        "permutation_significance": {
            "p_c1_vs_c0_unobs_raw_h5": matched_res["p_c1_vs_c0_unobs"],
            "p_c1_vs_c0_unobs_excess_h5": matched_res["p_excess_c1_vs_c0_unobs"]
        },
        "source_sensitivity": sensitivity_res,
        "concentration_audits": concentration_res
    }
    with open(source_intel_path, "w", encoding="utf-8") as f:
        json.dump(source_intel_data, f, indent=2)
    print(f"Saved Source Intelligence JSON to: {source_intel_path}")
    
    # C. Source Registry JSON
    source_registry_path = "scratch/zzz11_source_registry.json"
    registry_data = {
        "registry_version": "1.0.0",
        "total_sources_registered": len(engine.source_registry.list_sources()),
        "sources": [s.to_dict() for s in engine.source_registry.list_sources()]
    }
    with open(source_registry_path, "w", encoding="utf-8") as f:
        json.dump(registry_data, f, indent=2)
    print(f"Saved Source Registry JSON to: {source_registry_path}")
    
    # D. Red Team JSON
    redteam_path = "scratch/zzz11_redteam.json"
    with open(redteam_path, "w", encoding="utf-8") as f:
        json.dump(redteam_res, f, indent=2)
    print(f"Saved Red Team JSON to: {redteam_path}")
    
    # E. Coverage Analysis JSON
    coverage_path = "scratch/zzz11_coverage_analysis.json"
    coverage_data = {
        "total_setups": len(m_df),
        "evidence_present_count": int((m_df["information_state"] == "EVIDENCE_PRESENT").sum()),
        "unobserved_count": int((m_df["information_state"] == "NO_EVIDENCE_IN_DATASET").sum()),
        "coverage_rate": float((m_df["information_state"] == "EVIDENCE_PRESENT").mean()),
        "commodity_coverage": float((m_df[m_df["exposure_group"].isin(["COAL_PRODUCER", "NICKEL_MINER"])]["information_state"] == "EVIDENCE_PRESENT").mean()),
        "non_commodity_coverage": float((m_df[~m_df["exposure_group"].isin(["COAL_PRODUCER", "NICKEL_MINER"])]["information_state"] == "EVIDENCE_PRESENT").mean()),
        "by_ticker": m_df.groupby("target_symbol")["information_state"].apply(lambda s: float((s == "EVIDENCE_PRESENT").mean())).to_dict(),
        "by_year": m_df.groupby(m_df["target_date"].str[:4])["information_state"].apply(lambda s: float((s == "EVIDENCE_PRESENT").mean())).to_dict()
    }
    with open(coverage_path, "w", encoding="utf-8") as f:
        json.dump(coverage_data, f, indent=2)
    print(f"Saved Coverage Analysis JSON to: {coverage_path}")
    
    print("\n" + "=" * 80)
    print("BATCH ZZZ.11 EXECUTION HARNESS COMPLETED SUCCESSFULLY")
    print("=" * 80)

if __name__ == "__main__":
    main()

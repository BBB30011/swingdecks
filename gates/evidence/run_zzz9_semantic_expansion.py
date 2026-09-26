"""
scratch/run_zzz9_semantic_expansion.py

Runner script for Batch ZZZ.9: Historical Semantic Explanation & Attribution Expansion.
Populates DuckDB semantic substrate, reconstructs all 73 frozen Layer E setups at timestamp T,
evaluates economic transmission and peer counterfactuals, runs Red Team adversarial audits,
and generates machine-readable parquet and summary JSON artifacts.
"""

import os
import sys
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.semantic_substrate_engine import SemanticSubstrateEngine
from core.semantic_attribution_engine import SemanticAttributionEngine

def main():
    print("=" * 80)
    print("BATCH ZZZ.9 — HISTORICAL SEMANTIC EXPLANATION & ATTRIBUTION EXPANSION")
    print("=" * 80)
    
    # 1. Populate Semantic Substrate
    print("\n--- 1. Populating and Auditing DuckDB Semantic Substrate ---")
    substrate = SemanticSubstrateEngine()
    counts = substrate.populate_substrate()
    print("DuckDB Table Counts:", counts)
    
    # 2. Load Evaluated Layer E Candidates
    input_parquet = "scratch/zzz82_oos_results.parquet"
    if not os.path.exists(input_parquet):
        input_parquet = "scratch/zzz81_ablation_results.parquet"
        
    df = pd.read_parquet(input_parquet)
    print(f"\nLoaded {len(df)} historical observations from {input_parquet}")
    layer_e_count = int(df["sel_layer_e"].sum())
    print(f"Layer E Candidates to reconstruct: {layer_e_count}")
    
    # 3. Execute 13-Dimensional Historical Semantic Attribution
    print("\n--- 2. Executing 13-Dimensional Context Reconstruction at T ---")
    engine = SemanticAttributionEngine()
    contexts, summary_df = engine.evaluate_all_layer_e_candidates(df)
    
    print("\nReconstructed Sample Context (First Candidate):")
    sample = contexts[0]
    print(f"Candidate: {sample.candidate_id} | Symbol: {sample.symbol} | Date: {sample.date}")
    print(f"Canonical Name: {sample.canonical_name} (Entity: {sample.entity_id})")
    print(f"Quant: Score={sample.quant_score}, RelVol={sample.rel_vol:.2f}, DayReturn={sample.day_return*100:+.2f}%")
    print(f"Specificity: {sample.sector_context['specificity_status']} (Diff Return: {sample.sector_context['differential_return']*100:+.2f}%)")
    print(f"Commodity Exposures: {sample.commodity_context['exposures']}")
    print(f"Controllers: {sample.ownership_context['controllers']}")
    print(f"Economic Transmission: {sample.economic_transmission}")
    print(f"Peer Counterfactual: Expected={sample.peer_counterfactual['expected_affected_universe']}, Movers={sample.peer_counterfactual['actual_movers']}")
    print(f"Red Team Result: {sample.red_team_result.overall_status.value}")
    print(f"Thesis: {sample.thesis_classification} | Outcome Alignment: {sample.outcome_alignment}")
    
    # 4. Summary Breakdowns
    print("\n--- 3. Attribution & Thesis Classification Breakdown ---")
    print("Thesis Distribution:")
    print(summary_df["thesis_classification"].value_counts())
    
    print("\nOutcome Alignment Breakdown:")
    print(summary_df["outcome_alignment"].value_counts())
    
    print("\nCommodity vs Non-Commodity Thesis Performance:")
    for has_comm, grp in summary_df.groupby("has_commodity_exposure"):
        label = "COMMODITY_EXPOSED" if has_comm else "NON_COMMODITY"
        h5_mean = grp["H5"].mean()
        h10_mean = grp["H10"].mean()
        wr = (grp["H5"] > 0).mean()
        print(f"  {label:20s} (N={len(grp):2d}) | H5 Mean={h5_mean*100:+.2f}% | H10 Mean={h10_mean*100:+.2f}% | H5 WR={wr*100:.1f}%")
        
    print("\nThesis Class vs Forward Return Performance:")
    for th_cls, grp in summary_df.groupby("thesis_classification"):
        h5_mean = grp["H5"].mean()
        h10_mean = grp["H10"].mean()
        wr = (grp["H5"] > 0).mean()
        print(f"  {th_cls:20s} (N={len(grp):2d}) | H5 Mean={h5_mean*100:+.2f}% | H10 Mean={h10_mean*100:+.2f}% | H5 WR={wr*100:.1f}%")
        
    # 5. Save Parquet
    out_parquet = "scratch/zzz9_semantic_results.parquet"
    summary_df.to_parquet(out_parquet, index=False)
    print(f"\nSaved semantic reconstruction results to {out_parquet}")
    
    # 6. Save Summary JSON
    summary = {
        "metadata": {
            "batch": "ZZZ.9",
            "experiment": "Historical Semantic Explanation & Attribution Expansion",
            "total_layer_e_candidates": len(summary_df),
            "substrate_table_counts": counts,
            "random_seed": 42
        },
        "thesis_distribution": summary_df["thesis_classification"].value_counts().to_dict(),
        "outcome_alignment_distribution": summary_df["outcome_alignment"].value_counts().to_dict(),
        "commodity_breakdown": {
            "COMMODITY_EXPOSED": {
                "N": int((summary_df["has_commodity_exposure"] == True).sum()),
                "H5_Mean": float(summary_df[summary_df["has_commodity_exposure"] == True]["H5"].mean()),
                "H10_Mean": float(summary_df[summary_df["has_commodity_exposure"] == True]["H10"].mean()),
                "H5_WinRate": float((summary_df[summary_df["has_commodity_exposure"] == True]["H5"] > 0).mean())
            },
            "NON_COMMODITY": {
                "N": int((summary_df["has_commodity_exposure"] == False).sum()),
                "H5_Mean": float(summary_df[summary_df["has_commodity_exposure"] == False]["H5"].mean()),
                "H10_Mean": float(summary_df[summary_df["has_commodity_exposure"] == False]["H10"].mean()),
                "H5_WinRate": float((summary_df[summary_df["has_commodity_exposure"] == False]["H5"] > 0).mean())
            }
        },
        "thesis_vs_outcome": {
            th_cls: {
                "N": len(grp),
                "H5_Mean": float(grp["H5"].mean()),
                "H10_Mean": float(grp["H10"].mean()),
                "H5_WinRate": float((grp["H5"] > 0).mean())
            }
            for th_cls, grp in summary_df.groupby("thesis_classification")
        },
        "reconstructed_candidates": [
            {
                "candidate_id": ctx.candidate_id,
                "symbol": ctx.symbol,
                "entity_id": ctx.entity_id,
                "canonical_name": ctx.canonical_name,
                "date": ctx.date,
                "quant_score": ctx.quant_score,
                "rel_vol": ctx.rel_vol,
                "day_return": ctx.day_return,
                "exposures": ctx.commodity_context["exposures"],
                "controllers": ctx.ownership_context["controllers"],
                "specificity_status": ctx.sector_context["specificity_status"],
                "differential_return": ctx.sector_context["differential_return"],
                "economic_transmission": ctx.economic_transmission,
                "peer_counterfactual": ctx.peer_counterfactual,
                "alternative_explanations": ctx.alternative_explanations,
                "unknowns": ctx.unknowns,
                "red_team_status": ctx.red_team_result.overall_status.value,
                "thesis_classification": ctx.thesis_classification,
                "invalidation_conditions": ctx.invalidation_conditions,
                "outcome_alignment": ctx.outcome_alignment,
                "forward_returns": ctx.forward_returns
            }
            for ctx in contexts
        ]
    }
    
    out_json = "scratch/zzz9_semantic_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"Saved semantic summary JSON to {out_json}")
    print("\nExecution complete.")

if __name__ == "__main__":
    main()

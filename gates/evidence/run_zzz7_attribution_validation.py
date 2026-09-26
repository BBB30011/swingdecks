import os
import sys
import json
import duckdb
import numpy as np
import pandas as pd
from collections import defaultdict
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.candidate_attribution_engine import CandidateAttributionEngine

def run_zzz7_attribution_validation():
    print("Loading historical observations from scratch/zzz62_observations.parquet...", flush=True)
    df_obs = pd.read_parquet("scratch/zzz62_observations.parquet")
    print(f"Loaded {len(df_obs)} observations.", flush=True)
    
    engine = CandidateAttributionEngine("data/duckdb/intelligence.duckdb")
    
    # Group observations by date to feed the day universe
    date_groups = {d: group.to_dict(orient="records") for d, group in df_obs.groupby("date")}
    
    attributions = []
    print(f"Evaluating 18-dimension intelligence coverage and attribution across {len(df_obs)} observations...", flush=True)
    
    for i, row in df_obs.iterrows():
        dt = row["date"]
        day_universe = date_groups[dt]
        
        attr = engine.evaluate_candidate(row.to_dict(), day_universe, pit_mode="PUBLIC_PIT")
        
        attr_dict = {
            "candidate_id": attr.candidate_id,
            "symbol": attr.symbol,
            "date": attr.signal_timestamp,
            "official_signal_state": attr.official_signal_state,
            "quant_score": attr.quant_score,
            "signal_day_return": attr.signal_day_return,
            "pit_mode": attr.pit_mode,
            "is_signal": attr.official_signal_state in ["WATCH", "EARLY_WATCH"],
            # Counts
            "evidence_count": attr.evidence_count,
            "pit_valid_evidence_count": attr.pit_valid_evidence_count,
            "future_evidence_excluded_count": attr.future_evidence_excluded_count,
            "contradictory_evidence_count": attr.contradictory_evidence_count,
            "unresolved_evidence_count": attr.unresolved_evidence_count,
            # Entity & Relationships
            "entity_id": attr.entity_id,
            "entity_status": attr.entity_status.value,
            "relationship_status": attr.relationship_status.value,
            "exposure_status": attr.exposure_status.value,
            "peer_status": attr.peer_status.value,
            "event_status": attr.event_status.value,
            # Peer Reaction & Specificity
            "peer_count": attr.peer_reaction.peer_count,
            "peer_mean_return": attr.peer_reaction.peer_mean_return,
            "differential_return": attr.peer_reaction.differential_return,
            "specificity_status": attr.specificity_status.value,
            # Attribution
            "primary_attribution": attr.primary_attribution,
            "market_component": attr.attribution_components.market_component.value,
            "sector_component": attr.attribution_components.sector_component.value,
            "factor_component": attr.attribution_components.factor_component.value,
            "flow_component": attr.attribution_components.flow_component.value,
            "news_component": attr.attribution_components.news_component.value,
            "company_specific_component": attr.attribution_components.company_specific_component.value,
            "unknown_component": attr.attribution_components.unknown_component.value,
            # Red Team
            "red_team_status": attr.red_team_status.value,
            "contradiction_count": len(attr.contradictions),
            "unknowns_count": len(attr.unknowns),
            # 18 Dimensions Coverage
            "cov_news": attr.evidence_coverage.news.value,
            "cov_corporate_action": attr.evidence_coverage.corporate_action.value,
            "cov_fundamental": attr.evidence_coverage.fundamental.value,
            "cov_macro": attr.evidence_coverage.macro.value,
            "cov_commodity": attr.evidence_coverage.commodity.value,
            "cov_fx": attr.evidence_coverage.fx.value,
            "cov_monetary": attr.evidence_coverage.monetary.value,
            "cov_policy": attr.evidence_coverage.policy.value,
            "cov_politics": attr.evidence_coverage.politics.value,
            "cov_geopolitics": attr.evidence_coverage.geopolitics.value,
            "cov_ownership": attr.evidence_coverage.ownership.value,
            "cov_relationship": attr.evidence_coverage.relationship.value,
            "cov_exposure": attr.evidence_coverage.exposure.value,
            "cov_flow": attr.evidence_coverage.flow.value,
            "cov_sentiment": attr.evidence_coverage.sentiment.value,
            "cov_market_structure": attr.evidence_coverage.market_structure.value,
            "cov_event_calendar": attr.evidence_coverage.event_calendar.value,
            "cov_peer_information": attr.evidence_coverage.peer_information.value,
            # Forward Outcomes (Strictly Separated)
            "forward_h1": attr.forward_h1_return,
            "forward_h5": attr.forward_h5_return,
            "forward_h20": attr.forward_h20_return
        }
        attributions.append(attr_dict)
        
        if (i + 1) % 500 == 0:
            print(f"Processed {i + 1}/{len(df_obs)} observations...", flush=True)
            
    df_attr = pd.DataFrame(attributions)
    df_attr.to_parquet("scratch/zzz7_candidate_attributions.parquet")
    print("Saved attributions to scratch/zzz7_candidate_attributions.parquet", flush=True)
    
    # Generate population statistics
    df_sig = df_attr[df_attr["is_signal"]].copy()
    df_ctrl = df_attr[~df_attr["is_signal"]].copy()
    
    summary = {
        "metadata": {
            "experiment_id": "BATCH_ZZZ_7_ATTRIBUTION_VALIDATION",
            "timestamp": "2026-09-14T13:40:00Z",
            "total_observations": len(df_attr),
            "n_signals": len(df_sig),
            "n_controls": len(df_ctrl),
            "signal_states": df_sig["official_signal_state"].value_counts().to_dict()
        },
        "evidence_coverage_18_dimensions": {
            "news": df_sig["cov_news"].value_counts().to_dict(),
            "corporate_action": df_sig["cov_corporate_action"].value_counts().to_dict(),
            "fundamental": df_sig["cov_fundamental"].value_counts().to_dict(),
            "macro": df_sig["cov_macro"].value_counts().to_dict(),
            "commodity": df_sig["cov_commodity"].value_counts().to_dict(),
            "fx": df_sig["cov_fx"].value_counts().to_dict(),
            "monetary": df_sig["cov_monetary"].value_counts().to_dict(),
            "policy": df_sig["cov_policy"].value_counts().to_dict(),
            "politics": df_sig["cov_politics"].value_counts().to_dict(),
            "geopolitics": df_sig["cov_geopolitics"].value_counts().to_dict(),
            "ownership": df_sig["cov_ownership"].value_counts().to_dict(),
            "relationship": df_sig["cov_relationship"].value_counts().to_dict(),
            "exposure": df_sig["cov_exposure"].value_counts().to_dict(),
            "flow": df_sig["cov_flow"].value_counts().to_dict(),
            "sentiment": df_sig["cov_sentiment"].value_counts().to_dict(),
            "market_structure": df_sig["cov_market_structure"].value_counts().to_dict(),
            "event_calendar": df_sig["cov_event_calendar"].value_counts().to_dict(),
            "peer_information": df_sig["cov_peer_information"].value_counts().to_dict()
        },
        "pit_metrics": {
            "signals": {
                "total_valid_events_mean": float(df_sig["pit_valid_evidence_count"].mean()),
                "total_valid_events_max": int(df_sig["pit_valid_evidence_count"].max()),
                "future_excluded_mean": float(df_sig["future_evidence_excluded_count"].mean()),
                "future_excluded_max": int(df_sig["future_evidence_excluded_count"].max()),
                "candidates_with_pit_events": int((df_sig["pit_valid_evidence_count"] > 0).sum()),
                "candidates_with_zero_pit_events": int((df_sig["pit_valid_evidence_count"] == 0).sum())
            },
            "controls": {
                "total_valid_events_mean": float(df_ctrl["pit_valid_evidence_count"].mean()),
                "candidates_with_pit_events": int((df_ctrl["pit_valid_evidence_count"] > 0).sum()),
                "candidates_with_zero_pit_events": int((df_ctrl["pit_valid_evidence_count"] == 0).sum())
            }
        },
        "specificity_distribution": {
            "signals": df_sig["specificity_status"].value_counts().to_dict(),
            "controls": df_ctrl["specificity_status"].value_counts().to_dict()
        },
        "primary_attribution_distribution": {
            "signals": df_sig["primary_attribution"].value_counts().to_dict(),
            "controls": df_ctrl["primary_attribution"].value_counts().to_dict()
        },
        "red_team_distribution": {
            "signals": df_sig["red_team_status"].value_counts().to_dict(),
            "controls": df_ctrl["red_team_status"].value_counts().to_dict()
        },
        "specificity_vs_forward_return": {}
    }
    
    # Forward return by specificity status (to evaluate if company-specific candidates differ from market-wide)
    for spec in ["MARKET_WIDE", "SECTOR_WIDE", "FACTOR_WIDE", "COMPANY_SPECIFIC_CANDIDATE", "UNKNOWN"]:
        spec_df = df_sig[df_sig["specificity_status"] == spec]
        summary["specificity_vs_forward_return"][spec] = {
            "n": len(spec_df),
            "H1_mean": float(spec_df["forward_h1"].dropna().mean()) if len(spec_df) > 0 else None,
            "H5_mean": float(spec_df["forward_h5"].dropna().mean()) if len(spec_df) > 0 else None,
            "H20_mean": float(spec_df["forward_h20"].dropna().mean()) if len(spec_df) > 0 else None,
            "H5_win_rate": float((spec_df["forward_h5"].dropna() > 0).mean()) if len(spec_df) > 0 else None
        }
        
    with open("scratch/zzz7_attribution_summary.json", "w") as f:
        json.dump(summary, f, indent=4)
        
    print("\n=== ZZZ.7 ATTRIBUTION VALIDATION SUMMARY ===")
    print(f"Total Evaluated: {len(df_attr)} (Signals: {len(df_sig)}, Controls: {len(df_ctrl)})")
    print("\nSpecificity Breakdown (Signals):")
    for k, v in summary["specificity_distribution"]["signals"].items():
        print(f"  {k}: {v} ({v/len(df_sig)*100:.1f}%)")
    print("\nPrimary Attribution (Signals):")
    for k, v in summary["primary_attribution_distribution"]["signals"].items():
        print(f"  {k}: {v} ({v/len(df_sig)*100:.1f}%)")
    print("\nRed Team Status (Signals):")
    for k, v in summary["red_team_distribution"]["signals"].items():
        print(f"  {k}: {v} ({v/len(df_sig)*100:.1f}%)")
    print("\nSpecificity vs Forward H5 Return:")
    for k, v in summary["specificity_vs_forward_return"].items():
        h5_str = f"{v['H5_mean']*100:+.2f}%" if v['H5_mean'] is not None else "N/A"
        wr_str = f"{v['H5_win_rate']*100:.1f}%" if v['H5_win_rate'] is not None else "N/A"
        print(f"  {k} (N={v['n']}): H5 Mean = {h5_str}, Win Rate = {wr_str}")

if __name__ == "__main__":
    run_zzz7_attribution_validation()

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

def run_zzz71_audit_population():
    print("Loading historical observations from scratch/zzz62_observations.parquet...", flush=True)
    df_obs = pd.read_parquet("scratch/zzz62_observations.parquet")
    print(f"Loaded {len(df_obs)} observations.", flush=True)
    
    engine = CandidateAttributionEngine("data/duckdb/intelligence.duckdb")
    
    # Group observations by date to feed the day universe
    date_groups = {d: group.to_dict(orient="records") for d, group in df_obs.groupby("date")}
    
    attributions = []
    print(f"Evaluating hardened intelligence coverage and attribution across {len(df_obs)} observations...", flush=True)
    
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
            # Causality Level
            "causality_level": attr.causality_level.value,
            # Red Team
            "red_team_status": attr.red_team_status.value,
            "red_team_time_leakage": attr.red_team_audit.time_leakage,
            "red_team_evidence_hallucination": attr.red_team_audit.evidence_hallucination,
            "red_team_logic_consistency": attr.red_team_audit.logic_consistency,
            "red_team_alternative_explanation": attr.red_team_audit.alternative_explanation,
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
    out_parquet = "scratch/zzz71_candidate_attributions.parquet"
    df_attr.to_parquet(out_parquet, index=False)
    print(f"Saved {len(df_attr)} attributions to {out_parquet}", flush=True)
    
    # Generate Summary Metrics
    sig_mask = df_attr["is_signal"]
    ctrl_mask = ~sig_mask
    
    summary = {
        "metadata": {
            "experiment_id": "BATCH_ZZZ_7_1_ATTRIBUTION_LOGIC_AUDIT",
            "timestamp": "2026-09-14T14:05:00Z",
            "total_observations": len(df_attr),
            "n_signals": int(sig_mask.sum()),
            "n_controls": int(ctrl_mask.sum()),
            "signal_states": df_attr[sig_mask]["official_signal_state"].value_counts().to_dict()
        },
        "evidence_coverage_18_dimensions": {
            dim[4:]: df_attr[sig_mask][dim].value_counts().to_dict()
            for dim in df_attr.columns if dim.startswith("cov_")
        },
        "pit_metrics": {
            "signals": {
                "total_valid_events_mean": float(df_attr[sig_mask]["pit_valid_evidence_count"].mean()),
                "total_valid_events_max": int(df_attr[sig_mask]["pit_valid_evidence_count"].max()),
                "future_excluded_mean": float(df_attr[sig_mask]["future_evidence_excluded_count"].mean()),
                "future_excluded_max": int(df_attr[sig_mask]["future_evidence_excluded_count"].max()),
                "candidates_with_pit_events": int((df_attr[sig_mask]["pit_valid_evidence_count"] > 0).sum()),
                "candidates_with_zero_pit_events": int((df_attr[sig_mask]["pit_valid_evidence_count"] == 0).sum())
            },
            "controls": {
                "total_valid_events_mean": float(df_attr[ctrl_mask]["pit_valid_evidence_count"].mean()),
                "candidates_with_pit_events": int((df_attr[ctrl_mask]["pit_valid_evidence_count"] > 0).sum()),
                "candidates_with_zero_pit_events": int((df_attr[ctrl_mask]["pit_valid_evidence_count"] == 0).sum())
            }
        },
        "specificity_distribution": {
            "signals": df_attr[sig_mask]["specificity_status"].value_counts().to_dict(),
            "controls": df_attr[ctrl_mask]["specificity_status"].value_counts().to_dict()
        },
        "primary_attribution_distribution": {
            "signals": df_attr[sig_mask]["primary_attribution"].value_counts().to_dict(),
            "controls": df_attr[ctrl_mask]["primary_attribution"].value_counts().to_dict()
        },
        "causality_distribution": {
            "signals": df_attr[sig_mask]["causality_level"].value_counts().to_dict(),
            "controls": df_attr[ctrl_mask]["causality_level"].value_counts().to_dict()
        },
        "red_team_checks": {
            "signals": {
                "overall_status": df_attr[sig_mask]["red_team_status"].value_counts().to_dict(),
                "time_leakage": df_attr[sig_mask]["red_team_time_leakage"].value_counts().to_dict(),
                "evidence_hallucination": df_attr[sig_mask]["red_team_evidence_hallucination"].value_counts().to_dict(),
                "logic_consistency": df_attr[sig_mask]["red_team_logic_consistency"].value_counts().to_dict(),
                "alternative_explanation": df_attr[sig_mask]["red_team_alternative_explanation"].value_counts().to_dict()
            },
            "controls": {
                "overall_status": df_attr[ctrl_mask]["red_team_status"].value_counts().to_dict(),
                "time_leakage": df_attr[ctrl_mask]["red_team_time_leakage"].value_counts().to_dict(),
                "evidence_hallucination": df_attr[ctrl_mask]["red_team_evidence_hallucination"].value_counts().to_dict(),
                "logic_consistency": df_attr[ctrl_mask]["red_team_logic_consistency"].value_counts().to_dict(),
                "alternative_explanation": df_attr[ctrl_mask]["red_team_alternative_explanation"].value_counts().to_dict()
            }
        },
        "specificity_vs_forward_return": {}
    }
    
    # Calculate returns across specificity regimes
    for spec, grp in df_attr[sig_mask].groupby("specificity_status"):
        h1 = grp["forward_h1"].dropna()
        h5 = grp["forward_h5"].dropna()
        h20 = grp["forward_h20"].dropna()
        summary["specificity_vs_forward_return"][spec] = {
            "n": len(grp),
            "H1_mean": float(h1.mean()) if len(h1) > 0 else None,
            "H5_mean": float(h5.mean()) if len(h5) > 0 else None,
            "H20_mean": float(h20.mean()) if len(h20) > 0 else None,
            "H5_win_rate": float((h5 > 0).mean()) if len(h5) > 0 else None
        }
        
    out_json = "scratch/zzz71_attribution_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"Saved summary metrics to {out_json}", flush=True)
    
    # Print key distributions
    print("\n--- BATCH ZZZ.7.1 POPULATION AUDIT RESULTS ---")
    print("\nSpecificity Status Distribution (Signals):")
    for k, v in summary["specificity_distribution"]["signals"].items():
        print(f"  {k}: {v}")
        
    print("\nPrimary Attribution Distribution (Signals):")
    for k, v in summary["primary_attribution_distribution"]["signals"].items():
        print(f"  {k}: {v}")
        
    print("\nCausality Distribution (Signals):")
    for k, v in summary["causality_distribution"]["signals"].items():
        print(f"  {k}: {v}")
        
    print("\nRed Team 4-Dimension Checks (Signals):")
    for check, counts in summary["red_team_checks"]["signals"].items():
        print(f"  {check}: {counts}")

if __name__ == "__main__":
    run_zzz71_audit_population()

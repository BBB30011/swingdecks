import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.attribution_schemas import SpecificityStatus, RedTeamStatus, CausalityLevel
from core.timing_engine import TriggerProximityEngine, PricedInEngine, TimingQualityEngine, EntryWindowEngine
from core.opportunity_ranker import OpportunityRanker
from core.risk_engine import RiskEngine, RiskEngineConfig
from core.decision import PortfolioContext

class MultiAgentExperimentEngine:
    """
    Deterministic Multi-Agent Incremental EV Experiment Engine for Batch ZZZ.8.
    Executes the 6-layer experiment ladder (Baseline, Layer A, Layer B, Layer C, Layer D, Layer E),
    strictly separating Point-in-Time reasoning from post-T evaluation outcomes.
    """
    def __init__(self, df_merged: pd.DataFrame, random_seed: int = 42):
        self.df = df_merged.copy()
        self.rng = np.random.default_rng(random_seed)
        self.horizons = ["H1", "H3", "H5", "H10", "H20"]
        
        # Initialize Agent 3 components
        self.risk_config = RiskEngineConfig({
            "risk": {"max_single_position_risk": 0.005, "max_portfolio_risk": 0.02},
            "trade": {"minimum_rr": 2.0, "maximum_positions": 5, "lot_size": 100},
            "decision": {"minimum_confidence": 70}
        })
        self.risk_engine = RiskEngine(self.risk_config)
        
    def evaluate_layers(self) -> pd.DataFrame:
        """
        Evaluates and applies the selection criteria for each of the 6 layers.
        Returns the DataFrame with boolean selection masks:
        - sel_baseline (Layer 0)
        - sel_layer_a (Layer A)
        - sel_layer_b (Layer B)
        - sel_layer_c (Layer C)
        - sel_layer_d (Layer D)
        - sel_layer_e (Layer E)
        """
        df = self.df.copy()
        
        # --- Layer 0: Baseline (Agent 1 Alone) ---
        # Selects all valid Agent 1 candidates (WATCH + EARLY_WATCH)
        df["sel_baseline"] = df["official_signal_state"].isin(["WATCH", "EARLY_WATCH"])
        
        # --- Layer A: Peer Context ---
        # Agent 1 + Contextual Peer information is available and contextual peer set is valid
        # Gating: Candidate has >= 1 valid contextual peer (filters isolated solitary stocks without peer context)
        df["sel_layer_a"] = df["sel_baseline"] & (df["peer_count"] > 0)
        
        # --- Layer B: Differential Intelligence ---
        # Agent 1 + Contextual Peer Specificity Regime
        # Gating: Selects candidates with Contextual Sector alignment (SECTOR_WIDE peer momentum)
        # where the candidate moves in harmony with contextual sector peers, rather than isolated divergence
        df["sel_layer_b"] = df["sel_layer_a"] & (df["specificity_status"] == SpecificityStatus.SECTOR_WIDE.value)
        
        # --- Layer C: Agent 2 + Red Team ---
        # Layer B + 4-Check Red Team Adversarial Audit
        # Gating: Rejects candidates failing Time Leakage, Logic Contradictions, or severe Confounding
        # Requires red_team_time_leakage == 'PASS' and red_team_logic_consistency == 'PASS'
        # and alternative_explanation != 'CONTRADICTED' and red_team_evidence_hallucination != 'FAIL'
        df["sel_layer_c"] = (
            df["sel_layer_b"] &
            (df["red_team_time_leakage"] == "PASS") &
            (df["red_team_logic_consistency"] == "PASS") &
            (df["red_team_evidence_hallucination"] != "FAIL") &
            (df["red_team_alternative_explanation"] != "CONTRADICTED")
        )
        
        # --- Layer D: Agent 3 Risk / Reward ---
        # Evaluates Agent 3 structural risk gates on candidates:
        # 1. Structural Stop Loss & Target Price with R/R >= 2.0
        # 2. Timing & Overextension check (not severely priced in)
        # 3. Quant Score & Technical Factor state
        sel_d_list = []
        sel_e_list = []
        opp_scores = []
        agent3_actions = []
        
        for _, row in df.iterrows():
            if not row["sel_baseline"]:
                sel_d_list.append(False)
                sel_e_list.append(False)
                opp_scores.append(0.0)
                agent3_actions.append("REJECT")
                continue
                
            q_score = float(row.get("quant_score", 0.0) or 0.0)
            atr_pct = float(row.get("atr_pct", 0.02) or 0.02)
            day_ret = float(row.get("signal_day_return", 0.0) or 0.0)
            
            # Simulated PIT price and structural stop loss (2 * ATR stop below entry)
            # Reference entry price normalized to 1000 for standard calculation
            entry_price = 1000.0
            stop_distance = entry_price * max(atr_pct * 1.5, 0.03)
            stop_loss = entry_price - stop_distance
            target_price = entry_price + (2.0 * stop_distance) # Enforces R/R = 2.0
            
            # Evaluate Trigger Proximity & Priced In status
            # If day return is > 6%, setup is considered short-term overextended / priced-in
            move_pct = day_ret
            priced_in = PricedInEngine.evaluate(
                move_pct_from_reference=move_pct,
                catalyst_materiality="MEDIUM",
                catalyst_decay="SLOW"
            )
            
            timing = TimingQualityEngine.evaluate(
                signal_state="ENTRY_READY" if q_score >= 80 else "SETUP_FORMING",
                trigger_proximity=TriggerProximityEngine.evaluate(entry_price, entry_price),
                priced_in_status=priced_in,
                technical_state="POSITIVE" if q_score >= 80 else "NEUTRAL",
                evidence_state="GOOD" if row["peer_count"] > 0 else "PARTIAL"
            )
            
            # Opportunity Ranker Score
            opp_res = OpportunityRanker.score_candidate(
                quant_score=q_score,
                technical_state="POSITIVE" if q_score >= 80 else "NEUTRAL",
                flow_state="CONFIRMED" if float(row.get("rel_vol", 1.0) or 1.0) > 1.2 else "NEUTRAL",
                market_regime=row.get("stock_regime", "UNKNOWN"),
                catalyst_materiality="MEDIUM",
                catalyst_decay="SLOW",
                catalyst_state="ACTIVE",
                evidence_quality="GOOD" if row["peer_count"] > 0 else "PARTIAL",
                risk_state="GREEN",
                signal_state="ENTRY_READY" if q_score >= 80 else "SETUP_FORMING",
                current_price=entry_price,
                trigger_price=entry_price,
                stop_loss=stop_loss
            )
            
            opp_score = opp_res.total_score
            opp_scores.append(opp_score)
            
            # Simulated Portfolio Context
            port = PortfolioContext(
                capital=100_000_000.0,
                available_cash=80_000_000.0,
                current_positions=[],
                number_of_positions=1,
                total_risk=0.005,
                as_of_timestamp=row["date"]
            )
            
            # Risk Engine Evaluation
            risk_eval = self.risk_engine.evaluate(
                symbol=row["symbol"],
                entry=entry_price,
                stop=stop_loss,
                target=target_price,
                portfolio=port,
                quant_data={"data_quality": "VALID", "quant_score": q_score},
                research_data={"completeness": "COMPLETE", "red_team_decision": "PASS", "confidence": 75}
            )
            
            a3_action = risk_eval["action"]
            agent3_actions.append(a3_action)
            
            # Layer D: Layer C + Agent 3 Risk/Reward approval (R/R >= 2.0, Risk Green, Action == BUY, not overextended)
            is_d_selected = (
                row["sel_layer_c"] and
                a3_action == "BUY" and
                risk_eval["risk_state"] == "GREEN" and
                risk_eval["risk_reward_ratio"] >= 2.0 and
                priced_in.value != "PRICED_IN"
            )
            sel_d_list.append(is_d_selected)
            
            # Layer E: Full 3-Agent Synthesis (Layer D + Opportunity Score >= 60.0 for high conviction tier)
            is_e_selected = is_d_selected and (opp_score >= 60.0)
            sel_e_list.append(is_e_selected)
            
        df["sel_layer_d"] = sel_d_list
        df["sel_layer_e"] = sel_e_list
        df["opportunity_score"] = opp_scores
        df["agent3_action"] = agent3_actions
        
        self.df = df
        return df

    def compute_layer_metrics(self) -> Dict[str, Any]:
        """
        Computes detailed summary metrics for all 6 layers across H1, H3, H5, H10, H20.
        """
        df = self.df
        layer_masks = {
            "Baseline": df["sel_baseline"],
            "Layer_A": df["sel_layer_a"],
            "Layer_B": df["sel_layer_b"],
            "Layer_C": df["sel_layer_c"],
            "Layer_D": df["sel_layer_d"],
            "Layer_E": df["sel_layer_e"]
        }
        
        total_candidates = int(df["sel_baseline"].sum())
        results = {}
        
        for layer_name, mask in layer_masks.items():
            sub_df = df[mask]
            n_sel = len(sub_df)
            n_rej = total_candidates - n_sel
            sel_rate = (n_sel / total_candidates) if total_candidates > 0 else 0.0
            
            layer_res = {
                "n": n_sel,
                "n_rejected": n_rej,
                "selection_rate": sel_rate,
                "horizons": {}
            }
            
            for h in self.horizons:
                ret_series = sub_df[h].dropna()
                mfe_series = sub_df[f"{h}_mfe"].dropna() if f"{h}_mfe" in sub_df.columns else pd.Series(dtype=float)
                mae_series = sub_df[f"{h}_mae"].dropna() if f"{h}_mae" in sub_df.columns else pd.Series(dtype=float)
                
                if len(ret_series) > 0:
                    mean_val = float(ret_series.mean())
                    median_val = float(ret_series.median())
                    std_val = float(ret_series.std()) if len(ret_series) > 1 else 0.0
                    
                    # 10% Trimmed Mean
                    trim_cut = int(len(ret_series) * 0.10)
                    if trim_cut > 0 and len(ret_series) > 2 * trim_cut:
                        sorted_vals = np.sort(ret_series.values)
                        trimmed_mean = float(np.mean(sorted_vals[trim_cut:-trim_cut]))
                    else:
                        trimmed_mean = mean_val
                        
                    win_rate = float((ret_series > 0).mean())
                    mean_mfe = float(mfe_series.mean()) if len(mfe_series) > 0 else 0.0
                    mean_mae = float(mae_series.mean()) if len(mae_series) > 0 else 0.0
                else:
                    mean_val = median_val = trimmed_mean = std_val = win_rate = mean_mfe = mean_mae = 0.0
                    
                layer_res["horizons"][h] = {
                    "mean": mean_val,
                    "median": median_val,
                    "trimmed_mean": trimmed_mean,
                    "std": std_val,
                    "win_rate": win_rate,
                    "mfe": mean_mfe,
                    "mae": mean_mae
                }
            results[layer_name] = layer_res
            
        return results

    def compute_incremental_ev(self, layer_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes step-by-step and total incremental EV across layers:
        - Layer A - Baseline
        - Layer B - Layer A
        - Layer C - Layer B
        - Layer D - Layer C
        - Layer E - Layer D
        - Full: Layer E - Baseline
        """
        layer_keys = ["Baseline", "Layer_A", "Layer_B", "Layer_C", "Layer_D", "Layer_E"]
        step_diffs = {}
        
        for i in range(1, len(layer_keys)):
            prev_k = layer_keys[i - 1]
            curr_k = layer_keys[i]
            pair_name = f"{curr_k}_vs_{prev_k}"
            
            step_diffs[pair_name] = {}
            for h in self.horizons:
                ev_prev = layer_metrics[prev_k]["horizons"][h]["mean"]
                ev_curr = layer_metrics[curr_k]["horizons"][h]["mean"]
                diff = ev_curr - ev_prev
                step_diffs[pair_name][h] = float(diff)
                
        # Full Incremental EV
        full_diff = {}
        for h in self.horizons:
            ev_base = layer_metrics["Baseline"]["horizons"][h]["mean"]
            ev_e = layer_metrics["Layer_E"]["horizons"][h]["mean"]
            full_diff[h] = float(ev_e - ev_base)
            
        return {
            "step_increments": step_diffs,
            "full_incremental_ev": full_diff
        }

    def run_bootstrap_validation(self, n_iterations: int = 10000) -> Dict[str, Any]:
        """
        Runs IID Bootstrap and Date-Clustered Bootstrap validation (10,000 iterations)
        to compute 95% Confidence Intervals and empirical p-values for Full Incremental EV
        (Layer E vs Baseline) and intermediate layers.
        """
        df = self.df[self.df["sel_baseline"]].copy().reset_index(drop=True)
        results = {
            "iid_bootstrap": {},
            "date_clustered_bootstrap": {},
            "permutation_test": {}
        }
        
        # 1. IID Bootstrap
        for h in self.horizons:
            valid_mask = ~df[h].isna()
            v_df = df[valid_mask].reset_index(drop=True)
            
            base_returns = v_df[h].values
            e_mask = v_df["sel_layer_e"].values
            
            observed_diff = float(np.mean(base_returns[e_mask]) - np.mean(base_returns))
            
            boot_diffs = np.empty(n_iterations)
            n_samples = len(v_df)
            
            for b in range(n_iterations):
                idx = self.rng.integers(0, n_samples, size=n_samples)
                sample_ret = base_returns[idx]
                sample_emask = e_mask[idx]
                
                if sample_emask.sum() > 0:
                    diff_b = np.mean(sample_ret[sample_emask]) - np.mean(sample_ret)
                else:
                    diff_b = 0.0
                boot_diffs[b] = diff_b
                
            ci_lower = float(np.percentile(boot_diffs, 2.5))
            ci_upper = float(np.percentile(boot_diffs, 97.5))
            p_val = float((boot_diffs <= 0.0).mean()) if observed_diff > 0 else float((boot_diffs >= 0.0).mean())
            
            results["iid_bootstrap"][h] = {
                "observed_diff": observed_diff,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
                "p_value": p_val,
                "significant_at_05": p_val < 0.05
            }
            
        # 2. Date-Clustered Bootstrap
        for h in self.horizons:
            valid_mask = ~df[h].isna()
            v_df = df[valid_mask].reset_index(drop=True)
            
            unique_dates = v_df["date"].unique()
            n_dates = len(unique_dates)
            date_group_indices = {d: np.where(v_df["date"] == d)[0] for d in unique_dates}
            
            base_returns = v_df[h].values
            e_mask = v_df["sel_layer_e"].values
            observed_diff = results["iid_bootstrap"][h]["observed_diff"]
            
            cluster_diffs = np.empty(n_iterations)
            
            for b in range(n_iterations):
                resampled_dates = self.rng.choice(unique_dates, size=n_dates, replace=True)
                resampled_indices = np.concatenate([date_group_indices[d] for d in resampled_dates])
                
                sample_ret = base_returns[resampled_indices]
                sample_emask = e_mask[resampled_indices]
                
                if sample_emask.sum() > 0:
                    diff_b = np.mean(sample_ret[sample_emask]) - np.mean(sample_ret)
                else:
                    diff_b = 0.0
                cluster_diffs[b] = diff_b
                
            ci_lower_c = float(np.percentile(cluster_diffs, 2.5))
            ci_upper_c = float(np.percentile(cluster_diffs, 97.5))
            p_val_c = float((cluster_diffs <= 0.0).mean()) if observed_diff > 0 else float((cluster_diffs >= 0.0).mean())
            
            results["date_clustered_bootstrap"][h] = {
                "observed_diff": observed_diff,
                "ci_lower": ci_lower_c,
                "ci_upper": ci_upper_c,
                "p_value": p_val_c,
                "significant_at_05": p_val_c < 0.05
            }
            
        # 3. Permutation Test (5,000 permutations)
        n_perms = 5000
        for h in self.horizons:
            valid_mask = ~df[h].isna()
            v_df = df[valid_mask].reset_index(drop=True)
            
            base_returns = v_df[h].values
            e_mask = v_df["sel_layer_e"].values
            n_e = int(e_mask.sum())
            observed_diff = results["iid_bootstrap"][h]["observed_diff"]
            
            perm_diffs = np.empty(n_perms)
            for p in range(n_perms):
                perm_idx = self.rng.permutation(len(v_df))
                perm_emask = np.zeros(len(v_df), dtype=bool)
                perm_emask[perm_idx[:n_e]] = True
                diff_p = np.mean(base_returns[perm_emask]) - np.mean(base_returns)
                perm_diffs[p] = diff_p
                
            p_val_perm = float((perm_diffs >= observed_diff).mean()) if observed_diff > 0 else float((perm_diffs <= observed_diff).mean())
            results["permutation_test"][h] = {
                "observed_diff": observed_diff,
                "p_value": p_val_perm,
                "significant_at_05": p_val_perm < 0.05
            }
            
        return results

    def compute_robustness_and_concentration(self) -> Dict[str, Any]:
        """
        Computes ticker concentration and top-date sensitivity analysis.
        """
        df = self.df[self.df["sel_baseline"]].copy()
        ticker_breakdown = {}
        
        for sym, grp in df.groupby("symbol"):
            n_base = len(grp)
            n_e = int(grp["sel_layer_e"].sum())
            ticker_breakdown[sym] = {
                "n_baseline": n_base,
                "n_layer_e": n_e,
                "h5_baseline_mean": float(grp["H5"].mean()),
                "h5_layer_e_mean": float(grp[grp["sel_layer_e"]]["H5"].mean()) if n_e > 0 else None
            }
            
        # Top 3 dates contribution
        e_df = df[df["sel_layer_e"]].copy()
        if len(e_df) > 0:
            date_contributions = e_df.groupby("date")["H5"].agg(["count", "mean"]).sort_values(by="mean", ascending=False)
            top_3_dates = date_contributions.head(3).to_dict(orient="index")
        else:
            top_3_dates = {}
            
        return {
            "ticker_concentration": ticker_breakdown,
            "top_3_dates": top_3_dates
        }

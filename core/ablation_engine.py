"""
core/ablation_engine.py

Deterministic Ablation and Selection Robustness Experiment Engine for Batch ZZZ.8.1.
Systematically isolates components C1-C7 of Layer E, performs Leave-One-Out,
Matched-Selection Controls, Ticker/Sector/Date Concentration audits, and Clustered Statistical Inference.
"""

import os
import sys
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.attribution_schemas import SpecificityStatus, RedTeamStatus, CausalityLevel

class AblationEngine:
    """
    Controlled ablation and selection robustness testing engine for SwingDeck Batch ZZZ.8.1.
    """
    
    # Sector groups mapping for the 12 IDX pilot universe
    SECTOR_GROUPS = {
        "ENERGY_COAL": ["ADRO", "ITMG", "PTBA"],
        "MINING_METALS": ["ANTM", "INCO"],
        "BANKING_FINANCIAL": ["BBCA", "BBNI", "BBRI", "BMRI"],
        "AUTOMOTIVE_CONGLOMERATE": ["ASII"],
        "HEAVY_EQUIPMENT": ["UNTR"],
        "TELCO": ["TLKM"]
    }

    TICKER_TO_SECTOR = {}
    for sec, tickers in SECTOR_GROUPS.items():
        for t in tickers:
            TICKER_TO_SECTOR[t] = sec

    def __init__(self, df_merged: pd.DataFrame, random_seed: int = 42):
        self.df = df_merged.copy()
        self.rng = np.random.default_rng(random_seed)
        self.horizons = ["H1", "H3", "H5", "H10", "H20"]
        
        # Ensure sector column
        if "sector_group" not in self.df.columns:
            self.df["sector_group"] = self.df["symbol"].map(self.TICKER_TO_SECTOR).fillna("UNKNOWN")

    @classmethod
    def get_layer_e_contract(cls) -> Dict[str, Any]:
        """
        Returns the explicit machine-readable Layer E contract.
        """
        return {
            "LAYER_E_CONTRACT": {
                "sector_alignment": "SECTOR_WIDE (Contextual Peer Harmony)",
                "opportunity_score": ">= 60.0 (High Conviction Synthesis)",
                "quant_score": ">= 80.0 (Technical Breakout Readiness)",
                "relative_volume": "> 1.2 (Volume Acceleration)",
                "flow_confirmation": "CONFIRMED (rel_vol > 1.2)",
                "red_team": "CLEAN (Pass time_leakage & logic, no hallucination, not contradicted)",
                "agent3_risk_gate": "BUY + GREEN + R/R >= 2.0 + NOT_PRICED_IN"
            },
            "AGENT3_COMPOSITE_DEPENDENCY": True,
            "AGENT3_COMPOSITE_EXPLANATION": "opportunity_score >= 60.0 is algebraically equivalent to (quant_score >= 80) & (rel_vol > 1.2) under the standard scoring weights."
        }

    def isolate_component_masks(self) -> Dict[str, pd.Series]:
        """
        Creates independent boolean masks for each component C1 to C7.
        """
        df = self.df
        
        # Baseline pool: valid Agent 1 candidates with contextual peer context
        base_mask = df["sel_baseline"] & (df["peer_count"] > 0)
        
        # C1: Sector Alignment
        c1_sector = df["specificity_status"] == SpecificityStatus.SECTOR_WIDE.value
        
        # C2: Opportunity Score >= 60.0
        c2_opp_score = df["opportunity_score"] >= 60.0
        
        # C3: Quant Score >= 80.0
        c3_quant = df["quant_score"] >= 80.0
        
        # C4: Relative Volume > 1.2
        c4_rel_vol = df["rel_vol"] > 1.2
        
        # C5: Flow Confirmation
        c5_flow = df["rel_vol"] > 1.2
        
        # C6: Red Team Clean Status
        c6_red_team = (
            (df["red_team_time_leakage"] == "PASS") &
            (df["red_team_logic_consistency"] == "PASS") &
            (df["red_team_evidence_hallucination"] != "FAIL") &
            (df["red_team_alternative_explanation"] != "CONTRADICTED")
        )
        
        # C7: Agent 3 Risk Gate
        c7_agent3_risk = df["agent3_action"] == "BUY"
        
        return {
            "BASE": base_mask,
            "C1_SECTOR": c1_sector,
            "C2_OPP_SCORE": c2_opp_score,
            "C3_QUANT": c3_quant,
            "C4_REL_VOL": c4_rel_vol,
            "C5_FLOW": c5_flow,
            "C6_RED_TEAM": c6_red_team,
            "C7_RISK_GATE": c7_agent3_risk
        }

    def _calc_stats(self, series: pd.Series) -> Dict[str, float]:
        """Computes summary statistics for a return series."""
        s = series.dropna()
        n = len(s)
        if n == 0:
            return {"n": 0, "mean": 0.0, "median": 0.0, "trimmed_mean": 0.0, "std": 0.0, "win_rate": 0.0}
        
        mean_val = float(s.mean())
        median_val = float(s.median())
        std_val = float(s.std()) if n > 1 else 0.0
        win_rate = float((s > 0).mean())
        
        trim_cut = int(n * 0.10)
        if trim_cut > 0 and n > 2 * trim_cut:
            sorted_vals = np.sort(s.values)
            trimmed_mean = float(np.mean(sorted_vals[trim_cut:-trim_cut]))
        else:
            trimmed_mean = mean_val
            
        return {
            "n": n,
            "mean": mean_val,
            "median": median_val,
            "trimmed_mean": trimmed_mean,
            "std": std_val,
            "win_rate": win_rate
        }

    def run_experiment_1_single_ablation(self) -> pd.DataFrame:
        """
        Experiment 1: Single Component Addition.
        Starting from Layer D (N=252), evaluates adding each component independently.
        Also evaluates each component added directly to Baseline (N=1242).
        """
        df = self.df
        masks = self.isolate_component_masks()
        d_mask = df["sel_layer_d"]
        base_mask = df["sel_baseline"]
        
        exp1_rows = []
        
        # Test variations from Layer D
        d_sub = df[d_mask]
        d_h5 = d_sub["H5"].mean()
        
        variations_from_d = [
            ("Layer D (Reference)", d_mask),
            ("D + Opportunity Score (C2 >= 60.0)", d_mask & masks["C2_OPP_SCORE"]),
            ("D + Quant Score (C3 >= 80.0)", d_mask & masks["C3_QUANT"]),
            ("D + Relative Volume (C4 > 1.2)", d_mask & masks["C4_REL_VOL"]),
            ("D + Flow Confirmation (C5 CONFIRMED)", d_mask & masks["C5_FLOW"]),
            ("D + Sector Alignment (C1)", d_mask & masks["C1_SECTOR"])
        ]
        
        total_candidates = int(base_mask.sum())
        
        for name, mask in variations_from_d:
            sub = df[mask]
            n = len(sub)
            sel_rate = n / total_candidates if total_candidates > 0 else 0.0
            
            row_dict = {
                "Configuration": name,
                "N": n,
                "Selection_Rate": sel_rate
            }
            
            for h in self.horizons:
                stats = self._calc_stats(sub[h])
                row_dict[f"{h}_Mean"] = stats["mean"]
                row_dict[f"{h}_Median"] = stats["median"]
                row_dict[f"{h}_Trimmed"] = stats["trimmed_mean"]
                row_dict[f"{h}_WR"] = stats["win_rate"]
                
                mfe_s = sub[f"{h}_mfe"].dropna() if f"{h}_mfe" in sub.columns else pd.Series(dtype=float)
                mae_s = sub[f"{h}_mae"].dropna() if f"{h}_mae" in sub.columns else pd.Series(dtype=float)
                row_dict[f"{h}_MFE"] = float(mfe_s.mean()) if len(mfe_s) > 0 else 0.0
                row_dict[f"{h}_MAE"] = float(mae_s.mean()) if len(mae_s) > 0 else 0.0
                
            row_dict["Incremental_H5_vs_D"] = row_dict["H5_Mean"] - d_h5
            exp1_rows.append(row_dict)
            
        return pd.DataFrame(exp1_rows)

    def run_experiment_2_leave_one_out(self) -> pd.DataFrame:
        """
        Experiment 2: Leave-One-Component-Out (Primary Ablation Test).
        Starting from FULL Layer E (N=73), removes one component at a time.
        """
        df = self.df
        masks = self.isolate_component_masks()
        
        # FULL: Conjunction of Base + C1 + C2 + C3 + C4 + C5 + C6 + C7
        # Note: in code, FULL is sel_layer_e (which has all conditions)
        full_mask = df["sel_layer_e"]
        
        # Leave-One-Out definitions
        loo_configs = {
            "FULL": full_mask,
            "FULL - C1 (Sector Alignment)": (
                masks["BASE"] &
                masks["C3_QUANT"] &
                masks["C4_REL_VOL"] &
                masks["C6_RED_TEAM"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C2 (Opportunity Score)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C3_QUANT"] &
                masks["C4_REL_VOL"] &
                masks["C6_RED_TEAM"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C3 (Quant Score >= 80)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C4_REL_VOL"] &
                masks["C6_RED_TEAM"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C4 (Relative Volume > 1.2)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C3_QUANT"] &
                masks["C6_RED_TEAM"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C5 (Flow Confirmation)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C3_QUANT"] &
                masks["C6_RED_TEAM"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C6 (Red Team Gate)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C3_QUANT"] &
                masks["C4_REL_VOL"] &
                masks["C7_RISK_GATE"]
            ),
            "FULL - C7 (Agent 3 Risk Gate)": (
                masks["BASE"] &
                masks["C1_SECTOR"] &
                masks["C3_QUANT"] &
                masks["C4_REL_VOL"] &
                masks["C6_RED_TEAM"]
            )
        }
        
        full_sub = df[full_mask]
        full_h5 = full_sub["H5"].mean()
        full_h10 = full_sub["H10"].mean()
        
        loo_rows = []
        for name, mask in loo_configs.items():
            sub = df[mask]
            n = len(sub)
            
            row_dict = {
                "Configuration": name,
                "N": n,
                "Delta_N_vs_FULL": n - len(full_sub)
            }
            
            for h in self.horizons:
                stats = self._calc_stats(sub[h])
                row_dict[f"{h}_Mean"] = stats["mean"]
                row_dict[f"{h}_Median"] = stats["median"]
                row_dict[f"{h}_Trimmed"] = stats["trimmed_mean"]
                row_dict[f"{h}_WR"] = stats["win_rate"]
                
                mfe_s = sub[f"{h}_mfe"].dropna() if f"{h}_mfe" in sub.columns else pd.Series(dtype=float)
                mae_s = sub[f"{h}_mae"].dropna() if f"{h}_mae" in sub.columns else pd.Series(dtype=float)
                row_dict[f"{h}_MFE"] = float(mfe_s.mean()) if len(mfe_s) > 0 else 0.0
                row_dict[f"{h}_MAE"] = float(mae_s.mean()) if len(mae_s) > 0 else 0.0
                
            row_dict["Contribution_H5"] = full_h5 - row_dict["H5_Mean"]
            row_dict["Contribution_H10"] = full_h10 - row_dict["H10_Mean"]
            
            loo_rows.append(row_dict)
            
        return pd.DataFrame(loo_rows)

    def run_experiment_4_sequential_buildup(self) -> pd.DataFrame:
        """
        Experiment 4: Sequential Build-Up Funnel.
        Builds the strategy from Baseline through Layer E in fixed deterministic order.
        """
        df = self.df
        masks = self.isolate_component_masks()
        
        stages = [
            ("Baseline (Agent 1)", df["sel_baseline"]),
            ("+ Peer Context (Layer A)", df["sel_baseline"] & (df["peer_count"] > 0)),
            ("+ Sector Alignment (Layer B)", df["sel_layer_b"]),
            ("+ Red Team Gate (Layer C)", df["sel_layer_c"]),
            ("+ Agent 3 Risk Gate (Layer D)", df["sel_layer_d"]),
            ("+ Quant Score >= 80", df["sel_layer_d"] & masks["C3_QUANT"]),
            ("+ Relative Volume / Flow > 1.2", df["sel_layer_d"] & masks["C3_QUANT"] & masks["C4_REL_VOL"]),
            ("+ Opportunity Score >= 60.0 (Layer E)", df["sel_layer_e"])
        ]
        
        total_candidates = int(df["sel_baseline"].sum())
        buildup_rows = []
        prev_h5 = None
        
        for name, mask in stages:
            sub = df[mask]
            n = len(sub)
            pct_base = (n / total_candidates * 100.0) if total_candidates > 0 else 0.0
            
            h5_stats = self._calc_stats(sub["H5"])
            h10_stats = self._calc_stats(sub["H10"])
            
            h5_mean = h5_stats["mean"]
            h10_mean = h10_stats["mean"]
            
            inc_h5 = (h5_mean - prev_h5) if prev_h5 is not None else 0.0
            prev_h5 = h5_mean
            
            buildup_rows.append({
                "Stage": name,
                "N": n,
                "Pct_Baseline": pct_base,
                "H5": h5_mean,
                "H10": h10_mean,
                "Incremental_H5": inc_h5,
                "H5_Win_Rate": h5_stats["win_rate"]
            })
            
        return pd.DataFrame(buildup_rows)

    def run_experiment_5_matched_selection_control(self, n_iterations: int = 1000) -> Dict[str, Any]:
        """
        Experiment 5: Matched-Selection Controls.
        Tests whether drawing N=73 observations at random, or matched by date/ticker,
        yields comparable returns to Layer E.
        """
        df = self.df
        base_df = df[df["sel_baseline"]].copy()
        layer_e_df = df[df["sel_layer_e"]].copy()
        
        n_target = len(layer_e_df) # 73
        
        layer_e_h5 = float(layer_e_df["H5"].mean())
        layer_e_h10 = float(layer_e_df["H10"].mean())
        
        # 1. Uniform Random Matched Control (N=73 from 1242 candidates)
        random_h5_means = []
        random_h10_means = []
        
        for _ in range(n_iterations):
            sample_idx = self.rng.choice(len(base_df), size=n_target, replace=False)
            samp = base_df.iloc[sample_idx]
            random_h5_means.append(float(samp["H5"].mean()))
            random_h10_means.append(float(samp["H10"].mean()))
            
        random_h5_arr = np.array(random_h5_means)
        random_h10_arr = np.array(random_h10_means)
        
        # 2. Date-Matched Control
        # For each Layer E candidate with date t, sample another candidate from date t
        date_matched_h5 = []
        date_matched_h10 = []
        
        # Group baseline by date
        base_by_date = defaultdict(list)
        for idx, row in base_df.iterrows():
            base_by_date[row["date"]].append(row)
            
        for _ in range(n_iterations):
            sampled_rows = []
            for _, e_row in layer_e_df.iterrows():
                dt = e_row["date"]
                candidates = base_by_date.get(dt, [])
                if len(candidates) > 0:
                    chosen = candidates[self.rng.integers(0, len(candidates))]
                    sampled_rows.append(chosen)
            if len(sampled_rows) > 0:
                s_df = pd.DataFrame(sampled_rows)
                date_matched_h5.append(float(s_df["H5"].mean()))
                date_matched_h10.append(float(s_df["H10"].mean()))
                
        date_h5_arr = np.array(date_matched_h5)
        date_h10_arr = np.array(date_matched_h10)
        
        # 3. Ticker/Date-Matched Control
        # Group baseline by (symbol, date) or symbol
        ticker_matched_h5 = []
        ticker_matched_h10 = []
        base_by_sym = defaultdict(list)
        for idx, row in base_df.iterrows():
            base_by_sym[row["symbol"]].append(row)
            
        for _ in range(n_iterations):
            sampled_rows = []
            for _, e_row in layer_e_df.iterrows():
                sym = e_row["symbol"]
                candidates = base_by_sym.get(sym, [])
                if len(candidates) > 0:
                    chosen = candidates[self.rng.integers(0, len(candidates))]
                    sampled_rows.append(chosen)
            if len(sampled_rows) > 0:
                s_df = pd.DataFrame(sampled_rows)
                ticker_matched_h5.append(float(s_df["H5"].mean()))
                ticker_matched_h10.append(float(s_df["H10"].mean()))
                
        ticker_h5_arr = np.array(ticker_matched_h5)
        ticker_h10_arr = np.array(ticker_matched_h10)
        
        # P-values: proportion of matched controls with return >= Layer E return
        p_random_h5 = float(np.mean(random_h5_arr >= layer_e_h5))
        p_date_h5 = float(np.mean(date_h5_arr >= layer_e_h5))
        p_ticker_h5 = float(np.mean(ticker_h5_arr >= layer_e_h5))
        
        p_random_h10 = float(np.mean(random_h10_arr >= layer_e_h10))
        p_date_h10 = float(np.mean(date_h10_arr >= layer_e_h10))
        p_ticker_h10 = float(np.mean(ticker_h10_arr >= layer_e_h10))
        
        return {
            "Layer_E": {"H5": layer_e_h5, "H10": layer_e_h10, "N": n_target},
            "Random_Matched": {
                "H5_Mean": float(np.mean(random_h5_arr)),
                "H5_95_CI": [float(np.percentile(random_h5_arr, 2.5)), float(np.percentile(random_h5_arr, 97.5))],
                "H10_Mean": float(np.mean(random_h10_arr)),
                "H10_95_CI": [float(np.percentile(random_h10_arr, 2.5)), float(np.percentile(random_h10_arr, 97.5))],
                "P_Value_H5": p_random_h5,
                "P_Value_H10": p_random_h10
            },
            "Date_Matched": {
                "H5_Mean": float(np.mean(date_h5_arr)),
                "H5_95_CI": [float(np.percentile(date_h5_arr, 2.5)), float(np.percentile(date_h5_arr, 97.5))],
                "H10_Mean": float(np.mean(date_h10_arr)),
                "H10_95_CI": [float(np.percentile(date_h10_arr, 2.5)), float(np.percentile(date_h10_arr, 97.5))],
                "P_Value_H5": p_date_h5,
                "P_Value_H10": p_date_h10
            },
            "Ticker_Matched": {
                "H5_Mean": float(np.mean(ticker_h5_arr)),
                "H5_95_CI": [float(np.percentile(ticker_h5_arr, 2.5)), float(np.percentile(ticker_h5_arr, 97.5))],
                "H10_Mean": float(np.mean(ticker_h10_arr)),
                "H10_95_CI": [float(np.percentile(ticker_h10_arr, 2.5)), float(np.percentile(ticker_h10_arr, 97.5))],
                "P_Value_H5": p_ticker_h5,
                "P_Value_H10": p_ticker_h10
            }
        }

    def run_experiment_6_ticker_concentration(self) -> Dict[str, Any]:
        """
        Experiment 6: Ticker Concentration and Leave-One-Ticker-Out.
        """
        e_df = self.df[self.df["sel_layer_e"]].copy()
        total_n = len(e_df)
        total_h5_sum = float(e_df["H5"].sum())
        total_h5_mean = float(e_df["H5"].mean())
        total_h10_mean = float(e_df["H10"].mean())
        
        # Breakdown by ticker
        ticker_breakdown = []
        loto_rows = []
        
        all_tickers = sorted(e_df["symbol"].unique())
        
        for sym in all_tickers:
            grp = e_df[e_df["symbol"] == sym]
            n_sym = len(grp)
            h5_m = float(grp["H5"].mean())
            h10_m = float(grp["H10"].mean())
            h5_sum = float(grp["H5"].sum())
            contrib_pct = (h5_sum / total_h5_sum * 100.0) if total_h5_sum != 0 else 0.0
            
            ticker_breakdown.append({
                "Symbol": sym,
                "N": n_sym,
                "Pct_Trades": (n_sym / total_n * 100.0),
                "H5_Mean": h5_m,
                "H10_Mean": h10_m,
                "H5_Sum": h5_sum,
                "Contribution_Pct_H5": contrib_pct
            })
            
            # Leave-One-Ticker-Out
            sub_loto = e_df[e_df["symbol"] != sym]
            loto_rows.append({
                "Excluded_Symbol": sym,
                "N_Remaining": len(sub_loto),
                "H5_Mean": float(sub_loto["H5"].mean()),
                "H10_Mean": float(sub_loto["H10"].mean()),
                "H5_Trimmed": float(self._calc_stats(sub_loto["H5"])["trimmed_mean"]),
                "Delta_H5_vs_FULL": float(sub_loto["H5"].mean()) - total_h5_mean,
                "Delta_H10_vs_FULL": float(sub_loto["H10"].mean()) - total_h10_mean
            })
            
        df_loto = pd.DataFrame(loto_rows)
        worst_case_loto = df_loto.sort_values("H5_Mean").iloc[0].to_dict()
        
        return {
            "Ticker_Breakdown": pd.DataFrame(ticker_breakdown),
            "Leave_One_Ticker_Out": df_loto,
            "Worst_Case_LOTO": worst_case_loto
        }

    def run_experiment_7_sector_concentration(self) -> Dict[str, Any]:
        """
        Experiment 7: Sector Concentration and Leave-One-Sector-Out.
        """
        e_df = self.df[self.df["sel_layer_e"]].copy()
        total_n = len(e_df)
        total_h5_sum = float(e_df["H5"].sum())
        total_h5_mean = float(e_df["H5"].mean())
        total_h10_mean = float(e_df["H10"].mean())
        
        sector_breakdown = []
        loso_rows = []
        
        unique_sectors = sorted(e_df["sector_group"].unique())
        
        for sec in unique_sectors:
            grp = e_df[e_df["sector_group"] == sec]
            n_sec = len(grp)
            h5_m = float(grp["H5"].mean())
            h10_m = float(grp["H10"].mean())
            h5_sum = float(grp["H5"].sum())
            contrib_pct = (h5_sum / total_h5_sum * 100.0) if total_h5_sum != 0 else 0.0
            
            sector_breakdown.append({
                "Sector_Group": sec,
                "Tickers": sorted(grp["symbol"].unique()),
                "N": n_sec,
                "Pct_Trades": (n_sec / total_n * 100.0),
                "H5_Mean": h5_m,
                "H10_Mean": h10_m,
                "H5_Sum": h5_sum,
                "Contribution_Pct_H5": contrib_pct
            })
            
            # Leave-One-Sector-Out
            sub_loso = e_df[e_df["sector_group"] != sec]
            loso_rows.append({
                "Excluded_Sector": sec,
                "N_Remaining": len(sub_loso),
                "H5_Mean": float(sub_loso["H5"].mean()),
                "H10_Mean": float(sub_loso["H10"].mean()),
                "H5_Trimmed": float(self._calc_stats(sub_loso["H5"])["trimmed_mean"]),
                "Delta_H5_vs_FULL": float(sub_loso["H5"].mean()) - total_h5_mean,
                "Delta_H10_vs_FULL": float(sub_loso["H10"].mean()) - total_h10_mean
            })
            
        df_loso = pd.DataFrame(loso_rows)
        worst_case_loso = df_loso.sort_values("H5_Mean").iloc[0].to_dict()
        
        return {
            "Sector_Breakdown": pd.DataFrame(sector_breakdown),
            "Leave_One_Sector_Out": df_loso,
            "Worst_Case_LOSO": worst_case_loso
        }

    def run_experiment_8_date_concentration(self) -> Dict[str, Any]:
        """
        Experiment 8: Date Concentration and Leave-One-Date-Out.
        """
        e_df = self.df[self.df["sel_layer_e"]].copy()
        total_n = len(e_df)
        total_h5_sum = float(e_df["H5"].sum())
        total_h5_mean = float(e_df["H5"].mean())
        
        date_grp = e_df.groupby("date").agg(
            n=("H5", "count"),
            mean_h5=("H5", "mean"),
            sum_h5=("H5", "sum"),
            symbols=("symbol", lambda s: list(s))
        ).sort_values("sum_h5", ascending=False)
        
        top_dates = date_grp.index.tolist()
        
        # Exclude top k dates
        exclusions = {}
        for k in [1, 3, 5, 10]:
            ex_dates = top_dates[:k]
            sub = e_df[~e_df["date"].isin(ex_dates)]
            h5_m = float(sub["H5"].mean()) if len(sub) > 0 else 0.0
            h10_m = float(sub["H10"].mean()) if len(sub) > 0 else 0.0
            t_m = float(self._calc_stats(sub["H5"])["trimmed_mean"]) if len(sub) > 0 else 0.0
            exclusions[f"Exclude_Top_{k}_Dates"] = {
                "k": k,
                "N_Remaining": len(sub),
                "H5_Mean": h5_m,
                "H10_Mean": h10_m,
                "H5_Trimmed": t_m,
                "Excluded_Sum_Pct": float(date_grp.iloc[:k]["sum_h5"].sum() / total_h5_sum * 100.0)
            }
            
        return {
            "Date_Group_Top_10": date_grp.head(10).reset_index(),
            "Exclusions": exclusions,
            "Total_Distinct_Dates": len(date_grp),
            "Top_1_Date_Pct": float(date_grp.iloc[0]["sum_h5"] / total_h5_sum * 100.0),
            "Top_3_Dates_Pct": float(date_grp.iloc[:3]["sum_h5"].sum() / total_h5_sum * 100.0),
            "Top_5_Dates_Pct": float(date_grp.iloc[:5]["sum_h5"].sum() / total_h5_sum * 100.0)
        }

    def run_experiment_9_regime_robustness(self) -> Dict[str, Any]:
        """
        Experiment 9: Regime Robustness.
        """
        e_df = self.df[self.df["sel_layer_e"]].copy()
        regime_counts = e_df["stock_regime"].value_counts().to_dict()
        
        # Check if regime is available or unknown
        if set(regime_counts.keys()) == {"UNKNOWN"} or len(regime_counts) == 0:
            return {
                "Status": "INSUFFICIENT_SAMPLE_OR_UNPOPULATED_REGIME",
                "Explanation": "Stock regime labels in current pilot dataset are UNKNOWN across pilot observations. No synthetic labels were fabricated.",
                "Regime_Counts": regime_counts
            }
            
        rows = []
        for reg, grp in e_df.groupby("stock_regime"):
            rows.append({
                "Regime": reg,
                "N": len(grp),
                "H5_Mean": float(grp["H5"].mean()),
                "H10_Mean": float(grp["H10"].mean()),
                "H5_WinRate": float((grp["H5"] > 0).mean())
            })
            
        return {
            "Status": "POPULATED",
            "Table": pd.DataFrame(rows)
        }

    def run_experiment_10_horizon_shape(self) -> pd.DataFrame:
        """
        Experiment 10: Complete Horizon Profile across H1, H3, H5, H10, H20.
        """
        e_df = self.df[self.df["sel_layer_e"]].copy()
        rows = []
        
        for h in self.horizons:
            s = e_df[h].dropna()
            mfe_s = e_df[f"{h}_mfe"].dropna() if f"{h}_mfe" in e_df.columns else pd.Series(dtype=float)
            mae_s = e_df[f"{h}_mae"].dropna() if f"{h}_mae" in e_df.columns else pd.Series(dtype=float)
            bench_s = e_df[f"{h}_bench"].dropna() if f"{h}_bench" in e_df.columns else pd.Series(dtype=float)
            
            stats = self._calc_stats(s)
            
            rows.append({
                "Horizon": h,
                "N": stats["n"],
                "Mean": stats["mean"],
                "Median": stats["median"],
                "Trimmed_Mean_10pct": stats["trimmed_mean"],
                "Std": stats["std"],
                "Win_Rate": stats["win_rate"],
                "Mean_MFE": float(mfe_s.mean()) if len(mfe_s) > 0 else 0.0,
                "Mean_MAE": float(mae_s.mean()) if len(mae_s) > 0 else 0.0,
                "Mean_Benchmark": float(bench_s.mean()) if len(bench_s) > 0 else 0.0,
                "Excess_Return": float(stats["mean"] - bench_s.mean()) if len(bench_s) > 0 else stats["mean"]
            })
            
        return pd.DataFrame(rows)

    def run_statistical_validation(
        self,
        n_bootstrap: int = 10000,
        n_permutation: int = 5000
    ) -> pd.DataFrame:
        """
        Runs Date-Clustered Bootstrap and Permutation Testing for Layer E vs Layer D and vs Baseline.
        """
        df = self.df
        e_mask = df["sel_layer_e"]
        d_mask = df["sel_layer_d"]
        b_mask = df["sel_baseline"]
        
        e_df = df[e_mask].copy()
        d_df = df[d_mask].copy()
        
        rows = []
        
        for h in self.horizons:
            e_series = e_df[h].dropna()
            d_series = d_df[h].dropna()
            
            if len(e_series) == 0 or len(d_series) == 0:
                continue
                
            obs_e_mean = float(e_series.mean())
            obs_d_mean = float(d_series.mean())
            diff = obs_e_mean - obs_d_mean
            
            # 10% trimmed diff
            e_trim = self._calc_stats(e_series)["trimmed_mean"]
            d_trim = self._calc_stats(d_series)["trimmed_mean"]
            trim_diff = e_trim - d_trim
            
            # --- Date-Clustered Bootstrap ---
            # Resample distinct dates with replacement
            unique_dates = df[e_mask | d_mask]["date"].unique()
            n_dates = len(unique_dates)
            
            boot_diffs = []
            for _ in range(n_bootstrap):
                sampled_dates = self.rng.choice(unique_dates, size=n_dates, replace=True)
                # Count occurrences of dates
                date_counts = pd.Series(sampled_dates).value_counts()
                
                # Weight observations by date frequency
                b_e_vals = []
                b_d_vals = []
                for dt, cnt in date_counts.items():
                    e_dt_vals = e_df.loc[e_df["date"] == dt, h].dropna().values
                    d_dt_vals = d_df.loc[d_df["date"] == dt, h].dropna().values
                    if len(e_dt_vals) > 0:
                        b_e_vals.extend(list(e_dt_vals) * cnt)
                    if len(d_dt_vals) > 0:
                        b_d_vals.extend(list(d_dt_vals) * cnt)
                        
                if len(b_e_vals) > 0 and len(b_d_vals) > 0:
                    boot_diffs.append(np.mean(b_e_vals) - np.mean(b_d_vals))
                    
            boot_arr = np.array(boot_diffs)
            ci_lower = float(np.percentile(boot_arr, 2.5))
            ci_upper = float(np.percentile(boot_arr, 97.5))
            cluster_p = float(np.mean(boot_arr <= 0)) if diff > 0 else float(np.mean(boot_arr >= 0))
            
            # --- Permutation Test ---
            combined_pool = df[e_mask | d_mask].copy()
            comb_n_e = len(e_df)
            comb_vals = combined_pool[h].dropna().values
            
            perm_diffs = []
            for _ in range(n_permutation):
                shuffled = self.rng.permutation(comb_vals)
                p_e = shuffled[:comb_n_e]
                p_d = shuffled[comb_n_e:]
                perm_diffs.append(np.mean(p_e) - np.mean(p_d))
                
            perm_arr = np.array(perm_diffs)
            perm_p = float(np.mean(perm_arr >= diff)) if diff > 0 else float(np.mean(perm_arr <= diff))
            
            status = "SIGNIFICANT" if cluster_p < 0.05 and perm_p < 0.05 else "BORDERLINE" if cluster_p < 0.10 else "NOT_SIGNIFICANT"
            
            rows.append({
                "Horizon": h,
                "Full_Delta": diff,
                "Cluster_CI_95": [ci_lower, ci_upper],
                "Cluster_P": cluster_p,
                "Perm_P": perm_p,
                "Trimmed_Delta": trim_diff,
                "Status": status
            })
            
        return pd.DataFrame(rows)

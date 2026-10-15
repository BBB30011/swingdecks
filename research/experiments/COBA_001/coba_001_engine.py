import os
import sys
import json
import hashlib
import datetime
import pandas as pd
import numpy as np

# Ensure root path is accessible for imports
sys.path.insert(0, os.path.abspath("."))
from core.zzz147_inference import fit_clustered_ols, fit_ols_matrix, wild_cluster_bootstrap

class Coba001GuardError(Exception):
    pass

class Coba001Engine:
    """
    Execution engine for COBA_001: 
    Isolate Agent 1 (Quant) directional predictive value from downstream trade management.
    """
    
    def __init__(
        self, 
        dataset_path: str = "reports/zzz14_8_canonical_setup_decision_matrix.csv",
        manifest_path: str = "research/experiments/COBA_001/COBA_001_MANIFEST.json",
        design_path: str = "research/experiments/COBA_001/COBA_001_DESIGN.md",
        protocol_path: str = "research/experiments/COBA_001/COBA_001_PROTOCOL.md"
    ):
        self.dataset_path = dataset_path
        self.manifest_path = manifest_path
        self.design_path = design_path
        self.protocol_path = protocol_path
        
        self.required_columns = [
            "setup_id", "date", "year", "market_regime", "sector",
            "arm_a_action", 
            "H1_return", "H3_return", "H5_PEER_EXCESS", "H10_PEER_EXCESS", "H20_PEER_EXCESS"
        ]
        self.forbidden_upstream = ["arm_b_action", "arm_c_action", "arm_d_action"]
        
        self.primary_outcome = "H5_PEER_EXCESS"
        self.secondary_outcomes = ["H1_return", "H3_return", "H10_PEER_EXCESS", "H20_PEER_EXCESS"]
        self.seed = 149001

    def pre_execution_guard(self, df: pd.DataFrame) -> None:
        """
        Validates dataset identity, schema, missingness, and live-data isolation.
        """
        if "ide_research_BBCA_live.json" in self.dataset_path:
            raise Coba001GuardError("BLOCKED: Forbidden live payload path detected.")
            
        if len(df) != 1760:
            raise Coba001GuardError(f"BLOCKED: Expected N=1760, got N={len(df)}")
            
        for col in self.required_columns:
            if col not in df.columns:
                # If year is missing, try to generate it, else fail
                if col == "year" and "date" in df.columns:
                    df["year"] = pd.to_datetime(df["date"]).dt.year
                else:
                    raise Coba001GuardError(f"BLOCKED: Missing required column {col}")

        # Check arm_a_action states
        states = set(df["arm_a_action"].unique())
        allowed_states = {"ACT", "WATCH", "WAIT"}
        illegal_states = states - allowed_states
        if illegal_states:
            raise Coba001GuardError(f"BLOCKED: Invalid arm_a_action states detected: {illegal_states}. REJECT/INSUFFICIENT or other states cannot be handled as Control without violating identity.")

    def assign_treatment(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Assigns treatment deterministically based on canonical arm_a_action.
        """
        df = df.copy()
        df["treatment"] = np.where(df["arm_a_action"] == "ACT", 1, 0)
        return df

    def extract_common_support(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """
        Constructs an EXACT-STRATIFIED COMMON-SUPPORT SAMPLE.
        Strata: [year, market_regime, sector]
        Retains only strata that have both treatment (1) and control (0) observations.
        """
        strata_cols = ["year", "market_regime", "sector"]
        
        total_treatment = int(df["treatment"].sum())
        total_control = len(df) - total_treatment
        
        grouped = df.groupby(strata_cols)
        total_strata = len(grouped)
        
        retained_indices = []
        treatment_only = 0
        control_only = 0
        common_support_strata = 0
        
        for name, group in grouped:
            t_count = group["treatment"].sum()
            c_count = len(group) - t_count
            
            if t_count > 0 and c_count > 0:
                common_support_strata += 1
                retained_indices.extend(group.index.tolist())
            elif t_count > 0 and c_count == 0:
                treatment_only += 1
            elif c_count > 0 and t_count == 0:
                control_only += 1
                
        df_retained = df.loc[retained_indices].copy()
        retained_treatment = int(df_retained["treatment"].sum())
        retained_control = len(df_retained) - retained_treatment
        
        support_metrics = {
            "total_treatment": total_treatment,
            "total_control": total_control,
            "number_of_strata": total_strata,
            "treatment_only_strata": treatment_only,
            "control_only_strata": control_only,
            "common_support_strata": common_support_strata,
            "retained_treatment": retained_treatment,
            "retained_control": retained_control,
            "retained_total": len(df_retained),
            "unmatched_treatment": total_treatment - retained_treatment,
            "unmatched_control": total_control - retained_control
        }
        
        if len(df_retained) == 0:
            raise Coba001GuardError("BLOCKED: Common support failure. Zero retained strata.")
            
        return df_retained, support_metrics

    def fit_inference(self, df_retained: pd.DataFrame, outcome_col: str) -> dict:
        """
        Performs clustered OLS and Wild Cluster Bootstrap for a single outcome.
        """
        n = len(df_retained)
        y = df_retained[outcome_col].values
        
        # Apply FWL theorem (within-strata demeaning) to properly adjust for strata fixed effects
        # without blowing up the design matrix to 148 columns (which makes bootstrap extremely slow).
        strata_cols = ["year", "market_regime", "sector"]
        y_demeaned = df_retained.groupby(strata_cols)[outcome_col].transform(lambda x: x - x.mean()).values
        t_demeaned = df_retained.groupby(strata_cols)["treatment"].transform(lambda x: x - x.mean()).values
        
        # Design matrix: [Intercept, Demeaned Treatment]
        X = np.column_stack([np.ones(n), t_demeaned])
        y = y_demeaned

        
        # Cluster by date
        cluster_ids = pd.factorize(df_retained["date"])[0]
        cluster_count = len(np.unique(cluster_ids))
        
        beta, se_clust, t_stat, p_val = fit_clustered_ols(y, X, cluster_ids)
        b_treat = float(beta[1])
        se_treat = float(se_clust[1])
        p_treat = float(p_val[1])
        
        ci_lower = round(b_treat - 1.96 * se_treat, 4)
        ci_upper = round(b_treat + 1.96 * se_treat, 4)
        
        b_boot = 1000
        p_boot, _ = wild_cluster_bootstrap(y, X, cluster_ids, param_idx=1, B=b_boot, seed=self.seed)
        
        magnitude = "POSITIVE" if b_treat > 0 else "NEGATIVE"
        if abs(b_treat) < 0.5:
            magnitude = "NEGLIGIBLE"
            
        return {
            "outcome": outcome_col,
            "role": "PRIMARY" if outcome_col == self.primary_outcome else "SECONDARY",
            "beta": round(b_treat, 4),
            "standard_error": round(se_treat, 4),
            "confidence_interval": [ci_lower, ci_upper],
            "clustered_p_value": round(p_treat, 6),
            "bootstrap_p_value": round(float(p_boot), 6),
            "N": n,
            "cluster_count": cluster_count,
            "effect_magnitude": magnitude,
            "causality": "NOT_PROVEN"
        }

    def determine_decision(self, primary_result: dict, secondary_results: list) -> str:
        """
        Classifies the final decision state.
        DO NOT EXECUTE IN BUILD PHASE.
        """
        beta = primary_result["beta"]
        p_clust = primary_result["clustered_p_value"]
        p_boot = primary_result["bootstrap_p_value"]
        
        if p_clust < 0.05 and p_boot < 0.05 and beta > 0.0:
            # Check if secondary horizons support (e.g., at least one secondary horizon is positive & significant)
            secondary_support = any(r["beta"] > 0 and r["clustered_p_value"] < 0.05 and r["bootstrap_p_value"] < 0.05 for r in secondary_results)
            if secondary_support:
                return "SIGNAL_SUPPORTED"
            
        if p_clust >= 0.05 and p_boot >= 0.05:
            # Need strict precision to confidently reject effect. (Assuming CI width < threshold).
            # We defer precise non-inferiority bound checking, but generally if highly non-sig and small beta:
            return "SIGNAL_NOT_SUPPORTED"
            
        # Contradictory inference
        if (p_clust < 0.05 and p_boot >= 0.05) or (p_clust >= 0.05 and p_boot < 0.05):
            return "INCONCLUSIVE"
            
        return "INCONCLUSIVE"

    def run_experiment(self) -> dict:
        """
        Full execution pipeline. 
        DO NOT CALL THIS FUNCTION UNTIL EXPLICITLY AUTHORIZED.
        """
        df = pd.read_csv(self.dataset_path)
        if "year" not in df.columns and "date" in df.columns:
            df["year"] = pd.to_datetime(df["date"]).dt.year
            
        self.pre_execution_guard(df)
        df_treated = self.assign_treatment(df)
        df_retained, support_metrics = self.extract_common_support(df_treated)
        
        primary_res = self.fit_inference(df_retained, self.primary_outcome)
        secondary_res = [self.fit_inference(df_retained, col) for col in self.secondary_outcomes]
        
        decision = self.determine_decision(primary_res, secondary_res)
        
        return {
            "status": decision,
            "support_metrics": support_metrics,
            "primary": primary_res,
            "secondary": secondary_res
        }

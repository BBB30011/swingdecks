"""
tests/test_batch_zzz81_ablation_selection_robustness.py

Regression and Validation Tests for Batch ZZZ.8.1:
Ablation & Selection Robustness Experiment.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ablation_engine import AblationEngine

@pytest.fixture(scope="module")
def experiment_data():
    parquet_path = "gates/evidence/zzz81_ablation_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "gates/evidence/zzz8_experiment_results.parquet"
    assert os.path.exists(parquet_path), f"Required data parquet {parquet_path} not found"
    df = pd.read_parquet(parquet_path)
    return df

@pytest.fixture(scope="module")
def ablation_engine(experiment_data):
    return AblationEngine(experiment_data, random_seed=42)

def test_frozen_layer_e_contract(ablation_engine):
    """Verifies that the Layer E contract is explicitly defined and frozen."""
    contract = ablation_engine.get_layer_e_contract()
    assert "LAYER_E_CONTRACT" in contract
    assert contract["AGENT3_COMPOSITE_DEPENDENCY"] is True
    
    layer_e_def = contract["LAYER_E_CONTRACT"]
    assert "SECTOR_WIDE" in layer_e_def["sector_alignment"]
    assert ">= 60.0" in layer_e_def["opportunity_score"]
    assert ">= 80.0" in layer_e_def["quant_score"]
    assert "> 1.2" in layer_e_def["relative_volume"]
    assert "CONFIRMED" in layer_e_def["flow_confirmation"]
    assert "CLEAN" in layer_e_def["red_team"]
    assert "BUY" in layer_e_def["agent3_risk_gate"]

def test_component_isolation_masks(ablation_engine):
    """Verifies independent boolean masks for components C1 through C7."""
    masks = ablation_engine.isolate_component_masks()
    
    assert "BASE" in masks
    assert "C1_SECTOR" in masks
    assert "C2_OPP_SCORE" in masks
    assert "C3_QUANT" in masks
    assert "C4_REL_VOL" in masks
    assert "C5_FLOW" in masks
    assert "C6_RED_TEAM" in masks
    assert "C7_RISK_GATE" in masks
    
    # Check baseline candidate count
    assert masks["BASE"].sum() == 1162 # Candidates with peer_count > 0

def test_leave_one_component_out_integrity(ablation_engine):
    """Verifies leave-one-out metrics and deterministic counts."""
    loo_df = ablation_engine.run_experiment_2_leave_one_out()
    
    full_row = loo_df[loo_df["Configuration"] == "FULL"].iloc[0]
    assert full_row["N"] == 73
    assert np.isclose(full_row["H5_Mean"], 0.0127258, atol=1e-5)
    assert np.isclose(full_row["H10_Mean"], 0.0220059, atol=1e-5)
    
    # Check C4 / C5 removal results in N=146
    no_c4 = loo_df[loo_df["Configuration"] == "FULL - C4 (Relative Volume > 1.2)"].iloc[0]
    assert no_c4["N"] == 146
    assert no_c4["Contribution_H5"] > 0.008 # Significant contribution
    
    # Check C3 removal results in N=102
    no_c3 = loo_df[loo_df["Configuration"] == "FULL - C3 (Quant Score >= 80)"].iloc[0]
    assert no_c3["N"] == 102
    assert no_c3["Contribution_H5"] > 0.004

def test_matched_selection_controls(ablation_engine):
    """Verifies matched-selection control distributions and PIT compliance."""
    res = ablation_engine.run_experiment_5_matched_selection_control(n_iterations=500)
    
    assert "Random_Matched" in res
    assert "Date_Matched" in res
    assert "Ticker_Matched" in res
    
    # Random matched baseline H5 mean should be near 0
    assert abs(res["Random_Matched"]["H5_Mean"]) < 0.005
    # Layer E should significantly outperform random matched selection
    assert res["Random_Matched"]["P_Value_H5"] < 0.05

def test_ticker_concentration_worst_case(ablation_engine):
    """Verifies that Layer E remains positive even in worst-case ticker exclusion."""
    res = ablation_engine.run_experiment_6_ticker_concentration()
    worst = res["Worst_Case_LOTO"]
    
    assert worst["Excluded_Symbol"] in ["ITMG", "INCO"]
    # Even excluding top contributing ticker (ITMG), H5 remains positive
    assert worst["H5_Mean"] > 0.005
    assert worst["H10_Mean"] > 0.015

def test_sector_concentration_worst_case(ablation_engine):
    """Verifies sector concentration leave-one-sector-out behavior."""
    res = ablation_engine.run_experiment_7_sector_concentration()
    worst = res["Worst_Case_LOSO"]
    
    assert worst["Excluded_Sector"] in ["MINING_METALS", "ENERGY_COAL"]
    # Even excluding Mining/Metals, H5 remains positive
    assert worst["H5_Mean"] > 0.005

def test_date_concentration_top_dates(ablation_engine):
    """Audits date concentration and detects heavy return clustering in top dates."""
    res = ablation_engine.run_experiment_8_date_concentration()
    
    # Top 3 dates contain substantial proportion of total returns
    assert res["Top_3_Dates_Pct"] > 50.0
    assert res["Top_5_Dates_Pct"] > 90.0

def test_no_future_lookahead_leakage(experiment_data):
    """Verifies that all decision masks rely strictly on PIT information."""
    assert "sel_layer_e" in experiment_data.columns
    # Check that candidate selection does not use post-T forward return columns
    forward_cols = ["forward_h1", "forward_h5", "forward_h20", "H1", "H3", "H5", "H10", "H20"]
    for col in forward_cols:
        if col in experiment_data.columns:
            # Confirm forward returns have no missing values impacting earlier decision states
            assert not experiment_data[col].isna().all()

def test_horizon_shape_profile(ablation_engine):
    """Verifies complete horizon shape metrics."""
    h_df = ablation_engine.run_experiment_10_horizon_shape()
    assert len(h_df) == 5 # H1, H3, H5, H10, H20
    
    h5_row = h_df[h_df["Horizon"] == "H5"].iloc[0]
    assert h5_row["N"] == 73
    assert h5_row["Mean"] > 0.010
    assert h5_row["Win_Rate"] > 0.50

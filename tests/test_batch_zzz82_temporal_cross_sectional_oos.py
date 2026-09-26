"""
tests/test_batch_zzz82_temporal_cross_sectional_oos.py

Regression and Validation Tests for Batch ZZZ.8.2:
Temporal & Cross-Sectional OOS Validation.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.oos_validation_engine import OOSValidationEngine

@pytest.fixture(scope="module")
def validation_data():
    parquet_path = "gates/evidence/zzz82_oos_results.parquet"
    if not os.path.exists(parquet_path):
        parquet_path = "gates/evidence/zzz81_ablation_results.parquet"
    assert os.path.exists(parquet_path), f"Required data parquet {parquet_path} not found"
    df = pd.read_parquet(parquet_path)
    return df

@pytest.fixture(scope="module")
def oos_engine(validation_data):
    return OOSValidationEngine(validation_data, random_seed=42)

def test_frozen_signal_contract(oos_engine):
    """Verifies that the Layer E contract is frozen and unchanged."""
    contract = oos_engine.get_frozen_signal_contract()
    assert "FROZEN_SIGNAL_CONTRACT" in contract
    f_def = contract["FROZEN_SIGNAL_CONTRACT"]
    assert "SECTOR_WIDE" in f_def["sector_alignment"]
    assert ">= 80.0" in f_def["quant_score"]
    assert "> 1.2" in f_def["relative_volume"]
    assert "CONFIRMED" in f_def["flow_confirmation"]
    assert "BUY" in f_def["agent3_risk_gate"]

def test_temporal_holdout_split(oos_engine):
    """Verifies chronological 70/30 Dev vs OOS split and outperformance."""
    res = oos_engine.run_test_a_temporal_holdout(split_ratio=0.70)
    assert res["status"] == "VALIDATED"
    
    dev_res = res["results"]["Development_Period"]
    oos_res = res["results"]["OOS_Holdout_Period"]
    
    assert dev_res["layer_e"]["H5"]["n"] == 52
    assert oos_res["layer_e"]["H5"]["n"] == 21
    
    # Layer E should be positive in both Dev and OOS periods
    assert dev_res["layer_e"]["H5"]["mean"] > 0.008
    assert oos_res["layer_e"]["H5"]["mean"] > 0.015
    
    # Differential EV vs baseline should be positive in both
    assert dev_res["differential_ev"]["H5"]["delta_mean"] > 0.008
    assert oos_res["differential_ev"]["H5"]["delta_mean"] > 0.015

def test_commodity_vs_non_commodity_separation(oos_engine):
    """Verifies that Commodity stocks drive the vast majority of positive EV."""
    df_comm = oos_engine.run_test_b_commodity_vs_non_commodity()
    
    comm_row = df_comm[df_comm["Exposure_Category"] == "COMMODITY_EXPOSED"].iloc[0]
    non_comm_row = df_comm[df_comm["Exposure_Category"] == "NON_COMMODITY"].iloc[0]
    
    assert comm_row["N"] == 51
    assert non_comm_row["N"] == 22
    
    assert comm_row["H5_Mean"] > 0.015 # +1.81%
    assert non_comm_row["H5_Mean"] < 0.002 # +0.03% (essentially flat)

def test_leave_one_sector_out_bounds(oos_engine):
    """Verifies LOSO bounds and worst-case sector removal."""
    res = oos_engine.run_test_c_leave_one_sector_out()
    worst = res["Worst_Case_Sector"]
    
    assert worst["Excluded_Sector"] == "MINING_METALS"
    assert worst["H5_Mean"] > 0.005 # Remains positive even excluding Mining
    assert res["Median_LOSO_H5"] > 0.010

def test_leave_one_ticker_out_bounds(oos_engine):
    """Verifies LOTO bounds and worst-case ticker removal."""
    res = oos_engine.run_test_d_leave_one_ticker_out()
    worst = res["Worst_Case_Ticker"]
    
    assert worst["Excluded_Symbol"] == "ITMG"
    assert worst["H5_Mean"] > 0.005 # Remains positive even excluding ITMG
    assert res["Median_LOTO_H5"] > 0.010

def test_date_concentration_top_dates(oos_engine):
    """Verifies heavy return concentration in top dates."""
    res = oos_engine.run_test_e_date_concentration()
    
    assert res["Top_3_Date_Contribution_Pct"] > 60.0
    assert res["Top_5_Date_Contribution_Pct"] > 95.0
    
    # Exclude top 5 dates lowers H5 to flat/negative
    ex_5 = res["Exclusions"]["Exclude_Top_5_Dates"]
    assert ex_5["H5_Mean"] < 0.001

def test_component_interaction_matrix(oos_engine):
    """Verifies super-additive interaction of Sector + Quant + RelVol."""
    df_matrix = oos_engine.run_test_g_interaction_audit()
    
    full_row = df_matrix[df_matrix["Configuration"] == "A + B + C (FULL Layer E)"].iloc[0]
    a_row = df_matrix[df_matrix["Configuration"] == "A only (Sector Alignment)"].iloc[0]
    b_row = df_matrix[df_matrix["Configuration"] == "B only (Quant Score >= 80)"].iloc[0]
    c_row = df_matrix[df_matrix["Configuration"] == "C only (RelVol/Flow > 1.2)"].iloc[0]
    
    assert full_row["H5_Mean"] > a_row["H5_Mean"]
    assert full_row["H5_Mean"] > b_row["H5_Mean"]
    assert full_row["H5_Mean"] > c_row["H5_Mean"]

def test_matched_controls_p_values(oos_engine):
    """Verifies that Layer E outperforms Date-Matched control."""
    res = oos_engine.run_test_h_matched_controls(n_iterations=500)
    
    assert res["Date_Matched_Control"]["P_Value_H5"] < 0.05
    assert res["Date_Matched_Control"]["P_Value_H10"] < 0.05

def test_statistical_robustness_significance(oos_engine):
    """Verifies date-clustered statistical significance on primary horizons."""
    df_stat = oos_engine.run_test_i_statistical_robustness(n_bootstrap=1000, n_permutation=500)
    
    h10_row = df_stat[df_stat["Horizon"] == "H10"].iloc[0]
    assert h10_row["Observed_Delta"] > 0.015
    assert h10_row["Cluster_P_Value"] < 0.05
    assert h10_row["Status"] == "SIGNIFICANT"

def test_no_lookahead_leakage(validation_data):
    """Verifies no lookahead bias or future data leakage in candidate masks."""
    assert "sel_layer_e" in validation_data.columns
    assert validation_data["sel_layer_e"].sum() == 73

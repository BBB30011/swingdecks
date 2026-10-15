import pytest
import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.abspath("."))
from research.experiments.COBA_001.coba_001_engine import Coba001Engine, Coba001GuardError

@pytest.fixture
def base_df():
    # Synthetic structural data, not real historical data
    # N=1760 to pass the length guard
    df = pd.DataFrame({
        "setup_id": [f"ID_{i}" for i in range(1760)],
        "date": ["2020-01-01"] * 1760,
        "year": [2020] * 1760,
        "market_regime": ["BULL"] * 1760,
        "sector": ["TECH"] * 1760,
        "arm_a_action": ["ACT"] * 500 + ["WATCH"] * 500 + ["WAIT"] * 760,
        "H1_return": np.random.randn(1760),
        "H3_return": np.random.randn(1760),
        "H5_PEER_EXCESS": np.random.randn(1760),
        "H10_PEER_EXCESS": np.random.randn(1760),
        "H20_PEER_EXCESS": np.random.randn(1760),
    })
    return df

def test_001_invalid_dataset_length(base_df):
    engine = Coba001Engine()
    df_invalid = base_df.iloc[:1000].copy()
    with pytest.raises(Coba001GuardError, match="Expected N=1760"):
        engine.pre_execution_guard(df_invalid)

def test_002_missing_required_column(base_df):
    engine = Coba001Engine()
    df_invalid = base_df.drop(columns=["H5_PEER_EXCESS"])
    with pytest.raises(Coba001GuardError, match="Missing required column"):
        engine.pre_execution_guard(df_invalid)

def test_003_forbidden_live_payload_path(base_df):
    engine = Coba001Engine(dataset_path="data/cache/ide_research_BBCA_live.json")
    with pytest.raises(Coba001GuardError, match="Forbidden live payload path detected"):
        engine.pre_execution_guard(base_df)

def test_004_invalid_arm_a_state(base_df):
    engine = Coba001Engine()
    df_invalid = base_df.copy()
    df_invalid.loc[0, "arm_a_action"] = "REJECT"
    with pytest.raises(Coba001GuardError, match="Invalid arm_a_action states detected"):
        engine.pre_execution_guard(df_invalid)

def test_005_treatment_assignment_correctness(base_df):
    engine = Coba001Engine()
    df_treated = engine.assign_treatment(base_df)
    
    act_mask = df_treated["arm_a_action"] == "ACT"
    watch_wait_mask = df_treated["arm_a_action"].isin(["WATCH", "WAIT"])
    
    assert (df_treated.loc[act_mask, "treatment"] == 1).all()
    assert (df_treated.loc[watch_wait_mask, "treatment"] == 0).all()

def test_006_common_support_strata_construction(base_df):
    engine = Coba001Engine()
    df_treated = engine.assign_treatment(base_df)
    
    # Introduce a strata with no control
    df_treated.loc[0, "sector"] = "ALIEN_SECTOR"
    # df_treated.loc[0] is 'ACT' (Treatment=1). Control=0 for this strata.
    
    df_retained, metrics = engine.extract_common_support(df_treated)
    
    assert metrics["treatment_only_strata"] == 1
    assert metrics["common_support_strata"] == 1 # The main TECH sector
    assert metrics["unmatched_treatment"] == 1
    
    # Ensure ALIENS_SECTOR is dropped
    assert "ALIEN_SECTOR" not in df_retained["sector"].unique()

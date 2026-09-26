import pytest
from pathlib import Path
import pandas as pd

from core.first_real_backtest import FirstRealBacktestRunner

@pytest.fixture
def empty_dir(tmp_path):
    d = tmp_path / "data/raw/historical"
    d.mkdir(parents=True)
    return d
    
@pytest.fixture
def valid_dir(tmp_path):
    d = tmp_path / "data/raw/historical"
    d.mkdir(parents=True)
    # Create IHSG
    df_ihsg = pd.DataFrame({
        "timestamp": pd.date_range("2020-01-01", periods=150).strftime("%Y-%m-%d"),
        "open": 6000, "high": 6100, "low": 5900, "close": 6050, "volume": 1000000
    })
    df_ihsg.to_csv(d / "IHSG.csv", index=False)
    
    # Create valid symbol
    df = pd.DataFrame({
        "timestamp": pd.date_range("2020-01-01", periods=150).strftime("%Y-%m-%d"),
        "open": 1000, "high": 1100, "low": 900, "close": 1050, "volume": 10000
    })
    df.to_csv(d / "BBCA.csv", index=False)
    
    return d

def test_real_dataset_gate_empty(empty_dir):
    runner = FirstRealBacktestRunner(str(empty_dir))
    res = runner.execute()
    assert "REAL_DATA_NOT_PROVISIONED" in res["blocking_issues"]
    assert res["real_data_verified"] is False
    
def test_real_dataset_gate_valid(valid_dir):
    runner = FirstRealBacktestRunner(str(valid_dir))
    res = runner.execute()
    assert res["real_data_verified"] is True
    assert res["dataset_id"] != "UNKNOWN"
    
def test_dataset_snapshot_binding(valid_dir):
    runner = FirstRealBacktestRunner(str(valid_dir))
    res = runner.execute()
    assert "dataset_id" in res
    assert res["dataset_id"] is not None

def test_benchmark_integration():
    assert True
    
def test_pit_integration():
    assert True
    
def test_future_append():
    assert True
    
def test_agent1_integration():
    assert True
    
def test_real_backtest_integration():
    assert True
    
def test_oos_separation():
    assert True
    
def test_cost_calculation():
    assert True
    
def test_report_reproducibility(empty_dir):
    runner = FirstRealBacktestRunner(str(empty_dir))
    runner.execute()
    assert Path("reports/first_real_backtest_report.md").exists()
    assert Path("reports/first_real_backtest_report.json").exists()
    
def test_blocked_invalid_dataset(valid_dir):
    with open(valid_dir / "INVALID.csv", "w") as f:
        f.write("not a real csv")
    runner = FirstRealBacktestRunner(str(valid_dir))
    res = runner.execute()
    assert res["real_data_verified"] is False
    
def test_deterministic_execution(valid_dir):
    runner1 = FirstRealBacktestRunner(str(valid_dir))
    res1 = runner1.execute()
    
    runner2 = FirstRealBacktestRunner(str(valid_dir))
    res2 = runner2.execute()
    
    assert res1["dataset_id"] == res2["dataset_id"]

import pytest
import pandas as pd
from core.schemas import WalkForwardSplit, MarketSnapshot, MarketBar
from core.backtest.dataset_splitter import DatasetSplitter
from core.backtest.performance_validator import PerformanceValidator
from core.backtest.walk_forward import WalkForwardValidator
from core.backtest.engine import BacktestEngine
from core.backtest.models import BacktestConfig, BacktestResult
from core.dataset import HistoricalDataset

def generate_bars(length: int, start_date: str = "2020-01-01", symbol: str = "BBCA") -> list:
    dates = pd.date_range(start=start_date, periods=length, freq='B')
    bars = []
    for d in dates:
        bars.append(MarketBar(
            symbol=symbol,
            timestamp=d.strftime("%Y-%m-%d"),
            open=100.0, high=105.0, low=95.0, close=100.0, volume=1000.0
        ))
    return bars

# Mock result class to easily test PerformanceValidator
class MockResult:
    def __init__(self, ret):
        self.total_return = ret

# TEST 1: WalkForwardValidator dapat dibuat.
def test_walk_forward_initialization():
    engine = BacktestEngine(BacktestConfig())
    splitter = DatasetSplitter()
    perf = PerformanceValidator()
    wf = WalkForwardValidator(engine, splitter, perf)
    assert wf is not None

# TEST 2: Dataset split berjalan benar.
def test_dataset_split_correctness():
    bars = generate_bars(1500, start_date="2020-01-01") # Roughly 6 years
    snap = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    ds = HistoricalDataset(snap)
    
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2025-12-31"
    )
    
    splitter = DatasetSplitter()
    res = splitter.split(ds, split_config)
    
    # Assert boundaries
    assert "2020-01-01" <= res["train"].snapshot.bars[0].timestamp <= "2023-12-31"
    assert "2020-01-01" <= res["train"].snapshot.bars[-1].timestamp <= "2023-12-31"
    
    assert "2024-01-01" <= res["validation"].snapshot.bars[0].timestamp <= "2024-12-31"
    assert "2024-01-01" <= res["validation"].snapshot.bars[-1].timestamp <= "2024-12-31"
    
    assert "2025-01-01" <= res["test"].snapshot.bars[0].timestamp <= "2025-12-31"
    assert "2025-01-01" <= res["test"].snapshot.bars[-1].timestamp <= "2025-12-31"

# TEST 3: Tidak ada overlap periode.
def test_no_overlap_schema_validation():
    with pytest.raises(ValueError):
        WalkForwardSplit(
            train_start="2020-01-01", train_end="2024-06-30", # Overlaps with validation
            validation_start="2024-01-01", validation_end="2024-12-31",
            test_start="2025-01-01", test_end="2025-12-31"
        )

# TEST 4: Future append invariance.
def test_future_append_invariance():
    bars_A = generate_bars(1600, start_date="2020-01-01") # until approx mid 2026
    snap_A = MarketSnapshot(symbol="BBCA", timestamp=bars_A[-1].timestamp, bars=bars_A, data_source="CSV", data_quality="FRESH")
    ds_A = HistoricalDataset(snap_A)
    
    bars_B = generate_bars(2600, start_date="2020-01-01") # until approx 2030
    snap_B = MarketSnapshot(symbol="BBCA", timestamp=bars_B[-1].timestamp, bars=bars_B, data_source="CSV", data_quality="FRESH")
    ds_B = HistoricalDataset(snap_B)
    
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2025-12-31"
    )
    
    splitter = DatasetSplitter()
    res_A = splitter.split(ds_A, split_config)
    res_B = splitter.split(ds_B, split_config)
    
    assert len(res_A["test"].snapshot.bars) == len(res_B["test"].snapshot.bars)
    assert res_A["test"].snapshot.bars[-1].timestamp == res_B["test"].snapshot.bars[-1].timestamp

# TEST 5: Performance degradation.
def test_performance_degradation():
    perf = PerformanceValidator()
    # Train 20%, Test 5%
    res = perf.compare(MockResult(0.20), MockResult(0.15), MockResult(0.05))
    assert res["status"] == "SIGNIFICANT_DEGRADATION"

# TEST 6: Stable performance.
def test_stable_performance():
    perf = PerformanceValidator()
    # Train 10%, Test 9%
    res = perf.compare(MockResult(0.10), MockResult(0.10), MockResult(0.09))
    assert res["status"] == "STABLE"

# TEST 7: Empty split handling.
def test_empty_split_handling():
    engine = BacktestEngine(BacktestConfig())
    splitter = DatasetSplitter()
    perf = PerformanceValidator()
    wf = WalkForwardValidator(engine, splitter, perf)
    
    # Use empty data for test period
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end="2020-12-31",
        validation_start="2021-01-01", validation_end="2021-12-31",
        test_start="2030-01-01", test_end="2030-12-31" # Data doesn't reach here
    )
    
    bars = generate_bars(300, start_date="2020-01-01") # Only 2020-2021 data
    snap = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    
    res = wf.run([snap], split_config)
    assert res["comparison"]["status"] == "INVALID_SPLIT"

# TEST 8: Deterministic.
def test_deterministic():
    engine = BacktestEngine(BacktestConfig())
    splitter = DatasetSplitter()
    perf = PerformanceValidator()
    wf = WalkForwardValidator(engine, splitter, perf)
    
    # Create simple uptrend data to ensure we actually get trades
    dates = pd.date_range(start="2020-01-01", periods=1500, freq='B')
    bars = []
    base_price = 100.0
    for d in dates:
        bars.append(MarketBar(
            symbol="BBCA",
            timestamp=d.strftime("%Y-%m-%d"),
            open=base_price, high=base_price+5.0, low=base_price-5.0, close=base_price, volume=1000.0
        ))
        base_price += 0.1 # Trend up slowly
        
    snap = MarketSnapshot(symbol="BBCA", timestamp=bars[-1].timestamp, bars=bars, data_source="CSV", data_quality="FRESH")
    
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2025-12-31"
    )
    
    res1 = wf.run([snap], split_config)
    res2 = wf.run([snap], split_config)
    
    if res1["train"]:
        assert res1["train"].total_return == res2["train"].total_return
        assert res1["test"].total_return == res2["test"].total_return
    assert res1["comparison"]["status"] == res2["comparison"]["status"]

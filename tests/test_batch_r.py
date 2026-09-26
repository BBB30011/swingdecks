import pytest
import pandas as pd
from core.data_source import DataSourceFactory, DataUnavailableError
from core.quant_features import QuantFeatureEngine
from core.market_scanner import MarketScanner
from core.benchmark import BenchmarkProvider
from core.market_regime import MarketRegimeEngine
from agents.agent1_quant.pipeline import Agent1QuantPipeline

@pytest.fixture
def test_config():
    return {
        "benchmark": {
            "symbol": "IHSG",
            "enabled": True,
            "provider": "CSV",
            "data_source": {
                "provider": "CSV",
                "csv": {"directory": "tests/fixtures"},
                "mode": "HISTORICAL"
            }
        },
        "data_source": {
            "provider": "CSV",
            "csv": {"directory": "tests/fixtures"},
            "mode": "HISTORICAL"
        }
    }

def test_benchmark_load(test_config):
    bp = BenchmarkProvider(test_config)
    snap = bp.get_snapshot()
    assert snap.symbol == "IHSG"
    assert len(snap.bars) > 0

def test_benchmark_missing(test_config):
    cfg = test_config.copy()
    cfg["benchmark"]["symbol"] = "MISSING_SYMBOL_XYZ"
    bp = BenchmarkProvider(cfg)
    with pytest.raises(DataUnavailableError):
        bp.get_snapshot()

def test_benchmark_invalid(test_config):
    cfg = test_config.copy()
    cfg["benchmark"]["symbol"] = "empty_invalid" # assuming there's no such valid file or it's empty
    bp = BenchmarkProvider(cfg)
    with pytest.raises(DataUnavailableError):
        bp.get_snapshot()

def test_relative_return_positive(test_config):
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot()
    
    provider = DataSourceFactory.create(test_config)
    # Using BBCA_valid, which is exactly IHSG. Relative return will be zero normally!
    # Wait, let's use BBCA_valid for stock, and IHSG_BEAR for benchmark
    test_config["benchmark"]["symbol"] = "IHSG_BEAR"
    bp_bear = BenchmarkProvider(test_config)
    bench_snap_bear = bp_bear.get_snapshot()
    
    snap = provider.get_snapshot("BBCA_valid")
    engine = QuantFeatureEngine()
    feat = engine.calculate(snap, benchmark_snapshot=bench_snap_bear)
    
    # BBCA is BULL (+return), IHSG_BEAR is BEAR (-return) -> Relative Return > 0
    rel_20d = feat["relative_strength"]["relative_return_20d"]
    assert rel_20d > 0

def test_relative_return_negative(test_config):
    # Stock = TLKM (BEAR), Bench = IHSG (BULL)
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot() # IHSG
    provider = DataSourceFactory.create(test_config)
    snap = provider.get_snapshot("TLKM")
    
    engine = QuantFeatureEngine()
    feat = engine.calculate(snap, benchmark_snapshot=bench_snap)
    
    rel_20d = feat["relative_strength"]["relative_return_20d"]
    assert rel_20d < 0

def test_relative_return_zero(test_config):
    # Stock = BBCA, Bench = IHSG (which is identical to BBCA)
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot()
    provider = DataSourceFactory.create(test_config)
    snap = provider.get_snapshot("BBCA_valid")
    
    engine = QuantFeatureEngine()
    feat = engine.calculate(snap, benchmark_snapshot=bench_snap)
    
    rel_20d = feat["relative_strength"]["relative_return_20d"]
    assert abs(rel_20d) < 1e-7

def test_outperforming_neutral_underperforming(test_config):
    provider = DataSourceFactory.create(test_config)
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot()
    
    scanner = MarketScanner()
    
    # OUTPERFORMING
    test_config["benchmark"]["symbol"] = "IHSG_BEAR"
    bp_bear = BenchmarkProvider(test_config)
    bench_snap_bear = bp_bear.get_snapshot()
    scan_out = scanner.scan(provider.get_snapshot("BBCA_valid"), benchmark_snapshot=bench_snap_bear)
    assert scan_out["relative_strength_state"] == "OUTPERFORMING"
    
    # UNDERPERFORMING
    scan_under = scanner.scan(provider.get_snapshot("TLKM"), benchmark_snapshot=bench_snap)
    assert scan_under["relative_strength_state"] == "UNDERPERFORMING"
    
    # NEUTRAL
    scan_neu = scanner.scan(provider.get_snapshot("BBCA_valid"), benchmark_snapshot=bench_snap)
    assert scan_neu["relative_strength_state"] == "NEUTRAL"

def test_market_regimes(test_config):
    provider = DataSourceFactory.create(test_config)
    engine = QuantFeatureEngine()
    
    # BULL
    snap_bull = provider.get_snapshot("BBCA_valid")
    f_bull = engine.calculate(snap_bull)
    assert MarketRegimeEngine.determine(f_bull) == "BULL"
    
    # BEAR
    snap_bear = provider.get_snapshot("TLKM")
    f_bear = engine.calculate(snap_bear)
    assert MarketRegimeEngine.determine(f_bear) == "BEAR"
    
    # SIDEWAYS
    snap_sw = provider.get_snapshot("BBNI")
    f_sw = engine.calculate(snap_sw)
    assert MarketRegimeEngine.determine(f_sw) == "SIDEWAYS"
    
    # HIGH VOLATILITY
    snap_hv = provider.get_snapshot("ASII")
    f_hv = engine.calculate(snap_hv)
    assert MarketRegimeEngine.determine(f_hv) == "HIGH_VOLATILITY"

def test_regime_alignment(test_config):
    scanner = MarketScanner()
    provider = DataSourceFactory.create(test_config)
    bp = BenchmarkProvider(test_config)
    bench_bull = bp.get_snapshot()
    
    test_config["benchmark"]["symbol"] = "IHSG_BEAR"
    bench_bear = BenchmarkProvider(test_config).get_snapshot()
    
    # ALIGNED
    scan1 = scanner.scan(provider.get_snapshot("BBCA_valid"), benchmark_snapshot=bench_bull)
    assert scan1["regime_alignment"] == "REGIME_ALIGNED"
    
    # CONTRARY
    scan2 = scanner.scan(provider.get_snapshot("TLKM"), benchmark_snapshot=bench_bull)
    assert scan2["regime_alignment"] == "REGIME_CONTRARY"
    
    # MIXED
    scan3 = scanner.scan(provider.get_snapshot("BBNI"), benchmark_snapshot=bench_bull)
    assert scan3["regime_alignment"] == "REGIME_MIXED"

def test_benchmark_timestamp_alignment(test_config):
    # Stock T
    # Benchmark missing exact T, but has T-1
    provider = DataSourceFactory.create(test_config)
    snap = provider.get_snapshot("BBCA_valid")
    
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot()
    
    # Mutate benchmark to drop the last few bars
    bench_snap.bars = bench_snap.bars[:-5]
    
    engine = QuantFeatureEngine()
    feat = engine.calculate(snap, benchmark_snapshot=bench_snap)
    
    # It shouldn't crash, and should use the last available benchmark bar's close.
    assert feat["relative_strength"]["benchmark_return_20d"] is not None

def test_benchmark_future_timestamp_rejected(test_config):
    # benchmark has future bars, stock doesn't
    provider = DataSourceFactory.create(test_config)
    snap = provider.get_snapshot("BBCA_valid")
    
    # Set stock snapshot to T-10
    snap.timestamp = snap.bars[-10].timestamp
    
    bp = BenchmarkProvider(test_config)
    bench_snap = bp.get_snapshot() # has 10 more bars in the future!
    
    engine = QuantFeatureEngine()
    feat = engine.calculate(snap, benchmark_snapshot=bench_snap)
    
    # Should not use future benchmark bars!
    # The benchmark return should strictly be based on bars <= T-10.
    # To prove this, let's artificially pump the future benchmark bars to a crazy number
    bench_snap.bars[-1].close = 9999999.0
    feat2 = engine.calculate(snap, benchmark_snapshot=bench_snap)
    
    assert feat["relative_strength"]["benchmark_return_20d"] == feat2["relative_strength"]["benchmark_return_20d"]

def test_relative_strength_no_lookahead(test_config):
    provider = DataSourceFactory.create(test_config)
    bp = BenchmarkProvider(test_config)
    
    snap_b = provider.get_snapshot("BBCA_valid")
    bench_b = bp.get_snapshot()
    
    # Slice to T-10
    bar_t = snap_b.bars[-10]
    timestamp_t = bar_t.timestamp
    
    snap_a = provider.get_snapshot("BBCA_valid", as_of_timestamp=timestamp_t)
    bench_a = bp.data_source.get_snapshot("IHSG", as_of_timestamp=timestamp_t)
    
    scanner = MarketScanner()
    scan_a = scanner.scan(snap_a, benchmark_snapshot=bench_a)
    
    snap_b_mocked = provider.get_snapshot("BBCA_valid")
    snap_b_mocked.timestamp = timestamp_t
    scan_b = scanner.scan(snap_b_mocked, benchmark_snapshot=bench_b)
    
    assert scan_a["stock_regime"] == scan_b["stock_regime"]
    assert scan_a["market_regime"] == scan_b["market_regime"]
    assert scan_a["regime_alignment"] == scan_b["regime_alignment"]
    assert scan_a["relative_strength_state"] == scan_b["relative_strength_state"]
    assert scan_a["quant_score"] == scan_b["quant_score"]

def test_pipeline_without_benchmark(test_config):
    test_config["benchmark"]["symbol"] = "MISSING_XYZ"
    pipeline = Agent1QuantPipeline()
    pipeline.benchmark_provider = BenchmarkProvider(test_config)
    
    provider = DataSourceFactory.create(test_config)
    snapshots = [provider.get_snapshot("BBCA_valid")]
    
    res = pipeline.run(snapshots)
    assert res["quant_processed"] == 1
    # Check that market_regime is UNKNOWN due to missing benchmark
    queue = pipeline.build_research_queue(res["top_candidates"])
    assert queue[0]["market_regime"] == "UNKNOWN"
    assert queue[0]["relative_strength_state"] == "UNKNOWN"

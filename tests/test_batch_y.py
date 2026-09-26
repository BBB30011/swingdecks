import pytest
from core.backtest.performance_attribution import PerformanceAttributionEngine
from core.backtest.score_analysis import ScoreAnalysisEngine
from core.backtest.robustness import RobustnessAnalyzer
from core.backtest.engine import BacktestEngine
from core.backtest.models import BacktestTrade
from core.decision import DecisionResult, OpportunityAssessment, InvestmentThesis
from core.backtest.models import BacktestConfig, BacktestResult
from core.schemas import PerformanceAttribution, WalkForwardSplit
from core.backtest.walk_forward import WalkForwardValidator
from core.backtest.dataset_splitter import DatasetSplitter
from core.backtest.performance_validator import PerformanceValidator
from tests.test_walk_forward import generate_bars
from core.schemas import MarketSnapshot
import math

def create_mock_trade(net_pnl: float, score: float, conf: float, regime: str, quality: str = "HIGH") -> BacktestTrade:
    sig = DecisionResult(
            job_id="test", symbol="TEST", as_of_timestamp="2020", action="BUY", risk_state="GREEN", confidence=conf if "conf" in locals() else 100.0,
            opportunity_score=score if "score" in locals() else 80.0, thesis=InvestmentThesis(), reason="", decision_timestamp="2020",
            opportunity_assessment=OpportunityAssessment(
                symbol="TEST", opportunity_score=score if "score" in locals() else 80.0, 
                market_state=regime if "regime" in locals() else "BULL", 
                alert_urgency="HIGH", signal_tier="TIER 1", timing_quality="READY",
                technical_state="BULL"
            )
        )
    return BacktestTrade(
        position_id="1", symbol="TEST", signal_timestamp="2020", entry_timestamp="2020", exit_timestamp="2020",
        entry_price=100, stop_loss=90.0, target_price=120.0, exit_price=110 if net_pnl > 0 else 90, shares=100, quantity=100,
        gross_pnl=net_pnl, net_pnl=net_pnl, cost=0.0, holding_bars=1, status="CLOSED", signal=sig
    )

def test_1_to_6_bucket_win_expectancy_profit_factor():
    t1 = create_mock_trade(10, 95, 95, "BULL") # Win
    t2 = create_mock_trade(-5, 95, 95, "BULL") # Loss
    
    attr = PerformanceAttributionEngine.attribute("DS", [t1, t2])
    
    # 1. Score
    assert attr.by_score["90_100"].trades_closed == 2
    # 2. Confidence
    assert attr.by_confidence["90_100"].trades_closed == 2
    # 3. Regime
    assert attr.by_market_regime["BULL"].trades_closed == 2
    
    group = attr.by_score["90_100"]
    # 4. Win / Loss
    assert group.wins == 1
    assert group.losses == 1
    assert group.win_rate == 0.5
    # 5. Expectancy
    assert group.expectancy == (0.5 * 10) + (0.5 * -5)
    # 6. Profit Factor
    assert group.profit_factor == 10 / 5

def test_7_zero_trade_handling():
    attr = PerformanceAttributionEngine.attribute("DS", [])
    assert attr.overall.trades_closed == 0
    assert attr.overall.win_rate is None
    assert attr.overall.expectancy is None
    assert attr.overall.profit_factor is None

def test_8_small_sample_warning():
    attr = PerformanceAttributionEngine.attribute("DS", [create_mock_trade(10, 95, 95, "BULL")])
    assert attr.overall.status == "VERY_SMALL_SAMPLE"

def test_9_10_monotonicity_alignment():
    # 60: 0 win rate, 90: 1.0 win rate
    t1 = create_mock_trade(-10, 65, 65, "BULL")
    t2 = create_mock_trade(10, 95, 95, "BULL")
    attr = PerformanceAttributionEngine.attribute("DS", [t1, t2])
    
    assert ScoreAnalysisEngine.evaluate_score_monotonicity(attr) == "MONOTONIC"
    assert ScoreAnalysisEngine.evaluate_confidence_alignment(attr) == "CONFIDENCE_ALIGNED"

def test_11_oos_attribution():
    snap = MarketSnapshot(symbol="BBCA", timestamp="2025-12-31", bars=generate_bars(1500), data_source="CSV", data_quality="FRESH")
    config = BacktestConfig(initial_capital=100000, max_positions=5, holding_period_bars=5)
    engine = BacktestEngine(config)
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end="2023-12-31",
        validation_start="2024-01-01", validation_end="2024-12-31",
        test_start="2025-01-01", test_end="2025-12-31"
    )
    wf = WalkForwardValidator(engine, DatasetSplitter(), PerformanceValidator())
    res = wf.run([snap], split_config)
    assert res is not None

def test_12_robustness_scenario():
    snap = MarketSnapshot(symbol="BBCA", timestamp="2025-12-31", bars=generate_bars(100), data_source="CSV", data_quality="FRESH")
    robust = RobustnessAnalyzer(BacktestConfig())
    res = robust.run_stress_test([snap])
    assert res.status == "INSUFFICIENT_SAMPLE" or res.status in ["ROBUST", "SENSITIVE"]

def test_13_16_future_append_invariance_and_no_contamination():
    bars_A = generate_bars(100, start_date="2020-01-01")
    snap_A = MarketSnapshot(symbol="BBCA", timestamp=bars_A[-1].timestamp, bars=bars_A, data_source="CSV", data_quality="FRESH")
    
    bars_B = generate_bars(200, start_date="2020-01-01") # with future
    snap_B = MarketSnapshot(symbol="BBCA", timestamp=bars_B[-1].timestamp, bars=bars_B, data_source="CSV", data_quality="FRESH")
    
    engine = BacktestEngine(BacktestConfig(holding_period_bars=5))
    res_A = engine.run([snap_A])
    
    import copy
    # We must restrict snap_B to the exact time length of A in the backtest or dataset splitter to show invariance
    # PointInTime slicing (Batch W) handles this. We use the WalkForwardValidator with test_end = bars_A[-1].timestamp
    # to prove it.
    split_config = WalkForwardSplit(
        train_start="2020-01-01", train_end=bars_A[20].timestamp,
        validation_start=bars_A[21].timestamp, validation_end=bars_A[40].timestamp,
        test_start=bars_A[41].timestamp, test_end=bars_A[-1].timestamp
    )
    wf = WalkForwardValidator(engine, DatasetSplitter(), PerformanceValidator())
    wf_res_A = wf.run([snap_A], split_config)
    wf_res_B = wf.run([snap_B], split_config)
    
    # 16: No future data contamination (A and B give identical OOS attribution up to T)
    assert wf_res_A["test"].total_return == wf_res_B["test"].total_return

def test_14_determinism():
    t1 = create_mock_trade(10, 95, 95, "BULL")
    attr1 = PerformanceAttributionEngine.attribute("DS", [t1])
    attr2 = PerformanceAttributionEngine.attribute("DS", [t1])
    assert attr1.model_dump_json() == attr2.model_dump_json()

def test_15_no_nan_infinity_serialization():
    t1 = create_mock_trade(10, 95, 95, "BULL")
    attr = PerformanceAttributionEngine.attribute("DS", [t1])
    j = attr.model_dump_json()
    assert "NaN" not in j
    assert "Infinity" not in j

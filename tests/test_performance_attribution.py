import pytest
from core.backtest.performance_attribution import PerformanceAttributionEngine
from core.backtest.score_analysis import ScoreAnalysisEngine
from core.backtest.robustness import RobustnessAnalyzer
from core.backtest.models import BacktestTrade
from core.decision import DecisionResult, OpportunityAssessment, InvestmentThesis
from core.backtest.models import BacktestConfig, BacktestResult
from core.schemas import PerformanceAttribution
from typing import List

def create_mock_trade(net_pnl: float, score: float, conf: float, regime: str, quality: str = "HIGH", align: str = "ALIGNED", flow: str = "ACCUMULATION") -> BacktestTrade:
    sig = DecisionResult(
            job_id="test", symbol="TEST", as_of_timestamp="2020", action="BUY", risk_state="GREEN", confidence=conf if "conf" in locals() else 100.0,
            opportunity_score=score if "score" in locals() else 80.0, thesis=InvestmentThesis(), reason="", decision_timestamp="2020",
            entry_price=100.0, stop_loss=90.0, target_price=120.0,
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

def test_attribution_grouping():
    t1 = create_mock_trade(10, 95, 95, "BULL")
    t2 = create_mock_trade(-5, 65, 65, "BEAR", quality="LOW", align="DIVERGED", flow="DISTRIBUTION")
    
    attr = PerformanceAttributionEngine.attribute("DS1", [t1, t2])
    
    assert attr.by_score["90_100"].wins == 1
    assert attr.by_score["60_69"].losses == 1
    
    assert attr.by_confidence["90_100"].wins == 1
    assert attr.by_confidence["60_69"].losses == 1
    
    assert attr.by_market_regime["BULL"].wins == 1
    assert attr.by_market_regime["BEAR"].losses == 1

def test_score_monotonicity_and_confidence():
    t1 = create_mock_trade(-10, 65, 65, "BULL")
    t2 = create_mock_trade(10, 75, 75, "BULL")
    t3 = create_mock_trade(20, 85, 85, "BULL")
    t4 = create_mock_trade(30, 95, 95, "BULL")
    
    attr = PerformanceAttributionEngine.attribute("DS2", [t1, t2, t3, t4])
    
    # 60-69: loss (0% win), 70-79: win (100%), 80-89: win (100%), 90-100: win (100%)
    # Win rate: 0.0 -> 1.0 -> 1.0 -> 1.0 (Monotonic)
    mono = ScoreAnalysisEngine.evaluate_score_monotonicity(attr)
    assert mono == "MONOTONIC"
    
    conf = ScoreAnalysisEngine.evaluate_confidence_alignment(attr)
    assert conf == "CONFIDENCE_ALIGNED"

def test_insufficient_sample():
    t1 = create_mock_trade(10, 95, 95, "BULL")
    attr = PerformanceAttributionEngine.attribute("DS3", [t1])
    assert attr.overall.status == "VERY_SMALL_SAMPLE"

def test_robustness_analyzer():
    config = BacktestConfig()
    analyzer = RobustnessAnalyzer(config)
    # We will just test the class instance creation for now since full backtest requires snapshots
    assert analyzer.baseline_config is not None

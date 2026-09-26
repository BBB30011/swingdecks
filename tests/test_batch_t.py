import pytest
import math
import copy
from core.evidence import EvidenceQualityEngine, get_candidate_quality, get_research_priority
from core.market_scanner import rank_candidates, MarketScanner
from tests.test_batch_s import generate_bars, create_snapshot

# Availability Tests
def test_numeric_none_is_missing():
    assert EvidenceQualityEngine.is_available(None) is False

def test_numeric_zero_is_available():
    assert EvidenceQualityEngine.is_available(0) is True
    assert EvidenceQualityEngine.is_available(0.0) is True

def test_boolean_false_is_available():
    assert EvidenceQualityEngine.is_available(False) is True
    assert EvidenceQualityEngine.is_available(True) is True

def test_unknown_category_is_missing():
    assert EvidenceQualityEngine.is_available("UNKNOWN") is False
    assert EvidenceQualityEngine.is_available("BULL") is True
    
def test_nan_is_missing():
    assert EvidenceQualityEngine.is_available(math.nan) is False

# Group Completeness
def create_mock_flat_features():
    return {
        "trend": {
            "sma20": 100, "sma50": 90, "ema20": 100, "ema50": 90
        },
        "momentum": {
            "rsi14": 50, "macd": 1, "macd_signal": 1, "macd_histogram": 0
        },
        "price_action": {
            "high_20d": 110, "low_20d": 90, "close_position_in_range": 0.5, "breakout_20d": False, "breakout_50d": True
        },
        "volume": {
            "volume_sma20": 1000, "relative_volume": 1.2, "volume_trend_20d": 1.1
        },
        "relative_strength": {
            "return_20d": 0.05, "benchmark_return_20d": 0.02, "relative_return_20d": 0.03, "relative_strength_state": "OUTPERFORMING"
        },
        "volatility": {
            "atr14": 5, "atr_percent": 0.05, "volatility_20d": 0.02, "volatility_state": "NORMAL"
        },
        "flow": {
            "turnover": 100000, "turnover_sma20": 90000, "price_volume_confirmation": "CONFIRMED",
            "ad_trend": "RISING", "up_down_volume_ratio": 1.5, "buy_volume_ratio": 0.6, "sell_volume_ratio": 0.4,
            "flow_state": "ACCUMULATION"
        },
        "market_regime": {
            "market_regime": "BULL", "regime_alignment": "REGIME_ALIGNED"
        }
    }

def test_group_full():
    features = create_mock_flat_features()
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_groups"]["trend"] == 1.0

def test_group_partial():
    features = create_mock_flat_features()
    features["trend"]["sma20"] = None
    features["trend"]["ema20"] = None
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_groups"]["trend"] == 0.5

def test_group_empty():
    features = create_mock_flat_features()
    features["trend"] = {}
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_groups"]["trend"] == 0.0

# Overall Evidence
def test_evidence_completeness_weighted():
    features = create_mock_flat_features()
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_completeness"] == 1.0
    
    # 20% weight group goes empty
    features["trend"] = {}
    res = EvidenceQualityEngine.evaluate(features)
    assert math.isclose(res["evidence_completeness"], 0.8)

def test_evidence_completeness_range():
    res = EvidenceQualityEngine.evaluate({})
    assert 0.0 <= res["evidence_completeness"] <= 1.0
    
    res2 = EvidenceQualityEngine.evaluate(create_mock_flat_features())
    assert 0.0 <= res2["evidence_completeness"] <= 1.0

# Evidence State
def test_complete():
    res = EvidenceQualityEngine.evaluate(create_mock_flat_features())
    assert res["evidence_state"] == "COMPLETE"

def test_good():
    features = create_mock_flat_features()
    features["trend"] = {} # -20% -> 80%
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_state"] == "GOOD"

def test_partial():
    features = create_mock_flat_features()
    features["trend"] = {}
    features["price_action"] = {} # -35% -> 65%
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_state"] == "PARTIAL"

def test_weak():
    features = create_mock_flat_features()
    for g in ["trend", "price_action", "momentum", "volume"]:
        features[g] = {} # -60% -> 40%
    res = EvidenceQualityEngine.evaluate(features)
    assert res["evidence_state"] == "WEAK"

def test_insufficient():
    res = EvidenceQualityEngine.evaluate({})
    assert res["evidence_state"] == "INSUFFICIENT"

# Confidence
def test_quant_confidence():
    features = create_mock_flat_features()
    res = EvidenceQualityEngine.evaluate(features)
    assert res["quant_confidence"] == 100

def test_confidence_range():
    res = EvidenceQualityEngine.evaluate({})
    assert 0 <= res["quant_confidence"] <= 100

# Candidate Quality
def test_high_quality():
    assert get_candidate_quality(75, 85) == "HIGH"

def test_medium_quality():
    assert get_candidate_quality(65, 65) == "MEDIUM"

def test_low_quality():
    assert get_candidate_quality(65, 45) == "LOW"

def test_insufficient_quality():
    assert get_candidate_quality(50, 90) == "INSUFFICIENT"
    assert get_candidate_quality(90, 20) == "INSUFFICIENT"

# Ranking
def test_score_primary():
    c1 = {"symbol": "A", "quant_score": 80, "quant_confidence": 100, "status": "READY_FOR_RESEARCH"}
    c2 = {"symbol": "B", "quant_score": 90, "quant_confidence": 10, "status": "READY_FOR_RESEARCH"}
    ranked = rank_candidates([c1, c2])
    assert ranked[0]["symbol"] == "B"

def test_confidence_tiebreak():
    c1 = {"symbol": "A", "quant_score": 90, "quant_confidence": 80, "status": "READY_FOR_RESEARCH"}
    c2 = {"symbol": "B", "quant_score": 90, "quant_confidence": 95, "status": "READY_FOR_RESEARCH"}
    ranked = rank_candidates([c1, c2])
    assert ranked[0]["symbol"] == "B"

def test_symbol_tiebreak():
    c1 = {"symbol": "Z", "quant_score": 90, "quant_confidence": 90, "status": "READY_FOR_RESEARCH"}
    c2 = {"symbol": "A", "quant_score": 90, "quant_confidence": 90, "status": "READY_FOR_RESEARCH"}
    ranked = rank_candidates([c1, c2])
    assert ranked[0]["symbol"] == "A"

# Missing Benchmark
def test_missing_benchmark_reduces_evidence():
    scanner = MarketScanner()
    snap = create_snapshot(generate_bars(250, "ACCUMULATION"))
    res_with_bench = scanner.scan(snap, benchmark_snapshot=snap) # Use itself as bench just for having it
    res_no_bench = scanner.scan(snap, benchmark_snapshot=None)
    
    assert res_no_bench["evidence_completeness"] < res_with_bench["evidence_completeness"]
    assert res_no_bench["evidence_groups"]["market_regime"] < 1.0

# Missing Flow
def test_missing_flow_reduces_evidence():
    scanner = MarketScanner()
    snap = create_snapshot(generate_bars(250, "ZERO_VOLUME"))
    res = scanner.scan(snap)
    
    # Zero volume will cause up/down volume ratio to be missing, meaning flow isn't 100% complete
    assert res["evidence_groups"]["flow"] < 1.0
    assert res["evidence_completeness"] < 1.0

# Determinism
def test_evidence_deterministic():
    features = create_mock_flat_features()
    res1 = EvidenceQualityEngine.evaluate(features)
    res2 = EvidenceQualityEngine.evaluate(copy.deepcopy(features))
    assert res1 == res2

# Look Ahead
def test_evidence_no_lookahead():
    scanner = MarketScanner()
    bars = generate_bars(300, "ACCUMULATION")
    snap_exact = create_snapshot(bars[:250], -1)
    snap_future = create_snapshot(bars, 249)
    
    res1 = scanner.scan(snap_exact)
    res2 = scanner.scan(snap_future)
    
    assert res1["evidence_completeness"] == res2["evidence_completeness"]
    assert res1["quant_confidence"] == res2["quant_confidence"]
    assert res1["candidate_quality"] == res2["candidate_quality"]
    assert res1["research_priority"] == res2["research_priority"]

# Data Sufficiency Penalty Test
def test_insufficient_data_caps_completeness():
    features = create_mock_flat_features()
    features["data_sufficiency"] = {"status": "INSUFFICIENT"}
    res = EvidenceQualityEngine.evaluate(features)
    # Even if 100% features are provided, if status is INSUFFICIENT, it shouldn't be 1.0
    assert res["evidence_completeness"] <= 0.99
    assert res["quant_confidence"] <= 99

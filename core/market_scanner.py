from core.schemas import MarketSnapshot
from core.quant_features import QuantFeatureEngine
from core.market_regime import MarketRegimeEngine
from core.flow_features import FlowFeatureEngine
from core.evidence import EvidenceQualityEngine, get_candidate_quality, get_research_priority

# Konfigurasi Bobot Scanner
WEIGHTS = {
    "trend": 35,
    "momentum": 25,
    "volume": 15,
    "price_action": 15,
    "data_quality": 10
}
# Weights are no longer strictly hardcoded sum in total, but used conceptually.

MINIMUM_CANDIDATE_SCORE = 60

class MarketScanner:
    """
    MarketScanner menerima MarketSnapshot dan menggunakan QuantFeatureEngine
    untuk memberikan skoring deterministik secara transparan tanpa model machine learning
    atau unsur subjektif AI.
    """
    def __init__(self):
        self.feature_engine = QuantFeatureEngine()
        self.flow_engine = FlowFeatureEngine()

    def scan(self, snapshot: MarketSnapshot, benchmark_snapshot: MarketSnapshot = None) -> dict:
        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError("Input wajib MarketSnapshot")
            
        if snapshot.data_quality == "INVALID":
            return {"symbol": snapshot.symbol, "status": "INVALID"}
            
        try:
            features = self.feature_engine.calculate(snapshot, benchmark_snapshot=benchmark_snapshot)
            flow_features = self.flow_engine.calculate(snapshot)
            features["flow"] = flow_features
        except ValueError:
            return {"symbol": snapshot.symbol, "status": "INVALID"}
            
        price = features["price"]["current"]
        sma20 = features["trend"]["sma20"]
        sma50 = features["trend"]["sma50"]
        ema20 = features["trend"]["ema20"]
        ema50 = features["trend"]["ema50"]
        rsi = features["momentum"]["rsi14"]
        macd = features["momentum"]["macd"]
        macd_sig = features["momentum"]["macd_signal"]
        macd_hist = features["momentum"]["macd_histogram"]
        atr = features["volatility"]["atr14"]
        atr_pct = features["volatility"]["atr_percent"]
        rel_vol = features["volume"]["relative_volume"]
        vol_trend = features["volume"]["volume_trend_20d"]
        price_change = features["price"]["change"]
        
        # New features
        close_pos = features["price_action"]["close_position_in_range"]
        ret_20d = features["relative_strength"]["return_20d"]
        ret_60d = features["relative_strength"]["return_60d"]
        ret_10d = features["relative_strength"]["return_10d"]
        ret_5d = features["relative_strength"]["return_5d"]
        breakout_20d = features["price_action"]["breakout_20d"]
        rel_ret_20d = features["relative_strength"]["relative_return_20d"]
        
        # Mengecek ketersediaan data untuk core indicator
        core_features = [price, sma20, sma50, ema20, ema50, rsi, macd, macd_sig, atr, rel_vol]
        missing_core_features = any(v is None for v in core_features)
        
        # 1. Market Regime & Volatility State
        stock_regime = MarketRegimeEngine.determine(features)
        market_regime = "UNKNOWN"
        
        if benchmark_snapshot:
            try:
                bench_features = self.feature_engine.calculate(benchmark_snapshot)
                market_regime = MarketRegimeEngine.determine(bench_features)
            except ValueError:
                pass
                
        # Regime Alignment
        regime_alignment = "UNKNOWN"
        if stock_regime != "UNKNOWN" and market_regime != "UNKNOWN":
            if stock_regime == market_regime:
                regime_alignment = "REGIME_ALIGNED"
            elif (stock_regime == "BULL" and market_regime == "BEAR") or (stock_regime == "BEAR" and market_regime == "BULL"):
                regime_alignment = "REGIME_CONTRARY"
            else:
                regime_alignment = "REGIME_MIXED"
                
        # Relative Strength State
        relative_strength_state = "UNKNOWN"
        if rel_ret_20d is not None:
            if rel_ret_20d > 0.05:
                relative_strength_state = "OUTPERFORMING"
            elif rel_ret_20d < -0.05:
                relative_strength_state = "UNDERPERFORMING"
            else:
                relative_strength_state = "NEUTRAL"
        
        vol_state = "UNKNOWN"
        if atr_pct is not None:
            if atr_pct < 0.02: vol_state = "LOW"
            elif atr_pct <= 0.04: vol_state = "NORMAL"
            elif atr_pct <= 0.07: vol_state = "HIGH"
            else: vol_state = "EXTREME"
                
        # Inject for Evidence Quality Engine
        features["relative_strength"]["relative_strength_state"] = relative_strength_state
        features["volatility"]["volatility_state"] = vol_state
        features["market_regime"] = {
            "market_regime": market_regime,
            "regime_alignment": regime_alignment
        }
        
        evidence_res = EvidenceQualityEngine.evaluate(features)
        
        # 2. Scoring System
        trend_score = 0
        momentum_score = 0
        volume_score = 0
        price_action_score = 0
        relative_strength_score = 0
        relative_performance_score = 0
        flow_quality_score = 0
        data_quality_score = 10 if snapshot.data_quality == "FRESH" else 0
        
        if not missing_core_features:
            # Trend (Max 35)
            if price > sma20: trend_score += 10
            if price > sma50: trend_score += 10
            if sma20 > sma50: trend_score += 10
            if ema20 > ema50: trend_score += 5
            
            # Momentum (Max 25)
            if 40 <= rsi <= 70: momentum_score += 10
            elif rsi > 70: momentum_score += 5
            
            if macd > macd_sig: momentum_score += 10
            if macd_hist > 0: momentum_score += 5
            
            # Volume (Max 15)
            if rel_vol > 1.5: volume_score += 15
            elif rel_vol > 1.0: volume_score += 10
            elif rel_vol > 0.8: volume_score += 5
            
            # Price Action (Max 20)
            if close_pos is not None and close_pos >= 0.80: price_action_score += 5
            if ret_20d is not None and ret_20d > 0: price_action_score += 5
            if breakout_20d is True: price_action_score += 5
            if vol_trend is not None and vol_trend > 1.10: price_action_score += 5
            
            # Relative Strength (Max 15)
            if ret_20d is not None:
                if ret_20d > 0.10: relative_strength_score += 5
                elif ret_20d > 0.05: relative_strength_score += 3
                elif ret_20d > 0: relative_strength_score += 1
                
            if ret_5d is not None and ret_5d > 0: relative_strength_score += 3
            if ret_10d is not None and ret_10d > 0: relative_strength_score += 2
            if ret_60d is not None and ret_60d > 0: relative_strength_score += 5
            
            relative_strength_score = min(relative_strength_score, 15)
            
            # Relative Performance vs Benchmark (Max 10)
            if rel_ret_20d is not None:
                if rel_ret_20d > 0.10: relative_performance_score = 10
                elif rel_ret_20d > 0.05: relative_performance_score = 7
                elif rel_ret_20d > 0.02: relative_performance_score = 4
                elif rel_ret_20d > 0: relative_performance_score = 2
                
            # Flow Quality (Max 10)
            pv_conf = flow_features.get("price_volume_confirmation")
            ad_trend = flow_features.get("ad_trend")
            up_down_ratio = flow_features.get("up_down_volume_ratio")
            buy_ratio = flow_features.get("buy_volume_ratio")
            sell_ratio = flow_features.get("sell_volume_ratio")
            
            if pv_conf == "CONFIRMED": flow_quality_score += 3
            if ad_trend == "RISING": flow_quality_score += 2
            if up_down_ratio is not None and up_down_ratio > 1.5: flow_quality_score += 3
            if buy_ratio is not None and sell_ratio is not None and buy_ratio > sell_ratio: flow_quality_score += 2
            flow_quality_score = min(flow_quality_score, 10)
            
        raw_total = trend_score + momentum_score + volume_score + price_action_score + relative_strength_score + relative_performance_score + flow_quality_score + data_quality_score
        total_score = min(raw_total, 100)
        
        # Candidate Quality
        quant_confidence = evidence_res["quant_confidence"]
        candidate_quality = get_candidate_quality(total_score, quant_confidence)
        research_priority = get_research_priority(candidate_quality)
        
        # 3. Status
        status = "UNKNOWN"
        
        # Cek apakah dataset ini dari origin live atau historical
        meta = getattr(snapshot, 'metadata', None)
        origin = getattr(meta, 'data_origin', 'UNKNOWN') if meta else 'UNKNOWN'
        is_historical = origin in ["REAL_HISTORICAL", "SYNTHETIC", "MOCK"]
        
        if snapshot.data_quality == "STALE" and not is_historical:
            status = "STALE_DATA"
        elif missing_core_features:
            status = "INSUFFICIENT_DATA"
        elif total_score >= MINIMUM_CANDIDATE_SCORE:
            status = "READY_FOR_RESEARCH"
        else:
            status = "NOT_SELECTED"
            
        res = {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "quant_score": total_score,
            "quant_confidence": quant_confidence,
            "candidate_quality": candidate_quality,
            "research_priority": research_priority,
            "evidence_state": evidence_res["evidence_state"],
            "evidence_completeness": evidence_res["evidence_completeness"],
            "evidence_groups": evidence_res["evidence_groups"],
            "stock_regime": stock_regime,
            "market_regime": market_regime,
            "regime_alignment": regime_alignment,
            "relative_strength_state": relative_strength_state,
            "volatility_state": vol_state,
            "data_sufficiency": features["data_sufficiency"]["status"],
            "score_breakdown": {
                "trend_score": trend_score,
                "momentum_score": momentum_score,
                "volume_score": volume_score,
                "price_action_score": price_action_score,
                "relative_strength_score": relative_strength_score,
                "relative_performance_score": relative_performance_score,
                "flow_quality_score": flow_quality_score,
                "data_quality_score": data_quality_score
            },
            "features": features,
            "status": status
        }
        
        meta = getattr(snapshot, 'metadata', None)
        if meta:
            res["dataset_metadata"] = {
                "dataset_id": meta.dataset_id,
                "data_origin": getattr(meta, 'data_origin', 'UNKNOWN'),
                "data_quality": meta.audit_status,
                "data_quality_warnings": meta.warnings,
                "universe_method": meta.universe_method,
                "corporate_action_status": meta.corporate_action_status,
                "benchmark_available": getattr(meta, 'benchmark_available', False),
                "as_of_timestamp": snapshot.timestamp,
                "history_length": meta.record_count,
                "gap_status": meta.gap_status
            }
            
        return res

def rank_candidates(results: list[dict]) -> list[dict]:
    """
    Mengurutkan list dari result MarketScanner.
    Primary: quant_score DESC
    Secondary: quant_confidence DESC
    Tertiary: symbol ASC
    """
    valid_results = [r for r in results if r.get("status") in ("READY_FOR_RESEARCH", "NOT_SELECTED")]
    return sorted(valid_results, key=lambda x: (
        -x.get("quant_score", 0), 
        -x.get("quant_confidence", 0), 
        x.get("symbol", "")
    ))

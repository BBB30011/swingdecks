def get_candidate_quality(quant_score: float, quant_confidence: float) -> str:
    if quant_score >= 70 and quant_confidence >= 80:
        return "HIGH"
    elif quant_score >= 60 and quant_confidence >= 60:
        return "MEDIUM"
    elif quant_score >= 60 and quant_confidence >= 40:
        return "LOW"
    else:
        return "INSUFFICIENT"

def get_research_priority(candidate_quality: str) -> str:
    mapping = {
        "HIGH": "P1",
        "MEDIUM": "P2",
        "LOW": "P3",
        "INSUFFICIENT": "P4"
    }
    return mapping.get(candidate_quality, "P4")

class EvidenceQualityEngine:
    """
    Engine deterministic untuk mengkalkulasi kelengkapan evidence fitur kuantitatif.
    Tujuan utamanya adalah membedakan score tinggi yang didukung data lengkap 
    dengan score tinggi yang bolong (Missing / UNKNOWN features).
    """

    GROUPS = {
        "trend": [
            ("trend", "sma20"),
            ("trend", "sma50"),
            ("trend", "ema20"),
            ("trend", "ema50")
        ],
        "momentum": [
            ("momentum", "rsi14"),
            ("momentum", "macd"),
            ("momentum", "macd_signal"),
            ("momentum", "macd_histogram")
        ],
        "price_action": [
            ("price_action", "high_20d"),
            ("price_action", "low_20d"),
            ("price_action", "close_position_in_range"),
            ("price_action", "breakout_20d"),
            ("price_action", "breakout_50d")
        ],
        "volume": [
            ("volume", "volume_sma20"),
            ("volume", "relative_volume"),
            ("volume", "volume_trend_20d")
        ],
        "relative_strength": [
            ("relative_strength", "return_20d"),
            ("relative_strength", "benchmark_return_20d"),
            ("relative_strength", "relative_return_20d"),
            ("relative_strength", "relative_strength_state")  # injected by scanner
        ],
        "volatility": [
            ("volatility", "atr14"),
            ("volatility", "atr_percent"),
            ("volatility", "volatility_20d"),
            ("volatility", "volatility_state")  # injected by scanner
        ],
        "flow": [
            ("flow", "turnover"),
            ("flow", "turnover_sma20"),
            ("flow", "price_volume_confirmation"),
            ("flow", "ad_trend"),
            ("flow", "up_down_volume_ratio"),
            ("flow", "buy_volume_ratio"),
            ("flow", "sell_volume_ratio"),
            ("flow", "flow_state")
        ],
        "market_regime": [
            ("market_regime", "market_regime"),       # injected by scanner
            ("market_regime", "regime_alignment")     # injected by scanner
        ]
    }

    WEIGHTS = {
        "trend": 0.20,
        "momentum": 0.15,
        "price_action": 0.15,
        "volume": 0.10,
        "relative_strength": 0.15,
        "volatility": 0.10,
        "flow": 0.10,
        "market_regime": 0.05
    }

    @classmethod
    def is_available(cls, value) -> bool:
        """
        Mengevaluasi apakah value dari fitur dianggap tersedia (AVAILABLE).
        False/0.0 adalah AVAILABLE (karena valid feature value).
        None atau 'UNKNOWN' adalah MISSING.
        """
        if value is None:
            return False
        if isinstance(value, str):
            if value.upper() == "UNKNOWN":
                return False
        # float(NaN) is considered missing.
        if isinstance(value, float):
            import math
            if math.isnan(value):
                return False
        return True

    @classmethod
    def evaluate(cls, flat_features: dict) -> dict:
        """
        Mengevaluasi completeness. Argumen flat_features memetakan 
        (group, feature_name) -> value, mempermudah lookup dictionary bersarang.
        """
        
        group_results = {}
        total_completeness = 0.0

        for group, features in cls.GROUPS.items():
            available = 0
            total = len(features)
            
            for category, feature_name in features:
                # Cari feature. flat_features bentuknya: flat_features[category][feature_name]
                cat_dict = flat_features.get(category, {})
                val = cat_dict.get(feature_name, None)
                if cls.is_available(val):
                    available += 1
            
            group_comp = available / total if total > 0 else 0.0
            group_results[group] = group_comp
            
            weight = cls.WEIGHTS.get(group, 0.0)
            total_completeness += (group_comp * weight)

        # Cek data sufficiency
        data_suff = flat_features.get("data_sufficiency", {}).get("status", "SUFFICIENT")
        if data_suff == "INSUFFICIENT":
            # Jangan biarkan score bisa menembus batas psikologis jika INSUFFICIENT
            total_completeness = min(total_completeness, 0.99)
            
        quant_confidence = min(max(total_completeness * 100, 0), 100)
        
        # Evidence state
        if total_completeness >= 0.90:
            evidence_state = "COMPLETE"
        elif total_completeness >= 0.75:
            evidence_state = "GOOD"
        elif total_completeness >= 0.50:
            evidence_state = "PARTIAL"
        elif total_completeness >= 0.25:
            evidence_state = "WEAK"
        else:
            evidence_state = "INSUFFICIENT"
            
        return {
            "evidence_completeness": total_completeness,
            "evidence_groups": group_results,
            "evidence_state": evidence_state,
            "quant_confidence": quant_confidence
        }

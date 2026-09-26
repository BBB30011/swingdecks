from typing import Dict, Any, Literal, List
from core.position import PaperPosition

# Exit reason classification (Batch AR)
EXIT_REASONS = {
    "DATA_INVALID", "THESIS_INVALIDATED", "STOP_LOSS", "RISK_RED",
    "TARGET_REACHED", "TIME_EXIT",
    # Extended classification (AR)
    "MOMENTUM_FADE", "FLOW_REVERSAL", "FAILED_BREAKOUT",
    "MARKET_SHOCK", "SECTOR_REVERSAL", "CATALYST_EXPIRED",
    "TIME_DECAY", "THESIS_BREAK",
}

class ExitEngine:
    """
    Menghasilkan paper exit recommendation berdasarkan deterministic priority.
    Tidak membuat SELL order, hanya menghasilkan rekomendasi.
    
    Priority:
    1. DATA_INVALID
    2. THESIS_INVALIDATED
    3. STOP_LOSS
    4. RISK_RED
    5. TARGET_REACHED
    6. MOMENTUM_FADE / FLOW_REVERSAL (Batch AR)
    7. CATALYST_EXPIRED (Batch AR)
    8. SECTOR_REVERSAL (Batch AR)
    9. TIME_EXIT / TIME_DECAY
    """
    
    @staticmethod
    def evaluate(position: PaperPosition, context: Dict[str, Any]) -> Dict[str, Any]:
        current_price = position.current_price
        
        # 1. DATA_INVALID
        data_quality = context.get("data_quality", "VALID")
        if data_quality == "INVALID":
            return {"action": "EXIT", "reason": "DATA_INVALID", "price": current_price}
            
        # 2. THESIS_INVALIDATED
        active_invalidations = context.get("active_invalidations", [])
        if active_invalidations:
            return {"action": "EXIT", "reason": "THESIS_INVALIDATED", "price": current_price}
            
        # 3. STOP_LOSS
        if current_price and current_price <= position.stop_loss:
            return {"action": "EXIT", "reason": "STOP_LOSS", "price": current_price}
            
        # 4. RISK_RED
        risk_state = context.get("risk_state", "GREEN")
        exit_on_red = context.get("config", {}).get("exit_on_risk_red", True)
        if risk_state == "RED" and exit_on_red:
            return {"action": "EXIT", "reason": "RISK_RED", "price": current_price}
            
        # 5. TARGET_REACHED
        if current_price and current_price >= position.target_price:
            return {"action": "EXIT", "reason": "TARGET_REACHED", "price": current_price}

        # 6. MOMENTUM_FADE — quant score collapsed
        quant_score = context.get("quant_score", None)
        momentum_fade_threshold = context.get("config", {}).get("momentum_fade_threshold", 40)
        if quant_score is not None and quant_score <= momentum_fade_threshold:
            return {"action": "EXIT_WARNING", "reason": "MOMENTUM_FADE", "price": current_price}

        # 7. FLOW_REVERSAL — flow turned negative
        flow_state = context.get("flow_state", "UNKNOWN")
        if flow_state == "NEGATIVE":
            return {"action": "EXIT_WARNING", "reason": "FLOW_REVERSAL", "price": current_price}

        # 8. CATALYST_EXPIRED — original catalyst expired with no replacement
        catalyst_decay = context.get("catalyst_decay", "UNKNOWN")
        if catalyst_decay == "EXPIRED":
            return {"action": "EXIT_WARNING", "reason": "CATALYST_EXPIRED", "price": current_price}

        # 9. SECTOR_REVERSAL
        sector_state = context.get("sector_state", "UNKNOWN")
        if sector_state == "NEGATIVE":
            return {"action": "EXIT_WARNING", "reason": "SECTOR_REVERSAL", "price": current_price}
            
        # 10. TIME_EXIT
        max_holding_bars = context.get("config", {}).get("max_holding_bars", None)
        if max_holding_bars and position.holding_bars >= max_holding_bars:
            return {"action": "EXIT", "reason": "TIME_EXIT", "price": current_price}

        # 11. TIME_DECAY (approaching max but not over)
        time_decay_warning_pct = context.get("config", {}).get("time_decay_warning_pct", 0.8)
        if max_holding_bars and position.holding_bars >= max_holding_bars * time_decay_warning_pct:
            return {"action": "EXIT_WARNING", "reason": "TIME_DECAY", "price": current_price}
            
        # Default hold
        return {"action": "HOLD", "reason": "NONE"}

    @staticmethod
    def classify_reason(reason: str) -> str:
        """Returns severity of exit reason: CRITICAL / HIGH / MEDIUM / LOW."""
        if reason in ("DATA_INVALID", "STOP_LOSS", "RISK_RED"):
            return "CRITICAL"
        if reason in ("THESIS_INVALIDATED", "FAILED_BREAKOUT", "MARKET_SHOCK"):
            return "HIGH"
        if reason in ("TARGET_REACHED", "MOMENTUM_FADE", "FLOW_REVERSAL",
                      "CATALYST_EXPIRED", "SECTOR_REVERSAL", "THESIS_BREAK"):
            return "MEDIUM"
        return "LOW"

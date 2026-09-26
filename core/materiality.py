class MaterialityEngine:
    """
    Classifies material changes based on distance to critical levels and events.
    """
    
    @staticmethod
    def classify_price_movement(current_price: float, entry_price: float, stop_loss: float, target_price: float) -> str:
        if not current_price or not stop_loss or not target_price:
            return "LOW"
            
        distance_to_stop = (current_price - stop_loss) / current_price
        distance_to_target = (target_price - current_price) / current_price
        
        # Stop hit
        if current_price <= stop_loss:
            return "CRITICAL"
            
        # Target hit
        if current_price >= target_price:
            return "CRITICAL"
            
        # Near stop (< 2% away)
        if distance_to_stop < 0.02:
            return "HIGH"
            
        # Near target (< 2% away)
        if distance_to_target < 0.02:
            return "HIGH"
            
        # Medium movement (moved > 5% from entry)
        if entry_price:
            move_pct = abs(current_price - entry_price) / entry_price
            if move_pct > 0.05:
                return "MEDIUM"
                
        return "LOW"
        
    @staticmethod
    def classify_event(event_type: str) -> str:
        if event_type in ["THESIS_INVALIDATED", "DATA_INVALID"]:
            return "CRITICAL"
        if event_type in ["RISK_RED", "MAJOR_CORPORATE_EVENT"]:
            return "HIGH"
        if event_type in ["RISK_YELLOW", "REGIME_CHANGED"]:
            return "MEDIUM"
        return "LOW"

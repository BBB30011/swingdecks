class MarketRegimeEngine:
    """
    Engine deterministik untuk mendeteksi market regime berdasarkan fitur teknikal.
    Status yang dihasilkan: BULL, BEAR, SIDEWAYS, HIGH_VOLATILITY, UNKNOWN.
    Bisa diaplikasikan untuk IHSG maupun saham individual.
    """
    
    HIGH_VOLATILITY_THRESHOLD = 0.05  # ATR > 5%
    
    @classmethod
    def determine(cls, features: dict) -> str:
        if not features or "trend" not in features or "volatility" not in features:
            return "UNKNOWN"
            
        price = features.get("price", {}).get("current")
        sma20 = features.get("trend", {}).get("sma20")
        sma50 = features.get("trend", {}).get("sma50")
        atr_pct = features.get("volatility", {}).get("atr_percent")
        ret_20d = features.get("relative_strength", {}).get("return_20d")
        
        # Cek ketersediaan core features
        if None in [price, sma20, sma50, atr_pct, ret_20d]:
            return "UNKNOWN"
            
        # 1. HIGH_VOLATILITY prioritas utama
        if atr_pct > cls.HIGH_VOLATILITY_THRESHOLD:
            return "HIGH_VOLATILITY"
            
        # 2. BULL
        if price > sma20 and sma20 > sma50 and ret_20d > 0:
            return "BULL"
            
        # 3. BEAR
        if price < sma20 and sma20 < sma50 and ret_20d < 0:
            return "BEAR"
            
        # 4. SIDEWAYS
        return "SIDEWAYS"

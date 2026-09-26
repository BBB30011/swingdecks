import pandas as pd
from core.schemas import MarketSnapshot
from core.universe import UniverseManager

class LiquidityAnalyzer:
    """
    Kalkulator kelayakan saham berbasis price dan liquidity (Turnover/Volume).
    Bekerja deterministik memanfaatkan DataFrame pandas.
    """
    def __init__(self, universe_manager: UniverseManager = None):
        self.universe_manager = universe_manager or UniverseManager()
        config = self.universe_manager.config
        
        filters_cfg = config.get("filters", {})
        liq_cfg = config.get("liquidity", {})
        
        self.min_price = filters_cfg.get("minimum_price", 100)
        self.min_turnover = liq_cfg.get("minimum_average_turnover", 1000000000)

    def calculate(self, snapshot: MarketSnapshot) -> dict:
        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError("Input wajib berupa MarketSnapshot")
            
        symbol = snapshot.symbol
        base_result = {
            "symbol": symbol,
            "eligible": False,
            "price_eligible": False,
            "liquidity_status": "UNKNOWN",
            "average_volume": None,
            "average_turnover": None,
            "latest_volume": None,
            "latest_turnover": None,
            "reasons": []
        }
        
        if snapshot.data_quality == "INVALID":
            base_result["liquidity_status"] = "INVALID"
            base_result["reasons"].append("INVALID_DATA")
            return base_result
            
        if not snapshot.bars:
            base_result["liquidity_status"] = "INSUFFICIENT_DATA"
            base_result["reasons"].append("INSUFFICIENT_DATA")
            return base_result
            
        bars_data = [b.model_dump() for b in snapshot.bars]
        df = pd.DataFrame(bars_data)
        
        # Mencegah future data leakage
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        snap_time = pd.to_datetime(snapshot.timestamp)
        df = df[df['timestamp'] <= snap_time].copy()
        
        if df.empty:
            base_result["liquidity_status"] = "INSUFFICIENT_DATA"
            base_result["reasons"].append("INSUFFICIENT_DATA")
            return base_result
            
        df.sort_values('timestamp', ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        df['turnover'] = df['close'] * df['volume']
        avg_vol = float(df['volume'].mean())
        avg_turnover = float(df['turnover'].mean())
        
        last_bar = df.iloc[-1]
        latest_vol = float(last_bar['volume'])
        latest_turnover = float(last_bar['turnover'])
        current_price = float(last_bar['close'])
        
        base_result.update({
            "average_volume": avg_vol,
            "average_turnover": avg_turnover,
            "latest_volume": latest_vol,
            "latest_turnover": latest_turnover,
        })
        
        reasons = []
        
        if current_price >= self.min_price:
            base_result["price_eligible"] = True
        else:
            base_result["price_eligible"] = False
            reasons.append("PRICE_BELOW_MINIMUM")
            
        if avg_turnover >= self.min_turnover:
            base_result["liquidity_status"] = "LIQUID"
        else:
            base_result["liquidity_status"] = "ILLIQUID"
            reasons.append("AVERAGE_TURNOVER_BELOW_THRESHOLD")
            
        if snapshot.data_quality == "STALE":
            reasons.append("STALE_DATA")
            
        mode = "LIVE"
        try:
            import yaml
            from pathlib import Path
            cfg_path = Path("configs/data_source.yaml")
            if cfg_path.exists():
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    ds_cfg = yaml.safe_load(f) or {}
                    mode = ds_cfg.get("data_source", {}).get("mode", "LIVE")
        except Exception:
            pass
            
        is_historical = (mode == "HISTORICAL")
            
        is_eligible = (
            base_result["price_eligible"] and 
            base_result["liquidity_status"] == "LIQUID" and
            (snapshot.data_quality == "FRESH" or (snapshot.data_quality == "STALE" and is_historical))
        )
        
        base_result["eligible"] = is_eligible
        base_result["reasons"] = reasons
        
        return base_result

def filter_snapshots(snapshots: list[MarketSnapshot]) -> list[dict]:
    """
    Helper untuk memfilter ratusan snapshot secara deterministik.
    Menjamin tidak ada output symbol duplikat dan hasilnya tersortir ascending.
    """
    analyzer = LiquidityAnalyzer()
    results_dict = {}
    
    for snap in snapshots:
        res = analyzer.calculate(snap)
        if res["eligible"]:
            results_dict[res["symbol"]] = res
            
    results = list(results_dict.values())
    results.sort(key=lambda x: x["symbol"])
    return results

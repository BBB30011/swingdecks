import yaml
from pathlib import Path

class UniverseManager:
    """
    Manager deterministik untuk mengatur universe saham.
    Tidak menggunakan internet API; 100% lokal dari konfigurasi.
    """
    def __init__(self, config_path: str = "configs/universe.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            return {
                "universe": {"market": "IDX", "country": "Indonesia"},
                "filters": {"minimum_liquidity": True, "minimum_price": 100, "exclude_suspended": True},
                "liquidity": {"minimum_average_turnover": 1000000000, "minimum_average_volume": 0},
                "initial_symbols": []
            }
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def get_symbols(self) -> list[str]:
        symbols = self.config.get("initial_symbols", [])
        if not symbols:
            return []
        return self.filter_symbols(symbols)

    def filter_symbols(self, symbols: list[str]) -> list[str]:
        valid_symbols = []
        for s in symbols:
            if not s or not isinstance(s, str):
                continue
            s_clean = s.strip().upper()
            if s_clean:
                valid_symbols.append(s_clean)
        
        # Deduplikasi dan sorting alfabetik
        return sorted(list(set(valid_symbols)))

class HistoricalUniverseProvider:
    """
    Menyediakan dukungan eksplisit terkait survivorship bias.
    Batch W default: CURRENT_UNIVERSE.
    """
    
    METHODS = ["CURRENT_UNIVERSE", "HISTORICAL_UNIVERSE", "UNKNOWN"]
    
    def __init__(self, method: str = "CURRENT_UNIVERSE"):
        if method not in self.METHODS:
            method = "UNKNOWN"
        self.method = method
        
    def get_method(self) -> str:
        return self.method

from core.data_source import DataSourceFactory, DataUnavailableError, DataValidationError
from core.schemas import MarketSnapshot
from pathlib import Path
import yaml

class BenchmarkProvider:
    """
    Menyediakan MarketSnapshot untuk benchmark (seperti IHSG).
    Menggunakan abstraksi DataSourceFactory untuk pemuatan file (CSV/MOCK).
    Memastikan data di-cache selama run agar performa scanning efisien.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        
        # Load benchmark config if not present
        if "benchmark" not in self.config:
            universe_cfg = Path("configs/universe.yaml")
            if universe_cfg.exists():
                try:
                    with open(universe_cfg, 'r', encoding='utf-8') as f:
                        u_cfg = yaml.safe_load(f) or {}
                        if "benchmark" in u_cfg:
                            self.config["benchmark"] = u_cfg["benchmark"]
                except Exception:
                    pass
                    
        self.benchmark_cfg = self.config.get("benchmark", {})
        self.enabled = self.benchmark_cfg.get("enabled", True)
        self.symbol = self.benchmark_cfg.get("symbol", "IHSG")
        
        # Priority 1: benchmark.data_source from config dictionary
        # Priority 2: global data_source from config dictionary
        # Priority 3: global data_source.yaml file
        # Priority 4: Default fallback
        ds_cfg = None
        
        if "data_source" in self.benchmark_cfg:
            ds_cfg = {"data_source": self.benchmark_cfg["data_source"]}
        elif "data_source" in self.config:
            ds_cfg = {"data_source": self.config["data_source"]}
        else:
            try:
                ds_global = Path("configs/data_source.yaml")
                if ds_global.exists():
                    with open(ds_global, 'r', encoding='utf-8') as f:
                        dg = yaml.safe_load(f) or {}
                        if "data_source" in dg:
                            ds_cfg = {"data_source": dg["data_source"]}
            except Exception:
                pass
                
        if not ds_cfg:
            ds_cfg = {
                "data_source": {
                    "provider": "CSV",
                    "csv": {"directory": "data/raw"},
                    "mode": "HISTORICAL"
                }
            }
            
        # Ensure it is HISTORICAL mode to avoid freshness rejection
        if "data_source" in ds_cfg:
            ds_cfg["data_source"]["mode"] = "HISTORICAL"

        self.data_source = DataSourceFactory.create(ds_cfg)
        self._cache = {}

    def get_snapshot(self) -> MarketSnapshot:
        if not self.enabled:
            raise DataUnavailableError("Benchmark disabled via configuration")
            
        if self.symbol in self._cache:
            return self._cache[self.symbol]
            
        try:
            snap = self.data_source.get_snapshot(self.symbol)
            self._cache[self.symbol] = snap
            return snap
        except (DataUnavailableError, DataValidationError) as e:
            raise DataUnavailableError(f"Gagal memuat benchmark {self.symbol}: {e}")

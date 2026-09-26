from core.schemas import MarketSnapshot
from core.validator import validate_model
from core.data_source import MarketDataSource
from core.data_repository import DataRepository, check_data_quality

class DataEngine:
    """
    Orchestrator untuk mengambil data market dari source,
    memvalidasi kelayakannya, lalu menyimpannya ke repository lokal.
    """
    def __init__(self, data_source: MarketDataSource, repository: DataRepository, config: dict = None):
        self.data_source = data_source
        self.repository = repository
        self.config = config or {}
        
        ds_config = self.config.get("data_source", {})
        freshness_cfg = ds_config.get("freshness", {})
        self.max_age_minutes = freshness_cfg.get("max_age_minutes", 60)

    def fetch_and_store(self, symbol: str, as_of_timestamp: str = None) -> MarketSnapshot:
        # 1. Meminta snapshot dari data source
        snapshot = self.data_source.get_snapshot(symbol, as_of_timestamp=as_of_timestamp)
        
        # 2. Memastikan hasil berupa object MarketSnapshot
        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError(f"Hasil dari data source harus MarketSnapshot, bukan {type(snapshot)}")
            
        # 3. Melakukan validation Schema (OHLCV constraints)
        try:
            validate_model(snapshot)
        except Exception as e:
            raise ValueError(f"Snapshot untuk {symbol} tidak lolos validasi: {e}")
            
        # 4. Terapkan freshness ruleset dari config & repository
        actual_quality = check_data_quality(snapshot, self.max_age_minutes)
        snapshot.data_quality = actual_quality
            
        # 5. Menyimpan snapshot melalui DataRepository
        self.repository.save_snapshot(snapshot)
        
        return snapshot

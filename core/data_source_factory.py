from typing import Optional, Dict, Any
from core.data_source import MarketDataSource, MockMarketDataSource
from core.csv_data_source import CSVMarketDataSource
from core.providers.yfinance_provider import YFinanceProvider

class DataSourceFactory:
    """
    Factory untuk menginstansiasi provider secara dinamis dari config.
    Decoupled from core.data_source to eliminate circular dependencies.
    """
    @staticmethod
    def create(config: Optional[Dict[str, Any]] = None) -> MarketDataSource:
        if config is None:
            config = {}
        
        ds_config = config.get("data_source", {})
        provider = ds_config.get("provider", "MOCK").upper().strip()
        
        if provider == "MOCK":
            return MockMarketDataSource(config)
        elif provider == "CSV":
            return CSVMarketDataSource(config)
        elif provider == "YFINANCE":
            return YFinanceProvider(config)
            
        raise ValueError(f"Unknown Market Data Provider: {provider}")

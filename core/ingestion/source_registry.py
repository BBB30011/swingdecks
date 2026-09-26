import pandas as pd
from typing import Dict, Any, List
from datetime import datetime, timezone
import os

class SourceRegistry:
    def __init__(self, output_path: str = "gates/closed/data_source_registry_zzz1.csv"):
        self.output_path = output_path
        self.sources: Dict[str, Dict[str, Any]] = {}
        
        # Seed with initial known sources
        self.register_source({
            "source_id": "SRC_YFINANCE_MARKET",
            "source_name": "Yahoo Finance (yfinance)",
            "provider": "Yahoo",
            "data_category": "MARKET",
            "data_type": "OHLCV_CORP_ACTIONS",
            "coverage": "GLOBAL_IDX_ACTIVE",
            "historical_depth": "10y+",
            "granularity": "1d",
            "timezone": "Jakarta/UTC",
            "publication_timestamp_available": False,
            "observation_timestamp_available": True,
            "retrieval_timestamp_available": True,
            "PIT_capability": "LIMITED",
            "corporate_action_support": "YES",
            "historical_universe_support": "NO",
            "survivorship_support": "NO",
            "API_required": "NO",
            "credential_required": "NO",
            "rate_limit": "YES",
            "license/access_constraints": "Public/RateLimited",
            "reliability": "MEDIUM",
            "status": "ACTIVE",
            "last_verified": datetime.now(timezone.utc).isoformat()
        })
        
    def register_source(self, metadata: Dict[str, Any]) -> None:
        """Registers a new source in the registry."""
        source_id = metadata["source_id"]
        self.sources[source_id] = metadata
        
    def export_registry(self) -> None:
        """Exports the registry to a CSV file."""
        df = pd.DataFrame.from_dict(self.sources, orient="index")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)
        print(f"Exported Data Source Registry to {self.output_path}")

    def get_source(self, source_id: str) -> Dict[str, Any]:
        return self.sources.get(source_id)

if __name__ == "__main__":
    registry = SourceRegistry()
    registry.export_registry()

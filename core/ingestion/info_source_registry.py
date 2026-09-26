import pandas as pd
from typing import Dict, Any
from datetime import datetime, timezone
import os

class InfoSourceRegistry:
    def __init__(self, output_path: str = "reports/info_source_registry_zzz2.csv"):
        self.output_path = output_path
        self.sources: Dict[str, Dict[str, Any]] = {}
        
        # Seed with initial hypothetical/planned information sources
        self.register_source({
            "source_id": "INFO_IDX_ANNOUNCEMENTS",
            "source_name": "IDX Official Announcements",
            "source_type": "official exchange/regulator",
            "coverage": "IDX Listed Companies",
            "historical_depth": "10y+",
            "timestamp_quality": "HIGH",
            "entity_linkage": "HIGH",
            "PIT_quality": "HIGH",
            "provenance_quality": "HIGH",
            "access_method": "API / Web Scraping",
            "license_constraint": "Public",
            "reliability": "HIGH",
            "limitations": "Corporate actions and financial reports only, lacks macro context.",
            "status": "PLANNED"
        })
        
        self.register_source({
            "source_id": "INFO_GOV_MINISTRY",
            "source_name": "Ministry Decrees / Regulations",
            "source_type": "government/ministry",
            "coverage": "National Policy (Coal, Nickel, CPO)",
            "historical_depth": "Variable",
            "timestamp_quality": "MEDIUM",
            "entity_linkage": "LOW (Requires NLP extraction)",
            "PIT_quality": "MEDIUM",
            "provenance_quality": "HIGH",
            "access_method": "Manual / Govt APIs",
            "license_constraint": "Public",
            "reliability": "HIGH",
            "limitations": "Hard to map directly to specific tickers automatically.",
            "status": "PLANNED"
        })
        
    def register_source(self, metadata: Dict[str, Any]) -> None:
        """Registers a new source in the information registry."""
        source_id = metadata["source_id"]
        self.sources[source_id] = metadata
        
    def export_registry(self) -> None:
        """Exports the registry to a CSV file."""
        df = pd.DataFrame.from_dict(self.sources, orient="index")
        
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        df.to_csv(self.output_path, index=False)
        print(f"Exported Information Source Registry to {self.output_path}")

    def get_source(self, source_id: str) -> Dict[str, Any]:
        return self.sources.get(source_id)

if __name__ == "__main__":
    registry = InfoSourceRegistry()
    registry.export_registry()

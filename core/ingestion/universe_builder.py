import os
import pandas as pd
from datetime import datetime, timezone
from typing import List, Dict, Any

class UniverseBuilder:
    def __init__(self, output_path: str = "data/parquet/entity/universe.parquet"):
        self.output_path = output_path
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
    def build_pilot_universe(self) -> None:
        """
        Builds a pilot historical universe from a static known list of major IDX tickers.
        Because this list is current-day active tickers only, survivorship bias is guaranteed.
        Therefore, we strictly label it HIGH_RISK.
        """
        # Hardcoded sample for Pilot Phase 1 (e.g. Major IDX banks & commodities)
        pilot_tickers = [
            ("BBCA", "Bank Central Asia Tbk", "FINANCIALS"),
            ("BBRI", "Bank Rakyat Indonesia Tbk", "FINANCIALS"),
            ("BMRI", "Bank Mandiri Tbk", "FINANCIALS"),
            ("BBNI", "Bank Negara Indonesia Tbk", "FINANCIALS"),
            ("TLKM", "Telkom Indonesia Tbk", "INFRASTRUCTURE"),
            ("ASII", "Astra International Tbk", "CONSUMER_CYCLICALS"),
            ("PTBA", "Bukit Asam Tbk", "ENERGY"),
            ("ADRO", "Adaro Energy Tbk", "ENERGY"),
            ("ITMG", "Indo Tambangraya Megah Tbk", "ENERGY"),
            ("UNTR", "United Tractors Tbk", "INDUSTRIALS"),
            ("ANTM", "Aneka Tambang Tbk", "BASIC_MATERIALS"),
            ("INCO", "Vale Indonesia Tbk", "BASIC_MATERIALS")
        ]
        
        records = []
        retrieved_at = datetime.now(timezone.utc).isoformat()
        
        for ticker, name, sector in pilot_tickers:
            records.append({
                "entity_id": f"ENT_{ticker}",
                "ticker": ticker,
                "company_name": name,
                "exchange": "IDX",
                "sector": sector,
                "valid_from": "1990-01-01T00:00:00Z",  # Arbitrary deep history start
                "valid_to": None,
                "status": "LISTED",
                "source": "MANUAL_PILOT",
                "provenance": "MANUAL_ENTRY",
                "survivorship_status": "HIGH_RISK",
                "retrieved_at": retrieved_at
            })
            
        df = pd.DataFrame(records)
        df.to_parquet(self.output_path)
        print(f"Exported universe of {len(df)} entities to {self.output_path}. SURVIVORSHIP STATUS: HIGH_RISK.")

if __name__ == "__main__":
    builder = UniverseBuilder()
    builder.build_pilot_universe()

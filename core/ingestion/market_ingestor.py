import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
import pyarrow as pa
import pyarrow.parquet as pq

# We reuse the core logic from yfinance_provider, but bypass its internal MarketBar schemas 
# to save directly to Parquet for bulk historical ingestion.

class MarketDataIngestor:
    def __init__(self, raw_dir: str = "data/raw/market", parquet_dir: str = "data/parquet/market", ca_dir: str = "data/parquet/corporate_actions"):
        self.raw_dir = raw_dir
        self.parquet_dir = parquet_dir
        self.ca_dir = ca_dir
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.parquet_dir, exist_ok=True)
        os.makedirs(self.ca_dir, exist_ok=True)
        
    def _translate_symbol(self, symbol: str) -> str:
        """Appends .JK if not already present."""
        if not symbol.endswith(".JK") and symbol != "^JKSE":
            if symbol == "IHSG":
                return "^JKSE"
            return f"{symbol}.JK"
        return symbol

    def ingest_ticker(self, symbol: str, period: str = "max") -> Dict[str, Any]:
        """
        Fetches max available history for a ticker.
        Saves raw CSV to data/raw, and normalized Parquet to data/parquet.
        Extracts corporate actions to data/parquet/corporate_actions.
        Idempotent: Replaces or merges existing data, dropping duplicates.
        """
        sym_req = self._translate_symbol(symbol)
        ticker = yf.Ticker(sym_req)
        
        try:
            # We explicitly want auto_adjust=False to get raw prices, 
            # and actions=True to get splits/dividends.
            df = ticker.history(period=period, interval="1d", auto_adjust=False, actions=True)
        except Exception as e:
            return {"symbol": symbol, "status": "ERROR", "message": str(e)}
            
        if df.empty:
            return {"symbol": symbol, "status": "NO_DATA"}
            
        retrieved_at = datetime.now(timezone.utc).isoformat()
        df.index = pd.to_datetime(df.index, utc=True)
        
        # 1. Save Raw File
        raw_file = os.path.join(self.raw_dir, f"{symbol}_raw.csv")
        df.to_csv(raw_file)
        
        # 2. Extract Corporate Actions
        ca_records = []
        if 'Dividends' in df.columns and 'Stock Splits' in df.columns:
            ca_df = df[(df['Dividends'] > 0) | (df['Stock Splits'] > 0)].copy()
            for date, row in ca_df.iterrows():
                if row['Dividends'] > 0:
                    ca_records.append({
                        "corporate_action_id": f"DIV_{symbol}_{date.strftime('%Y%m%d')}",
                        "entity_id": symbol,
                        "action_type": "DIVIDEND",
                        "effective_date": date.isoformat(),
                        "value": float(row['Dividends']),
                        "source": "YFINANCE",
                        "retrieved_at": retrieved_at
                    })
                if row['Stock Splits'] > 0:
                    ca_records.append({
                        "corporate_action_id": f"SPLIT_{symbol}_{date.strftime('%Y%m%d')}",
                        "entity_id": symbol,
                        "action_type": "SPLIT",
                        "effective_date": date.isoformat(),
                        "value": float(row['Stock Splits']),
                        "source": "YFINANCE",
                        "retrieved_at": retrieved_at
                    })
        
        if ca_records:
            ca_path = os.path.join(self.ca_dir, f"{symbol}_actions.parquet")
            ca_out_df = pd.DataFrame(ca_records)
            ca_out_df.to_parquet(ca_path)
            
        # 3. Normalize Market Data
        # Keep standard OHLCV
        market_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        available_cols = [c for c in market_cols if c in df.columns]
        
        market_df = df[available_cols].copy()
        market_df.reset_index(inplace=True)
        market_df.rename(columns={'Date': 'timestamp', 'Datetime': 'timestamp'}, inplace=True)
        
        # Drop rows with NaN in Close
        market_df.dropna(subset=['Close'], inplace=True)
        
        # Add metadata
        market_df['symbol'] = symbol
        market_df['source'] = "YFINANCE"
        market_df['retrieved_at'] = retrieved_at
        market_df['dataset_version'] = "v1"
        
        market_path = os.path.join(self.parquet_dir, f"{symbol}.parquet")
        
        # Idempotency: Combine with existing, drop duplicates by timestamp
        if os.path.exists(market_path):
            existing_df = pd.read_parquet(market_path)
            combined_df = pd.concat([existing_df, market_df])
            # Drop duplicates keeping the latest retrieval
            combined_df.sort_values(by=['timestamp', 'retrieved_at'], inplace=True)
            combined_df.drop_duplicates(subset=['timestamp', 'symbol'], keep='last', inplace=True)
            market_df = combined_df
            
        market_df.to_parquet(market_path)
        
        return {
            "symbol": symbol,
            "status": "SUCCESS",
            "rows_ingested": len(market_df),
            "corporate_actions_found": len(ca_records),
            "min_date": market_df['timestamp'].min().isoformat() if not market_df.empty else None,
            "max_date": market_df['timestamp'].max().isoformat() if not market_df.empty else None
        }

if __name__ == "__main__":
    ingestor = MarketDataIngestor()
    print(ingestor.ingest_ticker("BBCA", period="max"))

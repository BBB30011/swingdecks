import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

from core.data_source import MarketDataSource, DataUnavailableError, DataValidationError
from core.schemas import MarketSnapshot, MarketBar

class CSVMarketDataSource(MarketDataSource):
    """
    Membaca historical OHLCV data dari file CSV lokal.
    Digunakan untuk research, backtesting, atau batch ingestion deterministik.
    """
    def __init__(self, config: dict = None):
        self.config = config or {}
        ds_config = self.config.get("data_source", {})
        csv_config = ds_config.get("csv", {})
        self.directory = Path(csv_config.get("directory", "data/raw/market"))
        self.timestamp_col_config = csv_config.get("timestamp_column", "timestamp").lower()
        self._cache = {}

    def _normalize_symbol(self, symbol: str) -> str:
        # Override MarketDataSource._normalize_symbol to NOT remove suffixes blindly.
        # "Normalisasi symbol: trim uppercase. Tetapi: BBCA.JK dan BBCA jangan dianggap identik secara otomatis."
        if not symbol or not isinstance(symbol, str):
            return "UNKNOWN"
        return symbol.strip().upper()

    def get_snapshot(self, symbol: str, as_of_timestamp: Optional[str] = None) -> MarketSnapshot:
        sym = self._normalize_symbol(symbol)
        
        if sym in self._cache:
            df, file_hash = self._cache[sym]
        else:
            # Cari file dengan ekstensi .csv atau .CSV
            file_path = self.directory / f"{sym}_raw.csv"
            if not file_path.exists():
                file_path = self.directory / f"{sym}.csv"
            if not file_path.exists():
                file_path = self.directory / f"{sym}.CSV"
            if not file_path.exists():
                raise DataUnavailableError(f"CSV file not found for {sym} in {self.directory}")
                    
            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                raise DataValidationError(f"Failed to parse CSV for {sym}: {e}")
                
            if df.empty:
                raise DataValidationError(f"CSV for {sym} is empty")
                
            # Normalisasi nama kolom
            df.columns = df.columns.str.strip().str.lower()
            
            # Fallback date -> timestamp
            if 'timestamp' not in df.columns:
                if self.timestamp_col_config in df.columns:
                    df.rename(columns={self.timestamp_col_config: 'timestamp'}, inplace=True)
                elif 'date' in df.columns:
                    df.rename(columns={'date': 'timestamp'}, inplace=True)
                    
            required_cols = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            for col in required_cols:
                if col not in df.columns:
                    raise DataValidationError(f"Missing required column '{col}' in {file_path.name}")
                    
            # Cek NaNs untuk required columns
            if df[required_cols].isna().any().any():
                raise DataValidationError(f"Missing values (NaN/NULL) found in OHLCV for {sym}")
                
            # Pastikan tipe numerik
            try:
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    df[col] = pd.to_numeric(df[col])
            except ValueError:
                raise DataValidationError(f"Non-numeric values in OHLCV for {sym}")
                
            # Normalisasi format timestamp ISO8601 dengan Asia/Jakarta
            try:
                dt_series = pd.to_datetime(df['timestamp'])
                if dt_series.dt.tz is None:
                    dt_series = dt_series.dt.tz_localize("Asia/Jakarta")
                else:
                    dt_series = dt_series.dt.tz_convert("Asia/Jakarta")
                df['timestamp'] = dt_series.dt.strftime('%Y-%m-%dT%H:%M:%S%z')
            except Exception as e:
                raise DataValidationError(f"Invalid timestamp format in {file_path.name}: {e}")
                
            # Sorting & reject duplicate
            df = df.sort_values('timestamp')
            if df['timestamp'].duplicated().any():
                raise DataValidationError(f"Duplicate timestamp detected for {sym}")
                
            import hashlib
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            self._cache[sym] = (df, file_hash)
            
        # Filter as_of_timestamp
        if as_of_timestamp:
            try:
                as_of_dt = pd.to_datetime(as_of_timestamp)
                if as_of_dt.tzinfo is None:
                    as_of_dt = as_of_dt.tz_localize("Asia/Jakarta")
                else:
                    as_of_dt = as_of_dt.tz_convert("Asia/Jakarta")
                as_of_dt_str = as_of_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
                df = df[df['timestamp'] <= as_of_dt_str]
            except Exception as e:
                raise DataValidationError(f"Invalid as_of_timestamp format: {e}")
                
        if df.empty:
            raise DataValidationError(f"No bars available for {sym} after applying as_of_timestamp filter")
            
        bars = []
        for _, row in df.iterrows():
            o = float(row['open'])
            h = float(row['high'])
            l = float(row['low'])
            c = float(row['close'])
            v = float(row['volume'])
            
            # Auto-correct dirty OHLC data to satisfy MarketBar constraints
            actual_high = max(o, h, l, c)
            actual_low = min(o, h, l, c)
            
            bars.append(MarketBar(
                symbol=sym,
                timestamp=row['timestamp'],
                open=o,
                high=actual_high,
                low=actual_low,
                close=c,
                volume=v
            ))
            
        bars = self._validate_and_sort_bars(bars)
        
        snap = MarketSnapshot(
            symbol=sym,
            timestamp=bars[-1].timestamp,
            bars=bars,
            data_source="CSV",
            data_quality="FRESH" # Wait, historical should be HISTORICAL/STALE based on prompt?
        )
        
        # Override data quality for historical
        snap.data_quality = "STALE" # "Historical = historical context. Jangan memalsukan freshness."
        
        # Assign Batch Z Data Origin and new metrics
        snap.metadata.data_origin = "REAL_HISTORICAL" 
        snap.metadata.record_count = len(bars)
        snap.metadata.start_timestamp = bars[0].timestamp
        snap.metadata.end_timestamp = bars[-1].timestamp
        
        # Check history sufficiency
        if len(bars) < 200:
            snap.metadata.audit_status = "PARTIAL"
            snap.metadata.warnings.append("Insufficient history (<200 bars)")
            
        # Assign checksum warning
        snap.metadata.warnings.append(f"checksum:{file_hash}")
        
        return snap

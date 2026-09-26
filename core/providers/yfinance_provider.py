import yfinance as yf
import pandas as pd
from typing import Optional, List
from datetime import datetime, timezone

from core.data_source import MarketDataSource, DataUnavailableError, DataValidationError
from core.schemas import MarketSnapshot, MarketBar

class YFinanceProvider(MarketDataSource):
    """
    MarketDataSource implementation using yfinance to fetch IDX data.
    Automatically appends '.JK' to IDX tickers.
    """
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        # Fetch configurations or default limits
        self.default_period = self.config.get("period", "5y")
        
    def _translate_symbol(self, symbol: str) -> str:
        """Appends .JK if not already present."""
        sym = self._normalize_symbol(symbol)
        if not sym.endswith(".JK") and sym != "^JKSE":
            # Assuming IHSG is passed as ^JKSE, else regular tickers get .JK
            if sym == "IHSG":
                return "^JKSE"
            return f"{sym}.JK"
        return sym
        
    def get_snapshot(self, symbol: str, as_of_timestamp: Optional[str] = None) -> MarketSnapshot:
        sym_req = self._translate_symbol(symbol)
        sym_clean = self._normalize_symbol(symbol)
        
        try:
            ticker = yf.Ticker(sym_req)
            # We fetch up to 5y by default to ensure we have enough history for quant indicators
            # and to mimic a solid data acquisition pass.
            df = ticker.history(period=self.default_period, interval="1d", auto_adjust=False)
            
            if df.empty:
                raise DataUnavailableError(f"No data returned for {sym_req} from yfinance.")
                
            # Filter up to as_of_timestamp if provided (Point in Time isolation)
            if as_of_timestamp:
                try:
                    limit_dt = pd.to_datetime(as_of_timestamp, utc=True)
                    # Convert index to UTC for comparison
                    df.index = pd.to_datetime(df.index, utc=True)
                    df = df[df.index <= limit_dt]
                except Exception as e:
                    raise DataValidationError(f"Invalid timestamp format: {as_of_timestamp}. {e}")
                    
            if df.empty:
                raise DataUnavailableError(f"No data for {sym_req} before timestamp {as_of_timestamp}.")
                
            bars: List[MarketBar] = []
            for date, row in df.iterrows():
                # Clean up dirty data
                if pd.isna(row['Open']) or pd.isna(row['Close']):
                    continue
                    
                bars.append(MarketBar(
                    symbol=sym_clean,
                    timestamp=date.isoformat(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=float(row['Volume'])
                ))
                
            bars = self._validate_and_sort_bars(bars)
            
            if not bars:
                raise DataValidationError(f"No valid bars extracted for {sym_clean}.")
                
            snap_ts = bars[-1].timestamp
            return MarketSnapshot(
                symbol=sym_clean,
                timestamp=snap_ts,
                bars=bars,
                data_source="YFINANCE",
                data_quality="FRESH"
            )
            
        except Exception as e:
            if isinstance(e, (DataUnavailableError, DataValidationError)):
                raise
            raise DataSourceError(f"Error fetching data from YFinance for {sym_req}: {str(e)}")

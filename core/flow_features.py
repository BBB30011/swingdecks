import pandas as pd
import numpy as np
from core.schemas import MarketSnapshot

class FlowFeatureEngine:
    """
    Engine deterministic untuk menghitung indikator price-volume dan market flow 
    (Accumulation/Distribution, Volume Pressure, Turnover, dll).
    Flow Analytics ini murni bersifat observasional kuantitatif dan BUKAN jaminan pelaku pasar tertentu.
    """
    
    def calculate(self, snapshot: MarketSnapshot) -> dict:
        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError("Input harus MarketSnapshot")
            
        if snapshot.data_quality == "INVALID":
            raise ValueError("Data quality INVALID tidak dapat diproses")
            
        if not snapshot.bars:
            raise ValueError("Snapshot tidak memiliki data bar")
            
        df = pd.DataFrame([b.model_dump() for b in snapshot.bars])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        snap_time = pd.to_datetime(snapshot.timestamp)
        
        # PENCEGAHAN LOOK-AHEAD:
        df = df[df['timestamp'] <= snap_time].copy()
        
        if df.empty:
            raise ValueError("Tidak ada bar yang valid sebelum atau sama dengan timestamp snapshot")
            
        df.sort_values('timestamp', ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        def get_last(series):
            if len(series) == 0:
                return None
            val = series.iloc[-1]
            if pd.isna(val) or np.isinf(val):
                return None
            return float(val)

        close = df['close']
        open_p = df['open']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # 1. Basic Price-Volume
        vol_change_5d = volume / volume.shift(5) - 1
        vol_change_20d = volume / volume.shift(20) - 1
        
        # Safe handling if volume.shift is 0
        vol_change_5d = vol_change_5d.replace([np.inf, -np.inf], np.nan)
        vol_change_20d = vol_change_20d.replace([np.inf, -np.inf], np.nan)
        
        turnover = close * volume
        turnover_sma20 = turnover.rolling(20, min_periods=20).mean()
        
        # Masking dev zero if denominator is 0
        prev_turnover_20d = turnover.shift(20)
        turnover_change_20d = pd.Series(
            np.where(prev_turnover_20d > 0, turnover / prev_turnover_20d - 1, np.nan),
            index=df.index
        )
        
        turnover_rel_sma20 = pd.Series(
            np.where(turnover_sma20 > 0, turnover / turnover_sma20, np.nan),
            index=df.index
        )
        
        vol_sma20 = volume.rolling(20, min_periods=20).mean()
        vol_rel_sma20 = pd.Series(
            np.where(vol_sma20 > 0, volume / vol_sma20, np.nan),
            index=df.index
        )
        
        # 2. Price-Volume Confirmation
        ret_20d = close.pct_change(20)
        
        last_ret_20d = get_last(ret_20d)
        last_vol_change_20d = get_last(vol_change_20d)
        
        pv_confirmation = "UNKNOWN"
        if last_ret_20d is not None and last_vol_change_20d is not None:
            if last_ret_20d > 0 and last_vol_change_20d > 0:
                pv_confirmation = "CONFIRMED"
            elif (last_ret_20d > 0 and last_vol_change_20d < 0) or (last_ret_20d < 0 and last_vol_change_20d > 0):
                pv_confirmation = "DIVERGENCE"
            else:
                pv_confirmation = "NEUTRAL"
                
        # 3. Accumulation / Distribution Line
        range_hl = high - low
        # Handle zero range
        mfm = np.where(range_hl > 0, ((close - low) - (high - close)) / range_hl, 0.0)
        mfv = mfm * volume
        ad_line = pd.Series(mfv).cumsum()
        
        # 4. AD Trend
        ad_slope_20d = ad_line - ad_line.shift(20)
        last_ad_slope = get_last(ad_slope_20d)
        
        ad_trend = "UNKNOWN"
        if last_ad_slope is not None:
            if last_ad_slope > 0:
                ad_trend = "RISING"
            elif last_ad_slope < 0:
                ad_trend = "FALLING"
            else:
                ad_trend = "FLAT"
                
        # 5. Up/Down Volume (20D)
        prev_close = close.shift(1)
        up_vol = np.where(close > prev_close, volume, 0.0)
        down_vol = np.where(close < prev_close, volume, 0.0)
        
        up_vol_20d = pd.Series(up_vol).rolling(20, min_periods=20).sum()
        down_vol_20d = pd.Series(down_vol).rolling(20, min_periods=20).sum()
        
        up_down_ratio = pd.Series(
            np.where(down_vol_20d > 0, up_vol_20d / down_vol_20d, np.nan),
            index=df.index
        )
        
        # 6. Buying / Selling Pressure Proxy (Candle-based)
        buy_vol = np.where(close > open_p, volume, 0.0)
        sell_vol = np.where(close < open_p, volume, 0.0)
        
        buy_vol_20d = pd.Series(buy_vol).rolling(20, min_periods=20).sum()
        sell_vol_20d = pd.Series(sell_vol).rolling(20, min_periods=20).sum()
        total_vol_20d = volume.rolling(20, min_periods=20).sum()
        
        buy_vol_ratio = pd.Series(
            np.where(total_vol_20d > 0, buy_vol_20d / total_vol_20d, np.nan),
            index=df.index
        )
        sell_vol_ratio = pd.Series(
            np.where(total_vol_20d > 0, sell_vol_20d / total_vol_20d, np.nan),
            index=df.index
        )
        
        # 7. Flow State
        flow_state = "UNKNOWN"
        if ad_trend == "RISING" and pv_confirmation == "CONFIRMED":
            flow_state = "ACCUMULATION"
        elif ad_trend == "FALLING" and last_ret_20d is not None and last_ret_20d < 0:
            flow_state = "DISTRIBUTION"
        elif ad_trend != "UNKNOWN" and last_ret_20d is not None:
            flow_state = "NEUTRAL"
        
        result = {
            "volume_change_5d": get_last(vol_change_5d),
            "volume_change_20d": get_last(vol_change_20d),
            "turnover": get_last(turnover),
            "turnover_sma20": get_last(turnover_sma20),
            "turnover_change_20d": get_last(turnover_change_20d),
            "turnover_relative_to_sma20": get_last(turnover_rel_sma20),
            "volume_relative_to_sma20": get_last(vol_rel_sma20),
            "price_volume_confirmation": pv_confirmation,
            "ad_line": get_last(ad_line),
            "ad_slope_20d": last_ad_slope,
            "ad_trend": ad_trend,
            "up_volume_20d": get_last(up_vol_20d),
            "down_volume_20d": get_last(down_vol_20d),
            "up_down_volume_ratio": get_last(up_down_ratio),
            "buy_volume_ratio": get_last(buy_vol_ratio),
            "sell_volume_ratio": get_last(sell_vol_ratio),
            "flow_state": flow_state
        }
        
        return result

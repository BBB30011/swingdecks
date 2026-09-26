import pandas as pd
import numpy as np
from core.schemas import MarketSnapshot

class QuantFeatureEngine:
    """
    Engine untuk menghasilkan fitur teknikal (Trend, Momentum, Volatility, Volume)
    berdasarkan data MarketSnapshot secara deterministik.
    """
    
    def calculate(self, snapshot: MarketSnapshot, benchmark_snapshot: MarketSnapshot = None) -> dict:
        if not isinstance(snapshot, MarketSnapshot):
            raise TypeError("Input harus berupa objek MarketSnapshot")
            
        if snapshot.data_quality == "INVALID":
            raise ValueError("Data quality INVALID tidak dapat diproses")
            
        if not snapshot.bars:
            raise ValueError("Snapshot tidak memiliki data bar")
            
        # Ekstrak bars ke Pandas DataFrame
        bars_data = [b.model_dump() for b in snapshot.bars]
        df = pd.DataFrame(bars_data)
        
        # Konversi ke datetime agar dapat disortir & difilter
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        snap_time = pd.to_datetime(snapshot.timestamp)
        
        # PENCEGAHAN LOOK-AHEAD:
        # Buang semua bar yang memiliki timestamp setelah timestamp snapshot
        df = df[df['timestamp'] <= snap_time].copy()
        
        if df.empty:
            raise ValueError("Tidak ada bar yang valid sebelum atau sama dengan timestamp snapshot")
            
        # Pengurutan data (sorting) mencegah error pada bar yang acak
        df.sort_values('timestamp', ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        # Helper untuk menarik scalar akhir secara aman (replace NaN dengan None)
        def get_last(series):
            if len(series) == 0:
                return None
            val = series.iloc[-1]
            if pd.isna(val) or np.isinf(val):
                return None
            return float(val)

        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # 1. Price Structure & Relative Strength
        current_price = get_last(close)
        
        if len(close) > 1:
            prev_close = close.iloc[-2]
            price_change = current_price - prev_close if current_price is not None else None
            price_change_pct = (price_change / prev_close) * 100 if prev_close and prev_close != 0 and price_change is not None else 0.0
        else:
            price_change = None
            price_change_pct = None
            
        ret_5d = close.pct_change(5)
        ret_10d = close.pct_change(10)
        ret_20d = close.pct_change(20)
        ret_60d = close.pct_change(60)
            
        # 2. Trend & Trend Quality
        sma20 = close.rolling(20, min_periods=20).mean()
        sma50 = close.rolling(50, min_periods=50).mean()
        sma200 = close.rolling(200, min_periods=200).mean()
        
        ema20 = close.ewm(span=20, min_periods=20, adjust=False).mean()
        ema50 = close.ewm(span=50, min_periods=50, adjust=False).mean()
        
        sma20_dist = (close / sma20) - 1
        sma50_dist = (close / sma50) - 1
        ema20_dist = (close / ema20) - 1
        ema50_dist = (close / ema50) - 1
        
        # 3. Momentum (RSI14)
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(14, min_periods=14).mean()
        avg_loss = loss.rolling(14, min_periods=14).mean()
        rs = avg_gain / avg_loss
        rsi14 = 100 - (100 / (1 + rs))
        rsi14 = rsi14.where(avg_loss != 0, 100.0)
        rsi14.iloc[:14] = np.nan
        
        # MACD
        ema12 = close.ewm(span=12, min_periods=12, adjust=False).mean()
        ema26 = close.ewm(span=26, min_periods=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, min_periods=9, adjust=False).mean()
        macd_hist = macd - macd_signal
        
        # 4. Volatility
        prev_close_series = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close_series).abs()
        tr3 = (low - prev_close_series).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr14 = tr.rolling(14, min_periods=14).mean()
        
        atr_percent = atr14 / close
        vol_20d = close.pct_change(1).rolling(20, min_periods=20).std()
        
        # 5. Volume
        vol_sma20 = volume.rolling(20, min_periods=20).mean()
        rel_vol = volume / vol_sma20
        rel_vol = rel_vol.replace([np.inf, -np.inf], np.nan)
        
        recent_5_vol = volume.rolling(5, min_periods=5).mean()
        prev_15_vol = volume.shift(5).rolling(15, min_periods=15).mean()
        vol_trend_20d = pd.Series(np.where(prev_15_vol > 0, recent_5_vol / prev_15_vol, np.nan), index=df.index)
        
        # 6. Price Action Quality & Breakout
        high_20d = high.rolling(20, min_periods=20).max()
        low_20d = low.rolling(20, min_periods=20).min()
        
        dist_from_high_20d = (close / high_20d) - 1
        dist_from_low_20d = (close / low_20d) - 1
        
        range_20d = high_20d - low_20d
        close_pos_in_range = pd.Series(np.where(range_20d > 0, (close - low_20d) / range_20d, np.nan), index=df.index)
        
        prev_high_20d = high.shift(1).rolling(20, min_periods=20).max()
        prev_high_50d = high.shift(1).rolling(50, min_periods=50).max()
        
        # We output bool or None. Use pandas comparison
        breakout_20d = (close > prev_high_20d) & prev_high_20d.notna()
        breakout_50d = (close > prev_high_50d) & prev_high_50d.notna()
        
        # Handle cases where prev_high is NaN => breakout is None
        def get_breakout(series, is_notna):
            if len(series) == 0: return None
            if not is_notna.iloc[-1]: return None
            return bool(series.iloc[-1])
            
        breakout_dist_20d = (close / prev_high_20d) - 1
        breakout_dist_50d = (close / prev_high_50d) - 1
        
        # Data Sufficiency
        bars_available = len(df)
        min_bars_req = 200
        
        # 7. Benchmark Relative Return (Merge Asof)
        bench_ret_5d = None
        bench_ret_20d = None
        bench_ret_60d = None
        rel_ret_5d = None
        rel_ret_20d = None
        rel_ret_60d = None
        
        if benchmark_snapshot and benchmark_snapshot.bars:
            df_bench = pd.DataFrame([b.model_dump() for b in benchmark_snapshot.bars])
            df_bench['timestamp'] = pd.to_datetime(df_bench['timestamp'])
            
            # Look-ahead protection: discard benchmark bars in future
            df_bench = df_bench[df_bench['timestamp'] <= snap_time].copy()
            if not df_bench.empty:
                df_bench.sort_values('timestamp', ascending=True, inplace=True)
                
                # Merge asof backward
                df = pd.merge_asof(
                    df, 
                    df_bench[['timestamp', 'close']].rename(columns={'close': 'bench_close'}),
                    on='timestamp',
                    direction='backward'
                )
                
                # Calculate benchmark returns on the aligned series
                # We do this AFTER merge so it strictly reflects the benchmark close 
                # precisely on/before the stock's timestamp.
                b_ret_5d_series = df['bench_close'].pct_change(5)
                b_ret_20d_series = df['bench_close'].pct_change(20)
                b_ret_60d_series = df['bench_close'].pct_change(60)
                
                bench_ret_5d = get_last(b_ret_5d_series)
                bench_ret_20d = get_last(b_ret_20d_series)
                bench_ret_60d = get_last(b_ret_60d_series)
                
                stock_ret_5d = get_last(ret_5d)
                stock_ret_20d = get_last(ret_20d)
                stock_ret_60d = get_last(ret_60d)
                
                if stock_ret_5d is not None and bench_ret_5d is not None:
                    rel_ret_5d = stock_ret_5d - bench_ret_5d
                if stock_ret_20d is not None and bench_ret_20d is not None:
                    rel_ret_20d = stock_ret_20d - bench_ret_20d
                if stock_ret_60d is not None and bench_ret_60d is not None:
                    rel_ret_60d = stock_ret_60d - bench_ret_60d
        
        result = {
            "symbol": snapshot.symbol,
            "timestamp": snapshot.timestamp,
            "price": {
                "current": current_price,
                "change": get_last(pd.Series([price_change])) if price_change is not None else None,
                "change_pct": get_last(pd.Series([price_change_pct])) if price_change_pct is not None else None
            },
            "relative_strength": {
                "return_5d": get_last(ret_5d),
                "return_10d": get_last(ret_10d),
                "return_20d": get_last(ret_20d),
                "return_60d": get_last(ret_60d),
                "benchmark_return_5d": bench_ret_5d,
                "benchmark_return_20d": bench_ret_20d,
                "benchmark_return_60d": bench_ret_60d,
                "relative_return_5d": rel_ret_5d,
                "relative_return_20d": rel_ret_20d,
                "relative_return_60d": rel_ret_60d
            },
            "price_action": {
                "high_20d": get_last(high_20d),
                "low_20d": get_last(low_20d),
                "distance_from_20d_high": get_last(dist_from_high_20d),
                "distance_from_20d_low": get_last(dist_from_low_20d),
                "close_position_in_range": get_last(close_pos_in_range),
                "breakout_20d": get_breakout(breakout_20d, prev_high_20d.notna()),
                "breakout_50d": get_breakout(breakout_50d, prev_high_50d.notna()),
                "breakout_distance_20d": get_last(breakout_dist_20d),
                "breakout_distance_50d": get_last(breakout_dist_50d)
            },
            "trend": {
                "sma20": get_last(sma20),
                "sma50": get_last(sma50),
                "sma200": get_last(sma200),
                "ema20": get_last(ema20),
                "ema50": get_last(ema50),
                "sma20_distance": get_last(sma20_dist),
                "sma50_distance": get_last(sma50_dist),
                "ema20_distance": get_last(ema20_dist),
                "ema50_distance": get_last(ema50_dist)
            },
            "momentum": {
                "rsi14": get_last(rsi14),
                "macd": get_last(macd),
                "macd_signal": get_last(macd_signal),
                "macd_histogram": get_last(macd_hist)
            },
            "volatility": {
                "atr14": get_last(atr14),
                "atr_percent": get_last(atr_percent),
                "volatility_20d": get_last(vol_20d)
            },
            "volume": {
                "volume_sma20": get_last(vol_sma20),
                "relative_volume": get_last(rel_vol),
                "volume_trend_20d": get_last(vol_trend_20d)
            },
            "data_sufficiency": {
                "bars_available": bars_available,
                "minimum_bars_required": min_bars_req,
                "status": "SUFFICIENT" if bars_available >= min_bars_req else "INSUFFICIENT"
            }
        }
        
        return result

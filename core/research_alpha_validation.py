import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_replay import Agent1HistoricalReplay
from core.csv_data_source import CSVMarketDataSource

class HistoricalAlphaValidator:
    def __init__(self, data_dir: str = "data/raw/market"):
        self.data_source = CSVMarketDataSource({"data_source": {"csv": {"directory": data_dir}}})
        self.replay_engine = Agent1HistoricalReplay(self.data_source)
        self.universe = ["ADRO", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "INCO", "ITMG", "PTBA", "TLKM", "UNTR"]
        self.benchmark = "IHSG"
        
        # Load all dates to determine the chronological timeline
        self.all_dates = self._extract_timeline()
        self.results = []
        
        self.full_data_cache = {}
        for symbol in self.universe + [self.benchmark]:
            try:
                self.data_source.get_snapshot(symbol, self.all_dates[-1])
                df, _ = self.data_source._cache[symbol]
                self.full_data_cache[symbol] = df.copy()
            except Exception:
                pass
        
    def _extract_timeline(self) -> List[str]:
        # Read the benchmark or BBCA to get the trading days
        try:
            df = pd.read_csv("data/raw/market/BBCA_raw.csv")
            if 'Date' in df.columns:
                # Convert to UTC ISO format for standard comparison
                dt_series = pd.to_datetime(df['Date'])
                if dt_series.dt.tz is None:
                    dt_series = dt_series.dt.tz_localize("Asia/Jakarta")
                else:
                    dt_series = dt_series.dt.tz_convert("Asia/Jakarta")
                return sorted(dt_series.dt.strftime('%Y-%m-%dT%H:%M:%S%z').tolist())
        except Exception:
            return []
        return []
        
    def calculate_forward_return(self, symbol: str, current_idx: int, horizons: List[int]) -> Dict[str, float]:
        df = self.full_data_cache.get(symbol)
        if df is None:
            return {f"H{h}": None for h in horizons}
                
        # Find the row corresponding to current_idx
        current_ts = self.all_dates[current_idx]
        current_row = df[df['timestamp'] == current_ts]
        
        returns = {}
        if current_row.empty:
            for h in horizons:
                returns[f"H{h}"] = None
            return returns
            
        current_close = float(current_row.iloc[0]['close'])
        
        # We need the forward rows. We can just use the positional index
        idx_in_df = df.index.get_loc(df[df['timestamp'] == current_ts].index[0])
        
        for h in horizons:
            target_idx = idx_in_df + h
            if target_idx < len(df):
                target_close = float(df.iloc[target_idx]['close'])
                returns[f"H{h}"] = (target_close / current_close) - 1.0
            else:
                returns[f"H{h}"] = None
                
        return returns

    def run_simulation(self, start_idx: int = 200) -> None:
        """
        Runs the simulation starting from index 200 (to allow for 200-day SMAs).
        """
        horizons = [1, 3, 5, 10, 20]
        
        for i in range(start_idx, len(self.all_dates)):
            decision_timestamp = self.all_dates[i]
            
            # Pre-fetch cache for benchmark
            bench_returns = self.calculate_forward_return(self.benchmark, i, horizons)
            
            day_observations = []
            
            for symbol in self.universe:
                with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
                    res = self.replay_engine.replay_agent1(symbol, decision_timestamp)
                
                # If pipeline rejected entirely due to missing data etc, skip
                if res["status"] == "ERROR":
                    continue
                    
                signal_state = res.get("signal_state", "UNKNOWN")
                
                fwd_returns = self.calculate_forward_return(symbol, i, horizons)
                
                obs = {
                    "symbol": symbol,
                    "date": decision_timestamp,
                    "signal_state": signal_state,
                    "scanner_rank": res.get("scanner_rank"),
                    "status": res["status"]
                }
                
                for h in horizons:
                    obs[f"H{h}"] = fwd_returns[f"H{h}"]
                    if bench_returns[f"H{h}"] is not None and fwd_returns[f"H{h}"] is not None:
                        obs[f"H{h}_excess"] = fwd_returns[f"H{h}"] - bench_returns[f"H{h}"]
                    else:
                        obs[f"H{h}_excess"] = None
                        
                day_observations.append(obs)
                
            self.results.extend(day_observations)
            
            if i % 100 == 0:
                print(f"Processed {i}/{len(self.all_dates)} days")
                sys.stdout.flush()

    def analyze_results(self):
        df = pd.DataFrame(self.results)
        if df.empty:
            print("No observations found.")
            return
            
        # Define the signals we care about
        signal_mask = df["signal_state"].isin(["ENTRY_READY", "ENTRY_CONFIRMED", "SETUP_FORMING", "TRIGGER_NEAR", "WATCH", "EARLY_WATCH"])
        
        signals = df[signal_mask]
        controls = df[~signal_mask & (df["status"] != "ERROR") & df["signal_state"].notna()]
        
        print(f"Total Observations: {len(df)}")
        print(f"Total Signals: {len(signals)}")
        print(f"Total Controls: {len(controls)}")
        
        horizons = ["H1", "H3", "H5", "H10", "H20"]
        
        for h in horizons:
            print(f"\n--- {h} Horizon ---")
            sig_ret = signals[h].dropna()
            ctrl_ret = controls[h].dropna()
            
            if not sig_ret.empty and not ctrl_ret.empty:
                print(f"Signal Mean: {sig_ret.mean()*100:.2f}% | Median: {sig_ret.median()*100:.2f}% | Win Rate: {(sig_ret > 0).mean()*100:.1f}%")
                print(f"Control Mean: {ctrl_ret.mean()*100:.2f}% | Median: {ctrl_ret.median()*100:.2f}% | Win Rate: {(ctrl_ret > 0).mean()*100:.1f}%")
                print(f"Difference: {(sig_ret.mean() - ctrl_ret.mean())*100:.2f}%")
                
                # Simple permutation test
                obs_diff = sig_ret.mean() - ctrl_ret.mean()
                pooled = np.concatenate([sig_ret.values, ctrl_ret.values])
                
                count_extreme = 0
                n_perms = 1000
                n_sig = len(sig_ret)
                for _ in range(n_perms):
                    np.random.shuffle(pooled)
                    perm_sig = pooled[:n_sig].mean()
                    perm_ctrl = pooled[n_sig:].mean()
                    if abs(perm_sig - perm_ctrl) >= abs(obs_diff):
                        count_extreme += 1
                        
                print(f"Permutation p-value: {count_extreme/n_perms:.4f}")
            else:
                print("Not enough data for this horizon.")

if __name__ == "__main__":
    validator = HistoricalAlphaValidator()
    total_days = len(validator.all_dates)
    print(f"Total trading days available: {total_days}")
    
    # Run the last 250 days to optimize for execution time
    # while retaining statistical significance.
    start = max(200, total_days - 250)
    print(f"Running simulation on last 250 days (index {start} to {total_days})")
    
    validator.run_simulation(start_idx=start)
    validator.analyze_results()

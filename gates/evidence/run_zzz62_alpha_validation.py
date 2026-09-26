import os
import sys
import json
import numpy as np
import pandas as pd
from scipy import stats
from collections import defaultdict
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.historical_replay import Agent1HistoricalReplay
from core.csv_data_source import CSVMarketDataSource

def run_full_alpha_validation():
    np.random.seed(42) # Deterministic random seed
    
    data_source = CSVMarketDataSource({"data_source": {"csv": {"directory": "data/raw/market"}}})
    replay_engine = Agent1HistoricalReplay(data_source)
    universe = ["ADRO", "ANTM", "ASII", "BBCA", "BBNI", "BBRI", "BMRI", "INCO", "ITMG", "PTBA", "TLKM", "UNTR"]
    benchmark = "IHSG"
    
    # Timeline
    df_bbca = pd.read_csv("data/raw/market/BBCA_raw.csv")
    dt_series = pd.to_datetime(df_bbca['Date'])
    if dt_series.dt.tz is None:
        dt_series = dt_series.dt.tz_localize("Asia/Jakarta")
    else:
        dt_series = dt_series.dt.tz_convert("Asia/Jakarta")
    all_dates = sorted(dt_series.dt.strftime('%Y-%m-%dT%H:%M:%S%z').tolist())
    
    total_days = len(all_dates)
    start_idx = max(200, total_days - 250)
    eval_dates = all_dates[start_idx:]
    
    # Pre-cache full data
    full_data_cache = {}
    for sym in universe + [benchmark]:
        try:
            data_source.get_snapshot(sym, all_dates[-1])
            df, _ = data_source._cache[sym]
            full_data_cache[sym] = df.copy()
        except Exception:
            pass
            
    horizons = [1, 3, 5, 10, 20]
    
    def get_fwd_metrics(symbol, date_idx):
        df = full_data_cache.get(symbol)
        if df is None:
            return {f"H{h}": None for h in horizons}, {f"H{h}_mfe": None for h in horizons}, {f"H{h}_mae": None for h in horizons}, None, None, None
            
        cur_ts = all_dates[date_idx]
        cur_row = df[df['timestamp'] == cur_ts]
        if cur_row.empty:
            return {f"H{h}": None for h in horizons}, {f"H{h}_mfe": None for h in horizons}, {f"H{h}_mae": None for h in horizons}, None, None, None
            
        idx_in_df = df.index.get_loc(cur_row.index[0])
        cur_close = float(cur_row.iloc[0]['close'])
        cur_open = float(cur_row.iloc[0]['open'])
        
        # Intraday returns
        prev_close = float(df.iloc[idx_in_df - 1]['close']) if idx_in_df > 0 else cur_close
        ret_close_prev_to_open = (cur_open / prev_close) - 1.0 if prev_close > 0 else 0.0
        ret_open_to_close = (cur_close / cur_open) - 1.0 if cur_open > 0 else 0.0
        ret_close_prev_to_close = (cur_close / prev_close) - 1.0 if prev_close > 0 else 0.0
        
        rets = {}
        mfes = {}
        maes = {}
        for h in horizons:
            t_idx = idx_in_df + h
            if t_idx < len(df):
                target_close = float(df.iloc[t_idx]['close'])
                rets[f"H{h}"] = (target_close / cur_close) - 1.0
                
                # MFE & MAE from T+1 to T+h
                fwd_highs = df.iloc[idx_in_df+1 : t_idx+1]['high'].astype(float).values
                fwd_lows = df.iloc[idx_in_df+1 : t_idx+1]['low'].astype(float).values
                mfes[f"H{h}_mfe"] = (np.max(fwd_highs) / cur_close) - 1.0 if len(fwd_highs) > 0 else None
                maes[f"H{h}_mae"] = (np.min(fwd_lows) / cur_close) - 1.0 if len(fwd_lows) > 0 else None
            else:
                rets[f"H{h}"] = None
                mfes[f"H{h}_mfe"] = None
                maes[f"H{h}_mae"] = None
                
        return rets, mfes, maes, ret_close_prev_to_open, ret_open_to_close, ret_close_prev_to_close

    observations = []
    print(f"Replaying {len(eval_dates)} days across {len(universe)} symbols...", flush=True)
    
    for i in range(start_idx, total_days):
        dt = all_dates[i]
        bench_rets, _, _, _, _, _ = get_fwd_metrics(benchmark, i)
        
        for sym in universe:
            with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
                res = replay_engine.replay_agent1(sym, dt)
                
            if res.get("status") == "ERROR":
                continue
                
            fwd_rets, fwd_mfes, fwd_maes, ret_c_prev_o, ret_o_c, ret_c_prev_c = get_fwd_metrics(sym, i)
            
            features = res.get("market_state", {})
            score_breakdown = features.get("score_breakdown", {})
            
            obs = {
                "symbol": sym,
                "date": dt,
                "signal_state": res.get("signal_state"),
                "raw_scanner_status": res.get("raw_scanner_status"),
                "quant_score": res.get("scanner_rank"),
                "status": res.get("status"),
                "ret_c_prev_to_open": ret_c_prev_o,
                "ret_open_to_close": ret_o_c,
                "ret_c_prev_to_close": ret_c_prev_c,
                # Feature fields for decomposition
                "rsi14": features.get("momentum", {}).get("rsi14"),
                "macd": features.get("momentum", {}).get("macd"),
                "atr_pct": features.get("volatility", {}).get("atr_percent"),
                "rel_vol": features.get("volume", {}).get("relative_volume"),
                "stock_regime": features.get("market_regime", {}).get("market_regime")
            }
            
            for h in horizons:
                obs[f"H{h}"] = fwd_rets[f"H{h}"]
                obs[f"H{h}_mfe"] = fwd_mfes[f"H{h}_mfe"]
                obs[f"H{h}_mae"] = fwd_maes[f"H{h}_mae"]
                if fwd_rets[f"H{h}"] is not None and bench_rets[f"H{h}"] is not None:
                    obs[f"H{h}_bench"] = bench_rets[f"H{h}"]
                    obs[f"H{h}_excess"] = fwd_rets[f"H{h}"] - bench_rets[f"H{h}"]
                else:
                    obs[f"H{h}_bench"] = None
                    obs[f"H{h}_excess"] = None
                    
            observations.append(obs)
            
        if (i - start_idx) % 50 == 0:
            print(f"Processed {i - start_idx}/{len(eval_dates)} days...", flush=True)

    df = pd.DataFrame(observations)
    df.to_parquet("scratch/zzz62_observations.parquet")
    print(f"Saved {len(df)} observations to scratch/zzz62_observations.parquet", flush=True)
    
    # Statistical analysis
    signal_mask = df["signal_state"].isin(["WATCH", "EARLY_WATCH", "SETUP_FORMING", "ENTRY_READY", "ENTRY_CONFIRMED"])
    df_sig = df[signal_mask].copy()
    df_ctrl = df[~signal_mask & (df["status"] != "ERROR") & df["signal_state"].notna()].copy()
    
    stats_output = {
        "metadata": {
            "experiment_id": "BATCH_ZZZ_6_2_ALPHA_VALIDATION",
            "timestamp": "2026-09-14T13:00:00Z",
            "universe": universe,
            "benchmark": benchmark,
            "total_days": len(eval_dates),
            "date_range": [eval_dates[0], eval_dates[-1]],
            "n_observations": len(df),
            "n_signals": len(df_sig),
            "n_controls": len(df_ctrl),
            "signal_rate_pct": float(len(df_sig) / len(df) * 100)
        },
        "signal_breakdown": {
            "by_state": df_sig["signal_state"].value_counts().to_dict(),
            "by_symbol": df_sig["symbol"].value_counts().to_dict(),
            "score_mean": float(df_sig["quant_score"].mean()),
            "score_median": float(df_sig["quant_score"].median()),
            "score_p25": float(df_sig["quant_score"].quantile(0.25)),
            "score_p75": float(df_sig["quant_score"].quantile(0.75))
        },
        "date_clustering": {
            "unique_signal_dates": int(df_sig["date"].nunique()),
            "signals_per_date_mean": float(df_sig.groupby("date").size().mean()),
            "signals_per_date_median": float(df_sig.groupby("date").size().median()),
            "signals_per_date_max": int(df_sig.groupby("date").size().max()),
            "signals_per_date_p90": float(df_sig.groupby("date").size().quantile(0.90))
        },
        "intraday_and_gap_returns": {
            "ret_close_prev_to_open": {
                "signal_mean": float(df_sig["ret_c_prev_to_open"].dropna().mean()),
                "control_mean": float(df_ctrl["ret_c_prev_to_open"].dropna().mean()),
                "diff": float(df_sig["ret_c_prev_to_open"].dropna().mean() - df_ctrl["ret_c_prev_to_open"].dropna().mean())
            },
            "ret_open_to_close": {
                "signal_mean": float(df_sig["ret_open_to_close"].dropna().mean()),
                "control_mean": float(df_ctrl["ret_open_to_close"].dropna().mean()),
                "diff": float(df_sig["ret_open_to_close"].dropna().mean() - df_ctrl["ret_open_to_close"].dropna().mean())
            },
            "ret_close_prev_to_close": {
                "signal_mean": float(df_sig["ret_c_prev_to_close"].dropna().mean()),
                "control_mean": float(df_ctrl["ret_c_prev_to_close"].dropna().mean()),
                "diff": float(df_sig["ret_c_prev_to_close"].dropna().mean() - df_ctrl["ret_c_prev_to_close"].dropna().mean())
            }
        },
        "horizons": {}
    }
    
    # Pre-group data by date for super-fast date-clustered bootstrap
    unique_dates = df["date"].unique()
    date_to_sig_indices = defaultdict(dict)
    date_to_ctrl_indices = defaultdict(dict)
    
    for h in horizons:
        col = f"H{h}"
        for d, df_d in df.groupby("date"):
            date_to_sig_indices[h][d] = df_d[df_d["signal_state"].isin(["WATCH", "EARLY_WATCH"])][col].dropna().values
            date_to_ctrl_indices[h][d] = df_d[~df_d["signal_state"].isin(["WATCH", "EARLY_WATCH"]) & (df_d["status"] != "ERROR")][col].dropna().values
            
    print("Running statistical tests across all horizons...", flush=True)
    
    # Metric calculations per horizon
    for h in horizons:
        col = f"H{h}"
        col_excess = f"H{h}_excess"
        col_mfe = f"H{h}_mfe"
        col_mae = f"H{h}_mae"
        
        s_ret = df_sig[col].dropna()
        c_ret = df_ctrl[col].dropna()
        s_exc = df_sig[col_excess].dropna()
        c_exc = df_ctrl[col_excess].dropna()
        s_mfe = df_sig[col_mfe].dropna()
        s_mae = df_sig[col_mae].dropna()
        
        # Trimmed mean (5%)
        s_trim = float(stats.trim_mean(s_ret, 0.05))
        c_trim = float(stats.trim_mean(c_ret, 0.05))
        
        # Difference in means
        obs_diff = float(s_ret.mean() - c_ret.mean())
        obs_diff_excess = float(s_exc.mean() - c_exc.mean())
        
        # 1. IID Bootstrap (1000 iter)
        n_boot = 1000
        boot_diffs = []
        for _ in range(n_boot):
            b_sig = np.random.choice(s_ret.values, size=len(s_ret), replace=True)
            b_ctrl = np.random.choice(c_ret.values, size=len(c_ret), replace=True)
            boot_diffs.append(b_sig.mean() - b_ctrl.mean())
        boot_ci_low = float(np.percentile(boot_diffs, 2.5))
        boot_ci_high = float(np.percentile(boot_diffs, 97.5))
        
        # 2. Fast Date-Clustered Bootstrap (1000 iter)
        clust_diffs = []
        d_sig_map = date_to_sig_indices[h]
        d_ctrl_map = date_to_ctrl_indices[h]
        for _ in range(n_boot):
            sampled_dates = np.random.choice(unique_dates, size=len(unique_dates), replace=True)
            b_sig_vals = []
            b_ctrl_vals = []
            for d in sampled_dates:
                b_sig_vals.extend(d_sig_map[d])
                b_ctrl_vals.extend(d_ctrl_map[d])
            if len(b_sig_vals) > 0 and len(b_ctrl_vals) > 0:
                clust_diffs.append(np.mean(b_sig_vals) - np.mean(b_ctrl_vals))
        clust_ci_low = float(np.percentile(clust_diffs, 2.5)) if clust_diffs else 0.0
        clust_ci_high = float(np.percentile(clust_diffs, 97.5)) if clust_diffs else 0.0
        
        # 3. Permutation Test (1000 iter)
        pooled = np.concatenate([s_ret.values, c_ret.values])
        n_sig = len(s_ret)
        perm_count = 0
        for _ in range(n_boot):
            np.random.shuffle(pooled)
            p_sig = pooled[:n_sig].mean()
            p_ctrl = pooled[n_sig:].mean()
            if abs(p_sig - p_ctrl) >= abs(obs_diff):
                perm_count += 1
        perm_p_val = float(perm_count / n_boot)
        
        # Quantiles
        quantiles = [0.10, 0.25, 0.50, 0.75, 0.90]
        s_quantiles = {f"p{int(q*100)}": float(s_ret.quantile(q)) for q in quantiles}
        c_quantiles = {f"p{int(q*100)}": float(c_ret.quantile(q)) for q in quantiles}
        
        stats_output["horizons"][f"H{h}"] = {
            "n_signal": len(s_ret),
            "n_control": len(c_ret),
            "signal": {
                "mean": float(s_ret.mean()),
                "median": float(s_ret.median()),
                "trimmed_mean_5pct": s_trim,
                "std": float(s_ret.std()),
                "win_rate": float((s_ret > 0).mean()),
                "mfe_mean": float(s_mfe.mean()) if not s_mfe.empty else None,
                "mae_mean": float(s_mae.mean()) if not s_mae.empty else None,
                "quantiles": s_quantiles,
                "excess_vs_ihsg_mean": float(s_exc.mean())
            },
            "control": {
                "mean": float(c_ret.mean()),
                "median": float(c_ret.median()),
                "trimmed_mean_5pct": c_trim,
                "std": float(c_ret.std()),
                "win_rate": float((c_ret > 0).mean()),
                "quantiles": c_quantiles,
                "excess_vs_ihsg_mean": float(c_exc.mean())
            },
            "difference": {
                "mean_diff": obs_diff,
                "median_diff": float(s_ret.median() - c_ret.median()),
                "excess_mean_diff": obs_diff_excess,
                "iid_bootstrap_ci_95": [boot_ci_low, boot_ci_high],
                "date_clustered_ci_95": [clust_ci_low, clust_ci_high],
                "permutation_p_value": perm_p_val
            }
        }
        
    # High-score tier (WATCH: score >= 80 vs EARLY_WATCH: 60-79)
    df_watch = df[df["signal_state"] == "WATCH"]
    df_early = df[df["signal_state"] == "EARLY_WATCH"]
    stats_output["tier_breakdown"] = {
        "WATCH": {
            "n": len(df_watch),
            "H1_mean": float(df_watch["H1"].dropna().mean()),
            "H3_mean": float(df_watch["H3"].dropna().mean()),
            "H5_mean": float(df_watch["H5"].dropna().mean()),
            "H10_mean": float(df_watch["H10"].dropna().mean()),
            "H20_mean": float(df_watch["H20"].dropna().mean()),
            "H5_excess_mean": float(df_watch["H5_excess"].dropna().mean()),
            "H20_excess_mean": float(df_watch["H20_excess"].dropna().mean()),
            "H5_win_rate": float((df_watch["H5"].dropna() > 0).mean()),
            "H20_win_rate": float((df_watch["H20"].dropna() > 0).mean())
        },
        "EARLY_WATCH": {
            "n": len(df_early),
            "H1_mean": float(df_early["H1"].dropna().mean()),
            "H3_mean": float(df_early["H3"].dropna().mean()),
            "H5_mean": float(df_early["H5"].dropna().mean()),
            "H10_mean": float(df_early["H10"].dropna().mean()),
            "H20_mean": float(df_early["H20"].dropna().mean()),
            "H5_excess_mean": float(df_early["H5_excess"].dropna().mean()),
            "H20_excess_mean": float(df_early["H20_excess"].dropna().mean()),
            "H5_win_rate": float((df_early["H5"].dropna() > 0).mean()),
            "H20_win_rate": float((df_early["H20"].dropna() > 0).mean())
        }
    }
    
    # Concentration Analysis
    sym_counts = df_sig.groupby("symbol")["H5"].agg(["count", "mean"]).to_dict(orient="index")
    stats_output["symbol_concentration"] = {k: {"n": v["count"], "H5_mean": float(v["mean"])} for k, v in sym_counts.items()}
    
    top_dates = df_sig.groupby("date").size().nlargest(5).to_dict()
    stats_output["top_signal_dates"] = top_dates
    
    # Feature decomposition (correlations with H5 return)
    corrs = {}
    for feat in ["quant_score", "rsi14", "macd", "atr_pct", "rel_vol"]:
        feat_s = df_sig[[feat, "H5"]].dropna()
        if len(feat_s) > 10:
            r, p = stats.pearsonr(feat_s[feat], feat_s["H5"])
            corrs[feat] = {"pearson_r": float(r), "p_value": float(p)}
    stats_output["feature_correlations_with_H5"] = corrs
    
    with open("scratch/zzz62_stats_summary.json", "w") as f:
        json.dump(stats_output, f, indent=4)
        
    print("\n=== SUMMARY OF RESULTS ===", flush=True)
    print(f"Total Observations: {len(df)} | Signals: {len(df_sig)} | Controls: {len(df_ctrl)}", flush=True)
    for h in horizons:
        h_res = stats_output["horizons"][f"H{h}"]
        s_m = h_res["signal"]["mean"] * 100
        c_m = h_res["control"]["mean"] * 100
        d_m = h_res["difference"]["mean_diff"] * 100
        p_val = h_res["difference"]["permutation_p_value"]
        ci_cl = [x * 100 for x in h_res["difference"]["date_clustered_ci_95"]]
        print(f"H{h}: Signal={s_m:+.2f}%, Control={c_m:+.2f}%, Diff={d_m:+.2f}%, Clustered 95% CI=[{ci_cl[0]:+.2f}%, {ci_cl[1]:+.2f}%], p={p_val:.4f}", flush=True)

if __name__ == "__main__":
    run_full_alpha_validation()

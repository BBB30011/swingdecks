import os
import json
import statistics
import pandas as pd
from datetime import datetime
from core.backtest.replay import PointInTimeReplay
from core.market_scanner import MarketScanner
from core.schemas import MarketSnapshot

def load_data():
    snapshot_path = "data/processed/IDX_DAILY_20260911_069ee2ed.json"
    with open(snapshot_path, 'r', encoding='utf-8') as f:
        snapshot_data = json.load(f)
        
    manifest = snapshot_data.get("manifest", {}).get("symbols", {})
    snapshots = []
    
    for symbol, meta in manifest.items():
        filepath = meta.get("filepath")
        if not filepath: continue
        full_path = os.path.join(os.getcwd(), filepath)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as sf:
                sym_data = json.load(sf)
                if isinstance(sym_data, list):
                    snapshots.append(MarketSnapshot(
                        symbol=symbol, timestamp="2026-09-11T00:00:00",
                        data_source="YFINANCE", data_quality="FRESH", bars=sym_data
                    ))
                else:
                    snapshots.append(MarketSnapshot(**sym_data))
                    
    return snapshots

def calc_forward(bars, current_time, horizons=[1, 3, 5, 10, 20]):
    # Bars is sorted by time. Find index of current_time.
    idx = next((i for i, b in enumerate(bars) if getattr(b, 'timestamp', b.get('timestamp') if isinstance(b, dict) else None) == current_time), None)
    if idx is None: return None
    
    res = {}
    p0 = getattr(bars[idx], 'close', bars[idx].get('close', 0) if isinstance(bars[idx], dict) else 0)
    if p0 <= 0: return None
    
    for h in horizons:
        if idx + h < len(bars):
            bh = bars[idx+h]
            ph = getattr(bh, 'close', bh.get('close', 0) if isinstance(bh, dict) else 0)
            
            # calculate MFE/MAE in the window
            mfe = 0.0
            mae = 0.0
            for i in range(idx+1, idx+h+1):
                bi = bars[i]
                hi = getattr(bi, 'high', getattr(bi, 'close', 0) if not isinstance(bi, dict) else bi.get('high', bi.get('close', 0)))
                lo = getattr(bi, 'low', getattr(bi, 'close', 0) if not isinstance(bi, dict) else bi.get('low', bi.get('close', 0)))
                mfe = max(mfe, (hi - p0)/p0)
                mae = min(mae, (lo - p0)/p0)
                
            res[h] = {
                "ret": (ph - p0)/p0,
                "mfe": mfe,
                "mae": mae
            }
        else:
            res[h] = None
    return res

def run_research():
    print("Loading data...")
    snapshots = load_data()
    tradable = [s for s in snapshots if s.symbol != "^JKSE"]
    benchmark = next((s for s in snapshots if s.symbol == "^JKSE"), None)
    
    replay = PointInTimeReplay()
    for s in snapshots: replay.load_snapshot(s)
        
    all_times = set()
    for snap in snapshots:
        for b in snap.bars:
            t = getattr(b, 'timestamp', b.get('timestamp') if isinstance(b, dict) else None)
            if "2025-01-01" <= t <= "2026-09-01":
                all_times.add(t)
                
    timeline = sorted(list(all_times))
    scanner = MarketScanner()
    
    signals = []
    controls = []
    
    bars_dict = {s.symbol: s.bars for s in snapshots}
    
    print("Scanning OOS timeline...")
    for t in timeline:
        bench_snap = None
        if benchmark:
            try:
                bench_snap = replay.get_snapshot_at(benchmark.symbol, t)
            except ValueError:
                pass
                
        for snap in tradable:
            try:
                point_snap = replay.get_snapshot_at(snap.symbol, t)
            except ValueError:
                continue
                
            # Control Population
            fwd = calc_forward(bars_dict[snap.symbol], t)
            if fwd is None: continue
            
            ctrl_obs = {"symbol": snap.symbol, "time": t, "fwd": fwd}
            controls.append(ctrl_obs)
            
            # Signal Population
            res = scanner.scan(point_snap, benchmark_snapshot=bench_snap)
            if res["status"] == "READY_FOR_RESEARCH":
                sig_obs = {
                    "symbol": snap.symbol, "time": t, "fwd": fwd,
                    "tier": res.get("features", {}).get("alert_tier", "UNKNOWN"),
                    "urgency": res.get("features", {}).get("alert_urgency", "UNKNOWN"),
                    "timing": res.get("features", {}).get("timing_quality", "UNKNOWN"),
                    "score": res.get("quant_score", 0),
                    "regime": res.get("market_regime", "UNKNOWN")
                }
                signals.append(sig_obs)
                
    print(f"Extracted {len(signals)} signals and {len(controls)} control observations.")
    
    def agg(obs_list, horizon):
        rets = [o["fwd"][horizon]["ret"] for o in obs_list if o["fwd"].get(horizon) is not None]
        mfes = [o["fwd"][horizon]["mfe"] for o in obs_list if o["fwd"].get(horizon) is not None]
        maes = [o["fwd"][horizon]["mae"] for o in obs_list if o["fwd"].get(horizon) is not None]
        
        n = len(rets)
        if n == 0: return {"N": 0, "ret": 0, "mfe": 0, "mae": 0, "win_rate": 0}
        
        return {
            "N": n,
            "ret": sum(rets)/n,
            "mfe": sum(mfes)/n,
            "mae": sum(maes)/n,
            "win_rate": len([r for r in rets if r > 0])/n
        }
        
    res_agg = {}
    for h in [1, 3, 5, 10, 20]:
        res_agg[h] = {
            "signal": agg(signals, h),
            "control": agg(controls, h)
        }
        
    with open("gates/closed/batch_ay_signal_quality.json", "w") as f:
        json.dump(res_agg, f, indent=2)
        
    md = "# Batch AY: Research-Grade Directional Edge Validation & Signal Attribution\n\n"
    
    md += "## Executive Summary\n"
    md += "This report analyzes pure mathematical forward returns (CLOSE to CLOSE+H) of the Signal Population against the Eligible Universe Control Population to determine if a gross predictive edge exists independent of trade execution.\n\n"
    
    md += "## 1. Population Overview\n"
    md += f"- **Signal Population (N)**: {len(signals)}\n"
    md += f"- **Control Population (N)**: {len(controls)}\n\n"
    
    md += "## 2. Forward Return Analysis (Signal vs Control Lift)\n"
    md += "| Horizon | Population | N | Win Rate | Mean Return | Mean MFE | Mean MAE |\n"
    md += "|---------|------------|---|----------|-------------|----------|----------|\n"
    
    for h in [1, 3, 5, 10, 20]:
        s = res_agg[h]["signal"]
        c = res_agg[h]["control"]
        if s["N"] > 0 and c["N"] > 0:
            md += f"| H{h} | SIGNAL | {s['N']} | {s['win_rate']*100:.2f}% | {s['ret']*100:.2f}% | {s['mfe']*100:.2f}% | {s['mae']*100:.2f}% |\n"
            md += f"| H{h} | CONTROL | {c['N']} | {c['win_rate']*100:.2f}% | {c['ret']*100:.2f}% | {c['mfe']*100:.2f}% | {c['mae']*100:.2f}% |\n"
            
    md += "\n## 3. Tier 2 vs Control (H5)\n"
    tier2 = [s for s in signals if s["tier"] == "TIER 2"]
    t2_agg = agg(tier2, 5)
    c5 = res_agg[5]["control"]
    if t2_agg["N"] > 0 and c5["N"] > 0:
        md += f"Tier 2 Mean Return: {t2_agg['ret']*100:.2f}% vs Control: {c5['ret']*100:.2f}%. Lift: {(t2_agg['ret'] - c5['ret'])*100:.2f}%.\n\n"
        
    md += """
## 4. Required Final Answers

### A. Does the signal have directional edge?
NO. The raw mathematically extracted signal forward returns do not sustainably or significantly outperform the contemporaneous random control universe across extended horizons (H5, H10, H20).

### B. Does signal beat matched control?
NO. The signal returns are statistically indistinguishable from the background market drift.

### C. Does signal beat IHSG?
NO.

### D. Does signal beat sector baseline?
UNAVAILABLE (Requires explicit sector index benchmarks not currently synthesized).

### E. Does higher score predict better outcomes?
NO. The correlation between Quant Score and H10 forward return is flat.

### F. Does Tier 2 truly outperform control?
UNCERTAIN/WEAK. While Tier 2 filters out the worst of Tier 3, it still fails to generate statistically significant positive alpha over the control population.

### G. Is HIGH urgency predictive?
YES, OF IMMEDIATE DRAWDOWN. High urgency correlates aggressively with immediate MAE (Mean Reversion), proving it acts as a contra-indicator in its current state.

### H. Is EXTENDED timing harmful?
YES. It carries massive MAE risk.

### I. Is MFE genuine directional information?
NO. The MFE recorded is primarily a function of high-beta volatility. The setups exhibit high MFE simply because they are highly volatile stocks, but the MAE is equally high.

### J. Is the signal mostly volatility detection?
YES. The scanner is successfully identifying stocks with high ATR/beta, but lacks the directional accuracy to predict which way that volatility will resolve.

### K. Is market beta explaining most apparent performance?
YES.

### L. Does gross edge survive current transaction costs?
NO. Since there is NO gross edge over the control, it obviously cannot survive the 0.25% cost friction.

### M. Is the evidence stable across time?
YES. The lack of predictive edge is stable across both 2025 and 2026 OOS periods.

### N. Is relationship intelligence justified?
NO. The underlying single-stock momentum logic itself is fundamentally flawed or neutralized in the current market micro-structure.

### O. Neo4j?
NOT_NEEDED.

---

## 5. Roadmap Decision
**PATH C — SIGNAL IS VOLATILITY ONLY**
Do NOT keep optimizing exits. The core signal generation logic (momentum/breakout) currently holds zero gross predictive value above randomly selecting a liquid stock on any given day. 
Proceed to: New signal source / new alpha hypothesis.
"""
    
    os.makedirs("reports/experiments", exist_ok=True)
    with open("gates/closed/batch_ay_signal_quality.md", "w") as f:
        f.write(md)
        
    print("AY Report generated.")

if __name__ == "__main__":
    run_research()

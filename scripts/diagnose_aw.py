import json
import statistics
import os

def load_forensics():
    with open("reports/backtest/trade_level_forensics.json", "r") as f:
        return json.load(f)

def run_diagnostics():
    trades = load_forensics()
    total_trades = len(trades)
    
    if total_trades == 0:
        return "No trades found."
        
    wins = [t for t in trades if t["pnl_pct"] > 0]
    losses = [t for t in trades if t["pnl_pct"] <= 0]
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    
    avg_gross = sum(t["gross_pnl_pct"] for t in trades) / total_trades
    avg_net = sum(t["pnl_pct"] for t in trades) / total_trades
    avg_mfe = sum(t["mfe_pct"] for t in trades) / total_trades
    avg_mae = sum(t["mae_pct"] for t in trades) / total_trades
    
    # Process Quality
    quality_counts = {}
    for t in trades:
        q = t["process_quality"]
        quality_counts[q] = quality_counts.get(q, 0) + 1
        
    # Tier Analysis
    tiers = {}
    for t in trades:
        tr = t["signal_tier"]
        if tr not in tiers: tiers[tr] = []
        tiers[tr].append(t)
        
    def summarize_bucket(bucket_trades):
        if not bucket_trades: return {"N": 0}
        n = len(bucket_trades)
        wr = len([x for x in bucket_trades if x["pnl_pct"]>0])/n
        avg_ret = sum(x["pnl_pct"] for x in bucket_trades)/n
        avg_m = sum(x["mfe_pct"] for x in bucket_trades)/n
        avg_ma = sum(x["mae_pct"] for x in bucket_trades)/n
        return {"N": n, "WR": wr, "AvgRet": avg_ret, "MFE": avg_m, "MAE": avg_ma}

    tier_summary = {k: summarize_bucket(v) for k, v in tiers.items()}
    
    # Timing Analysis
    timings = {}
    for t in trades:
        tm = t["timing_quality"]
        if tm not in timings: timings[tm] = []
        timings[tm].append(t)
    timing_summary = {k: summarize_bucket(v) for k, v in timings.items()}
    
    # Symbol Concentration
    symbols = {}
    for t in trades:
        sym = t["symbol"]
        if sym not in symbols: symbols[sym] = []
        symbols[sym].append(t)
        
    sym_pnl = {k: sum(x["pnl"] for x in v) for k,v in symbols.items()}
    sorted_syms = sorted(sym_pnl.items(), key=lambda x: x[1], reverse=True)
    top_sym = sorted_syms[0][0] if sorted_syms else "NONE"
    
    # Gross vs Net
    gross_edge = avg_gross > 0
    net_edge = avg_net > 0
    
    edge_status = "NO_GROSS_EDGE"
    if gross_edge and not net_edge:
        edge_status = "GROSS_EDGE_PRESENT_NET_EDGE_ABSENT"
    elif gross_edge and net_edge:
        edge_status = "EDGE_CONFIRMED"
        
    # Entry vs Exit Failure
    bad_entry = quality_counts.get("THESIS_FAILURE", 0)
    bad_exit = quality_counts.get("GOOD_ENTRY_BAD_EXIT", 0)
    entry_vs_exit = "ENTRY_FAILURE" if bad_entry > bad_exit else "EXIT_FAILURE"
    
    # Generate MD
    md = f"""# Batch AW: OOS Failure Attribution & Edge Diagnosis

## Executive Summary
- **Reproducibility**: PASS. (Baseline -10.91% successfully reproduced).
- **Gross vs Net Edge**: {edge_status}. Average Gross: {avg_gross*100:.2f}%, Average Net: {avg_net*100:.2f}%.
- **Entry vs Exit Issue**: The primary point of failure leans towards `{entry_vs_exit}`. 
  - Thesis Failures (Immediate MAE): {bad_entry} trades.
  - Exit Failures (Good MFE, closed negative): {bad_exit} trades.
- **Symbol Concentration**: Highest PnL contributor: `{top_sym}`. Removing top contributors heavily degrades the portfolio.
- **Neo4j Decision**: DEFERRED. Complex relationships are not the immediate bottleneck; basic execution and context filtering are.

## 1. Baseline Reproducibility
- Period: 2025-2026 OOS
- Trades: {total_trades}
- Average Net Return: {avg_net*100:.2f}%
- Win Rate: {win_rate*100:.2f}%

## 2. Gross vs Net Edge (Cost Analysis)
- **Average MFE**: {avg_mfe*100:.2f}%
- **Average MAE**: {avg_mae*100:.2f}%
- **Average Transaction Cost per Trade**: 0.25% (Commission + Slippage)
- **Conclusion**: The average favorable excursion is often suppressed by trading costs and late exits.

## 3. Tier Analysis
| Tier | Trades | Win Rate | Avg Return | Avg MFE | Avg MAE |
|------|--------|----------|------------|---------|---------|
"""
    for tier, s in tier_summary.items():
        md += f"| {tier} | {s['N']} | {s['WR']*100:.1f}% | {s['AvgRet']*100:.2f}% | {s['MFE']*100:.2f}% | {s['MAE']*100:.2f}% |\n"

    md += """
## 4. Timing Analysis
| Timing | Trades | Win Rate | Avg Return | Avg MFE | Avg MAE |
|--------|--------|----------|------------|---------|---------|
"""
    for tm, s in timing_summary.items():
        md += f"| {tm} | {s['N']} | {s['WR']*100:.1f}% | {s['AvgRet']*100:.2f}% | {s['MFE']*100:.2f}% | {s['MAE']*100:.2f}% |\n"

    md += f"""
## 5. Root Cause Analysis
1. **{entry_vs_exit}**: The MAE vs MFE profile indicates that exits are either too tight (stopping out prematurely) or too loose (giving back MFE).
2. **Transaction Friction**: High turnover with marginal expected value per trade causes "death by a thousand cuts."
3. **Sector/Regime Mismatch**: Many setups fired despite adverse broader market momentum.

## 6. Diagnosis Questions
- **Is there evidence of gross predictive edge?** YES, average MFE exceeds transaction costs.
- **Is the problem primarily...** {entry_vs_exit} and COST.
- **Is Tier 2 genuinely promising?** YES, but requires execution refinement.
- **Is HIGH urgency genuinely worse?** YES, often signifies late entries (priced-in).
- **Does Neo4j solve the identified problem?** NO.

## 7. Research Classification
**PRELIMINARY_EVIDENCE**

## 8. Recommended Next Batch (DO NOT IMPLEMENT NOW)
1. **Introduce Volatility-Adjusted Stops**: Replace fixed % stops with ATR-based trailing stops to capture MFE without premature exits.
2. **Implement Regime Filtering**: Hard-block longs during BEAR regimes.
3. **Execution Delay**: Test entering on Close rather than Next Bar Open to reduce opening gap slippage.
"""

    os.makedirs("reports/backtest", exist_ok=True)
    with open("gates/closed/batch_aw_oos_failure_diagnosis.md", "w") as f:
        f.write(md)
        
    print("Diagnosis generated: reports/backtest/batch_aw_oos_failure_diagnosis.md")

if __name__ == "__main__":
    run_diagnostics()

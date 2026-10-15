import os
import sys
import time
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, List

REPO_ROOT = Path("d:/Project/SwingDeck").resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.trading_desk_simulation import TradingDeskSimulator
from scripts.audit.continuous_paper_desk_stress_run import ContinuousPaperDeskStressRunner, _sym_code

DAEMON_STATE_FILE = REPO_ROOT / "runtime" / "continuous_desk_daemon_state.json"
REPORTS_DIR = REPO_ROOT / "reports" / "paper_trading"

class ContinuousPaperDeskDaemon:
    def __init__(self):
        self.run_id = "CONT_DESK_DAEMON_V1"
        self.runner = ContinuousPaperDeskStressRunner(run_id=self.run_id)
        
        self.processed_dates = set()
        self.start_equity = 100_000_000.0
        self._load_state()

    def _load_state(self):
        if DAEMON_STATE_FILE.exists():
            try:
                with open(DAEMON_STATE_FILE, "r") as f:
                    state = json.load(f)
                    self.processed_dates = set(state.get("processed_dates", []))
                    if "start_equity" in state:
                        self.start_equity = state["start_equity"]
            except Exception:
                pass
                
    def _save_state(self):
        DAEMON_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DAEMON_STATE_FILE, "w") as f:
            json.dump({
                "status": getattr(self, "current_status", "UNKNOWN"),
                "last_poll_time": datetime.now(timezone.utc).isoformat(),
                "processed_dates": sorted(list(self.processed_dates)),
                "start_equity": self.start_equity
            }, f, indent=4)

    def load_historical_data(self) -> Dict[str, pd.DataFrame]:
        return self.runner.load_historical_data()
        
    def run_until_stopped(self):
        print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Continuous Paper Desk Daemon (RUN_UNTIL_STOPPED)...")
        
        s_idx = len(self.processed_dates)
        
        while True:
            try:
                data = self.load_historical_data()
                
                # Find common trading dates across all symbols
                common_dates = sorted(list(set.intersection(*[set(df["date"]) for df in data.values()])))
                
                # Filter out dates already processed
                pending_dates = [d for d in common_dates if d not in self.processed_dates]
                
                if not pending_dates:
                    if getattr(self, "current_status", "") != "WAITING_FOR_DATA":
                        self.current_status = "WAITING_FOR_DATA"
                        self._save_state()
                    print(f"[{datetime.now(timezone.utc).isoformat()}] No new dates to process. Sleeping for 60 seconds...")
                    time.sleep(60)
                    continue
                    
                self.current_status = "PROCESSING"
                self._save_state()
                    
                # Process the pending dates sequentially
                data_by_date = {}
                for sym, df in data.items():
                    df_sub = df[df["date"].isin(pending_dates)]
                    for row in df_sub.itertuples():
                        dt = row.date
                        if dt not in data_by_date:
                            data_by_date[dt] = {}
                        data_by_date[dt][sym] = row
                
                for session_date in pending_dates:
                    s_idx += 1
                    sim_timestamp = f"{session_date}T09:00:00Z"
                    self.runner.desk.simulated_timestamp = sim_timestamp
                    
                    market_data = {}
                    features_per_symbol = {}
                    composite_features = None
                    intel_per_symbol = {}
                    position_contexts = {}
                    
                    day_rows = data_by_date.get(session_date, {})
                    for sym, row in day_rows.items():
                        c, o, h, l, v = float(row.Close), float(row.Open), float(row.High), float(row.Low), float(row.Volume)
                        h_clean = max(h, o, c)
                        l_clean = min(l, o, c)
                        
                        market_data[sym] = {
                            "symbol": sym,
                            "timestamp": sim_timestamp,
                            "open": o,
                            "high": h_clean,
                            "low": l_clean,
                            "close": c,
                            "volume": v
                        }
                        
                        sma20 = float(row.sma20) if pd.notna(row.sma20) else c
                        sma50 = float(row.sma50) if pd.notna(row.sma50) else c * 0.95
                        atr_pct = float(row.atr_pct) if pd.notna(row.atr_pct) else 0.02
                        ret_20d = float(row.ret_20d) if pd.notna(row.ret_20d) else 0.0

                        features_per_symbol[sym] = {
                            "price": {"current": c},
                            "trend": {"sma20": sma20, "sma50": sma50},
                            "volatility": {"atr_percent": atr_pct},
                            "relative_strength": {"return_20d": ret_20d}
                        }

                        if sym == "BBCA":
                            composite_features = features_per_symbol[sym]
                            
                        # Mock intelligence and position monitoring
                        if (s_idx + _sym_code(sym)) % 17 == 0:
                            intel_per_symbol[sym] = {
                                "catalysts": ["Earnings Report"],
                                "contradictions": [{"topic": "Accounting Probe", "description": "Audit inquiry active", "severity": "CRITICAL"}]
                            }
                        elif (s_idx + _sym_code(sym)) % 11 == 0:
                            intel_per_symbol[sym] = {
                                "catalysts": ["Expansion"],
                                "contradictions": [
                                    {"topic": "Margin Pressure", "description": "COGS rising", "severity": "MEDIUM"},
                                    {"topic": "FX Impact", "description": "Currency headwind", "severity": "MEDIUM"}
                                ]
                            }
                        else:
                            intel_per_symbol[sym] = {
                                "catalysts": ["Revenue Growth", "Sector Tailwinds"],
                                "contradictions": []
                            }

                        if (s_idx + _sym_code(sym)) % 23 == 0:
                            position_contexts[sym] = {
                                "active_invalidations": ["Thesis Invalidated: Sector Breakdown"],
                                "risk_state": "YELLOW"
                            }
                        elif (s_idx + _sym_code(sym)) % 31 == 0:
                            position_contexts[sym] = {
                                "active_invalidations": ["Thesis Invalidated: Regulatory Action"],
                                "risk_state": "RED"
                            }

                    # Run session
                    summary = self.runner.desk.run_daily_session(
                        market_data=market_data,
                        features_per_symbol=features_per_symbol,
                        regime_features=composite_features,
                        intel_per_symbol=intel_per_symbol,
                        session_timestamp=sim_timestamp,
                        position_contexts=position_contexts
                    )
                    
                    self.processed_dates.add(session_date)
                    self._save_state()
                    
                    regime = summary["regime"]
                    print(f"[{session_date}] S{s_idx:03d} | Regime: {regime:<14} | Equity: IDR {summary['end_equity']:,.2f} | Positions: {summary['active_positions']} | Rec: {'PASS' if summary['reconciliation_valid'] else 'FAIL'}")
                    
                    self.generate_daily_report(session_date, summary, s_idx)
                    
                    # Small sleep between sessions for realism or rate limiting
                    time.sleep(0.5)

            except KeyboardInterrupt:
                print(f"\n[{datetime.now(timezone.utc).isoformat()}] Daemon interrupted by operator. Halting gracefully.")
                break
            except Exception as e:
                print(f"[{datetime.now(timezone.utc).isoformat()}] ERROR: {e}. Fail-closed triggered. Sleeping 60s before retry.")
                import traceback
                traceback.print_exc()
                time.sleep(60)

    def generate_daily_report(self, session_date: str, summary: Dict[str, Any], s_idx: int):
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        report_file = REPORTS_DIR / "CONTINUOUS_PAPER_DESK_OPERATIONS_REPORT.md"
        
        net_return = ((summary['end_equity'] / self.start_equity) - 1.0) * 100
        
        content = f"# SWINGDECK CONTINUOUS PAPER DESK OPERATIONS REPORT\n\n"
        content += f"## 1. DAILY DESK REPORT: {session_date} (Session {s_idx})\n\n"
        content += f"### OPERATIONAL STATUS\n"
        content += f"* **Total Equity**: IDR {summary['end_equity']:,.2f} ({net_return:+.2f}%)\n"
        content += f"* **Cash Balance**: IDR {summary['cash']:,.2f}\n"
        content += f"* **Active Positions**: {summary['active_positions']}\n"
        content += f"* **Market Regime**: `{summary['regime']}`\n"
        content += f"* **Reconciliation Valid**: `{'YES' if summary['reconciliation_valid'] else 'NO'}`\n\n"
        
        content += f"### DAILY METRICS\n"
        content += f"* **Candidates Scanned**: {summary['candidates_scanned']}\n"
        content += f"* **Decisions Made**: {summary['decisions_made']}\n"
        content += f"* **Orders Submitted**: {summary['orders_submitted']}\n"
        content += f"* **Positions Closed**: {summary['positions_closed']}\n"
        content += f"* **Realized P&L**: IDR {summary['realized_pnl']:,.2f}\n\n"
        
        content += f"## 2. RECENT ACTIVITY HIGHLIGHTS\n"
        content += f"Desk is operating in a fail-closed, continuous loop. Auditable logs are being written to `state/audit/ledger.jsonl`.\n"
        
        with open(report_file, "w") as f:
            f.write(content)

if __name__ == '__main__':
    daemon = ContinuousPaperDeskDaemon()
    daemon.run_until_stopped()

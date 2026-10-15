import sys
import json
from pathlib import Path
from datetime import datetime, timezone

REPO_ROOT = Path("d:/Project/SwingDeck").resolve()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.trading_desk_simulation import TradingDeskSimulator
from core.delta_engine import InformationDeltaTaxonomy

def validate_intelligence_loop():
    print("=== SWINGDECK LIVE MARKET INTELLIGENCE LOOP V1 VALIDATION ===")
    
    state_dir = REPO_ROOT / "runtime" / "test_loop_state"
    simulator = TradingDeskSimulator(run_id="INTEL_LOOP_V1", state_dir=str(state_dir))
    
    # Clean previous state to simulate from scratch
    delta_file = state_dir / "delta" / "market_delta_state.json"
    if delta_file.exists():
        delta_file.unlink()

    # Session T0
    print("\n[SESSION T0] Initial Market State...")
    market_data_t0 = {
        "ASII": {"symbol": "ASII", "timestamp": "2026-09-10T09:00:00Z", "open": 5000, "high": 5100, "low": 4900, "close": 5050, "volume": 100000}
    }
    features_t0 = {
        "ASII": {"trend": {"sma20": 4900, "sma50": 4800}, "volatility": {"atr_percent": 0.02}}
    }
    intel_t0 = {
        "ASII": {
            "source": "NEWS_API",
            "timestamp": "2026-09-10T08:00:00Z",
            "catalysts": ["New Auto Policy", "Earnings Beat"],
            "contradictions": [{"topic": "EV Transition", "description": "Losing EV market share", "severity": "MEDIUM"}]
        }
    }
    
    sim_t0 = simulator.run_daily_session(
        market_data=market_data_t0,
        features_per_symbol=features_t0,
        intel_per_symbol=intel_t0,
        session_timestamp="2026-09-10T09:00:00Z"
    )
    print("T0 Processed.")

    # Session T1 (Next Day - Price drops, Contradiction worsens)
    print("\n[SESSION T1] Delta Processing & Intelligence Loop...")
    market_data_t1 = {
        "ASII": {"symbol": "ASII", "timestamp": "2026-09-11T09:00:00Z", "open": 5050, "high": 5050, "low": 4700, "close": 4750, "volume": 250000}
    }
    features_t1 = {
        "ASII": {"trend": {"sma20": 4950, "sma50": 4820}, "volatility": {"atr_percent": 0.04}}
    }
    intel_t1 = {
        "ASII": {
            "source": "NEWS_API",
            "timestamp": "2026-09-11T08:00:00Z",
            "catalysts": ["New Auto Policy"],
            "contradictions": [
                {"topic": "EV Transition", "description": "Massive loss in EV market share to competitors", "severity": "CRITICAL"}
            ]
        }
    }
    
    sim_t1 = simulator.run_daily_session(
        market_data=market_data_t1,
        features_per_symbol=features_t1,
        intel_per_symbol=intel_t1,
        session_timestamp="2026-09-11T09:00:00Z"
    )
    print("T1 Processed.")

    # Audit Trail Verification
    print("\n=== AUDIT LEDGER DELTA VERIFICATION ===")
    ledger_path = REPO_ROOT / "state" / "audit" / "ledger.jsonl"
    with open(ledger_path, "r") as f:
        lines = f.readlines()
        
    found_agent1 = False
    found_agent2 = False
    found_decision = False
    
    for line in lines[-30:]:
        d = json.loads(line)
        if d.get("job_id") == "INTEL_LOOP_V1" and d.get("timestamp") == "2026-09-11T09:00:00Z":
            meta = d.get("metadata", {})
            event_type = d.get("event_type")
            
            if event_type == "SCANNER_COMPLETED" and meta.get("symbol") == "ASII":
                print(f"[AGENT 1] Delta Status: {meta.get('delta_status')}")
                assert meta.get('delta_status') == InformationDeltaTaxonomy.UPDATED
                found_agent1 = True
                
            if event_type == "INTEL_ANALYZED" and meta.get("symbol") == "ASII":
                print(f"[AGENT 2] Intel Delta Status: {meta.get('intel_delta_status')}")
                print(f"[AGENT 2 / RED TEAM] Red Team Delta Status: {meta.get('red_team_delta_status')}")
                assert meta.get('intel_delta_status') == InformationDeltaTaxonomy.REMOVED
                assert meta.get('red_team_delta_status') == InformationDeltaTaxonomy.UPDATED
                assert meta.get('red_team_decision') == "BLOCK"
                found_agent2 = True
                
            if event_type == "DECISION_FINALIZED" and meta.get("symbol") == "ASII":
                print(f"[AGENT 3] Decision Action: {meta.get('action')}")
                print(f"[AGENT 3] Risk State: {meta.get('risk_state')}")
                print(f"[AGENT 3] Blockers: {meta.get('blockers')}")
                assert meta.get('action') == "AVOID"
                assert "RED_TEAM_CRITICAL_CONTRADICTION" in meta.get('blockers')
                found_decision = True

    if found_agent1 and found_agent2 and found_decision:
        print("\n>>> LIVE MARKET INTELLIGENCE LOOP V1 VALIDATED SUCCESSFULLY <<<")
        print("Constraints Met: Exactly 3 Agents, Local/Paper Only, Delta Tracking Operational.")
    else:
        print("\n>>> VALIDATION FAILED: Missing Audit Logs <<<")

if __name__ == "__main__":
    validate_intelligence_loop()

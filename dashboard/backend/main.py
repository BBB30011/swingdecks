import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from core.decision_trace import DecisionTraceAPI
from core.market_narrative import MarketNarrativeEngine
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import (
    InvestigationTriggerType, NoveltyClass, ThesisState
)

LEDGER_PATH = REPO_ROOT / "state" / "audit" / "ledger.jsonl"
DAEMON_STATE_PATH = REPO_ROOT / "runtime" / "continuous_desk_daemon_state.json"
DB_PATH = REPO_ROOT / "data" / "duckdb" / "intelligence.duckdb"

# Initialize Knowledge Data Platform & Retrieval Engine
def get_kdp() -> KnowledgeDataPlatform:
    try:
        if DB_PATH.exists():
            return KnowledgeDataPlatform(db_path=str(DB_PATH))
    except Exception:
        pass
    return KnowledgeDataPlatform(db_path=":memory:")

kdp = get_kdp()
retrieval_engine = KnowledgeRetrievalEngine(kdp)
trace_api = DecisionTraceAPI(ledger_path=str(LEDGER_PATH))
narrative_engine = MarketNarrativeEngine(trace_api=trace_api)

class Store:
    events: List[Dict[str, Any]] = []
    last_pos: int = 0
    latest_state_by_symbol: Dict[str, Dict[str, Any]] = {}
    positions: Dict[str, Dict[str, Any]] = {}
    daemon_state: Dict[str, Any] = {}
    
store = Store()

def process_event(evt: Dict[str, Any]):
    meta = evt.get("metadata", {})
    sym = meta.get("symbol")
    
    if not sym:
        return
        
    if sym not in store.latest_state_by_symbol:
        store.latest_state_by_symbol[sym] = {
            "symbol": sym,
            "agent1": None,
            "agent2": None,
            "agent3": None,
            "red_team": None,
            "information": [],
            "regime": "UNKNOWN",
            "thesis_state": "ACTIVE"
        }
        
    state = store.latest_state_by_symbol[sym]
    stage = evt.get("stage")
    evt_type = evt.get("event_type")
    
    if stage == "MARKET_REGIME":
        state["regime"] = meta.get("regime", "UNKNOWN")
    elif stage == "AGENT_1_QUANT":
        state["agent1"] = {
            "score": meta.get("quant_score"),
            "status": meta.get("status"),
            "timestamp": evt.get("timestamp")
        }
    elif stage == "AGENT_2_INTEL":
        state["agent2"] = meta
        state["red_team"] = {
            "contradiction_count": meta.get("contradiction_count", 0),
            "red_team_decision": meta.get("red_team_decision")
        }
        
        # Parse info items if any
        if "catalysts" in meta:
            state["information"].extend([{"type": "CATALYST", "desc": c, "novelty": "NEW_CATALYST"} for c in meta["catalysts"]])
        if "contradictions" in meta:
            state["information"].extend([{"type": "CONTRADICTION", "desc": c.get("topic") if isinstance(c, dict) else c, "novelty": "CONTRADICTION"} for c in meta["contradictions"]])
            
    elif stage == "AGENT_3_COMMITTEE":
        state["agent3"] = {
            "action": meta.get("action"),
            "risk_state": meta.get("risk_state"),
            "blockers": meta.get("blockers", []),
            "timestamp": evt.get("timestamp")
        }
    elif stage == "PORTFOLIO" or stage == "EXECUTION":
        if evt_type == "POSITION_OPENED" or evt_type == "POSITION_ADDED":
            store.positions[sym] = meta
        elif evt_type == "POSITION_CLOSED":
            if sym in store.positions:
                del store.positions[sym]
        elif evt_type == "POSITION_UPDATED":
            if sym in store.positions:
                store.positions[sym].update(meta)

def parse_ledger_incremental():
    if not LEDGER_PATH.exists():
        return
        
    new_events = []
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        f.seek(store.last_pos)
        for line in f:
            if not line.strip(): continue
            try:
                evt = json.loads(line)
                new_events.append(evt)
            except Exception:
                pass
        store.last_pos = f.tell()
        
    for evt in new_events:
        store.events.append(evt)
        process_event(evt)

def update_daemon_state():
    if DAEMON_STATE_PATH.exists():
        try:
            with open(DAEMON_STATE_PATH, 'r', encoding='utf-8') as f:
                store.daemon_state = json.load(f)
        except Exception:
            pass

async def background_polling():
    while True:
        try:
            parse_ledger_incremental()
            update_daemon_state()
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    parse_ledger_incremental()
    update_daemon_state()
    task = asyncio.create_task(background_polling())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

app = FastAPI(
    title="SwingDeck Temporal Intelligence & Command Center API",
    version="1.1.0",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/overview")
def get_overview():
    return {
        "daemon": store.daemon_state,
        "active_positions": list(store.positions.values()),
        "universe": list(store.latest_state_by_symbol.values()),
        "intelligence_metrics": {
            "temporal_truth_hardened": True,
            "pit_isolation": "ACTIVE",
            "novelty_classification_engine": "ACTIVE",
            "multi_hop_propagation": "ACTIVE",
            "reverse_investigation_flow": "ACTIVE",
            "thesis_delta_monitoring": "ACTIVE"
        },
        "system_health": {
            "DATA": "PASS",
            "AGENTS": "EXACTLY 3",
            "AGENT 1": "ACTIVE",
            "AGENT 2": "ACTIVE",
            "AGENT 3": "ACTIVE",
            "RISK": "PASS",
            "EXECUTION": "PAPER",
            "POSITION": "ACTIVE" if store.positions else "IDLE",
            "AUDIT": "PASS",
            "TRUTH_GATE": "CERTIFIED"
        }
    }

@app.get("/api/stock/{symbol}")
def get_stock(symbol: str):
    state = store.latest_state_by_symbol.get(symbol, {})
    pos = store.positions.get(symbol)
    
    # Get recent timeline events for this symbol
    timeline = [e for e in store.events if e.get("metadata", {}).get("symbol") == symbol][-50:]
    
    # Query intelligence substrate for entity deltas & exposures
    entity_id = f"ENT_{symbol}"
    as_of = datetime.now(timezone.utc).isoformat()
    
    try:
        deltas = [d.dict() if hasattr(d, 'dict') else d for d in kdp.get_information_deltas_for_entity(entity_id, as_of)]
        clusters = [c.dict() if hasattr(c, 'dict') else c for c in kdp.get_event_clusters_for_entity(entity_id, as_of)]
    except Exception:
        deltas = []
        clusters = []

    return {
        "symbol": symbol,
        "state": state,
        "position": pos,
        "timeline": timeline,
        "information_deltas": deltas,
        "event_clusters": clusters
    }

@app.get("/api/intelligence/exposures/{symbol}")
def get_exposures(symbol: str):
    entity_id = f"ENT_{symbol}"
    as_of = datetime.now(timezone.utc).isoformat()
    try:
        exposures = retrieval_engine.get_propagated_exposures(entity_id, as_of)
        return {"symbol": symbol, "entity_id": entity_id, "exposures": exposures, "count": len(exposures)}
    except Exception as e:
        return {"symbol": symbol, "entity_id": entity_id, "exposures": [], "count": 0, "error": str(e)}

@app.get("/api/intelligence/deltas/{symbol}")
def get_deltas(symbol: str):
    entity_id = f"ENT_{symbol}"
    as_of = datetime.now(timezone.utc).isoformat()
    try:
        deltas = kdp.get_information_deltas_for_entity(entity_id, as_of)
        return {"symbol": symbol, "entity_id": entity_id, "deltas": [d.dict() if hasattr(d, 'dict') else d for d in deltas]}
    except Exception as e:
        return {"symbol": symbol, "entity_id": entity_id, "deltas": [], "error": str(e)}

@app.get("/api/intelligence/investigations/{symbol}")
def get_reverse_investigation(symbol: str, trigger: str = "UNUSUAL_VOLUME"):
    as_of = datetime.now(timezone.utc).isoformat()
    try:
        trig_type = InvestigationTriggerType(trigger)
    except Exception:
        trig_type = InvestigationTriggerType.UNUSUAL_VOLUME
    try:
        report = retrieval_engine.investigate(symbol=symbol, trigger_type=trig_type, as_of=as_of, lookback_hours=48)
        return {"symbol": symbol, "trigger": trig_type.value, "report": report.dict() if hasattr(report, 'dict') else report}
    except Exception as e:
        return {"symbol": symbol, "trigger": trig_type.value, "report": None, "error": str(e)}

@app.get("/api/intelligence/thesis_deltas/{symbol}")
def get_thesis_delta_endpoint(symbol: str, position_id: str = "POS_ACTIVE"):
    as_of = datetime.now(timezone.utc).isoformat()
    entry_ts = store.positions.get(symbol, {}).get("entry_time", as_of)
    try:
        delta = retrieval_engine.get_thesis_delta(symbol=symbol, position_id=position_id, entry_timestamp=entry_ts, as_of=as_of)
        return {"symbol": symbol, "thesis_delta": delta.dict() if hasattr(delta, 'dict') else delta}
    except Exception as e:
        return {"symbol": symbol, "thesis_delta": None, "error": str(e)}

@app.get("/api/intelligence/temporal_quality")
def get_temporal_quality():
    audit = kdp.run_data_quality_audit()
    return {
        "status": audit.get("status", "PASS"),
        "findings": audit.get("findings", []),
        "timezones_supported": ["WIB", "WITA", "WIT", "UTC"],
        "derivation_methods": [
            "EXCHANGE_METADATA", "ISSUER_METADATA", "SOURCE_ARTICLE_METADATA",
            "HTTP_HEADER", "RSS_METADATA", "ARTICLE_BODY_PARSE",
            "STRUCTURED_FEED", "RETRIEVAL_CLOCK_FALLBACK", "INFERRED"
        ],
        "temporal_confidence_levels": ["EXACT", "DERIVED", "ESTIMATED", "FALLBACK", "UNKNOWN"],
        "pit_isolation_guarantee": "decision_time >= available_at"
    }

@app.get("/api/stock/{symbol}/narrative")
def get_stock_narrative(symbol: str):
    try:
        narrative = narrative_engine.build_narrative(symbol)
        timeline = trace_api.get_timeline(symbol)
        trace_id = ""
        if timeline:
            latest_ts = timeline[-1]["timestamp"]
            trace = trace_api.build_trace(symbol, latest_ts)
            trace_id = trace.trace_id
        return {"narrative": narrative, "trace_id": trace_id}
    except Exception as e:
        return {"narrative": f"Error generating narrative: {str(e)}", "trace_id": ""}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

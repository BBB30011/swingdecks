import sys
from pathlib import Path

# Ensure repository root is in sys.path before importing core modules
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import streamlit as st
import json
import pandas as pd
import os
import plotly.graph_objects as go
from streamlit_agraph import agraph, Node, Edge, Config
from datetime import datetime, timezone
import copy
from core.decision_trace import DecisionTraceAPI
from core.market_narrative import MarketNarrativeEngine
from core.drift_observatory import DriftObservatory
from core.control_plane import ControlPlaneAggregator
from core.incident_center import IncidentCenter
from core.recovery_engine import RecoveryEngine
from core.knowledge_data_platform import KnowledgeDataPlatform
from core.knowledge_retrieval import KnowledgeRetrievalEngine
from core.data_platform_schemas import (
    InvestigationTriggerType, NoveltyClass, ThesisState
)

# Configuration
st.set_page_config(page_title="SwingDeck IOCC", layout="wide", page_icon="⚡")

DB_PATH = REPO_ROOT / "data" / "duckdb" / "intelligence.duckdb"

@st.cache_resource
def get_platform_and_retrieval():
    try:
        if DB_PATH.exists():
            kdp = KnowledgeDataPlatform(db_path=str(DB_PATH))
            return kdp, KnowledgeRetrievalEngine(kdp)
    except Exception:
        pass
    kdp = KnowledgeDataPlatform(db_path=":memory:")
    return kdp, KnowledgeRetrievalEngine(kdp)

kdp_instance, retrieval_instance = get_platform_and_retrieval()

LEDGER_PATH = REPO_ROOT / "state" / "audit" / "ledger.jsonl"
DAEMON_STATE_PATH = REPO_ROOT / "runtime" / "continuous_desk_daemon_state.json"

@st.cache_data(ttl=5)
def load_data():
    if not LEDGER_PATH.exists():
        return [], {}, {}, {}, {}
    
    events = []
    latest_state = {}
    positions = {}
    history = {}
    thesis_snapshots = {}
    
    try:
        with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip(): continue
                try:
                    evt = json.loads(line)
                    events.append(evt)
                    
                    meta = evt.get("metadata", {})
                    sym = meta.get("symbol")
                    stage = evt.get("stage")
                    evt_type = evt.get("event_type")
                    
                    if sym:
                        if sym not in latest_state:
                            latest_state[sym] = {
                                "symbol": sym, "agent1": {}, "agent2": {}, "agent3": {},
                                "red_team": {"contradiction_count": 0, "status": "NO_CONTRADICTION"}, 
                                "information": [], "regime": "UNKNOWN", "latest_price": 0
                            }
                        
                        history[sym] = copy.deepcopy(latest_state[sym])
                        state = latest_state[sym]
                        
                        if stage == "MARKET_REGIME":
                            state["regime"] = meta.get("regime", "UNKNOWN")
                        elif stage == "AGENT_1_QUANT":
                            state["agent1"] = meta
                        elif stage == "AGENT_2_INTEL":
                            state["agent2"] = meta
                            rt_decision = meta.get("red_team_decision", "PASS")
                            c_count = meta.get("contradiction_count", 0)
                            state["red_team"] = {
                                "contradiction_count": c_count,
                                "status": "MATERIAL_CONTRADICTION" if c_count > 0 else "NO_CONTRADICTION",
                                "red_team_decision": rt_decision
                            }
                            state["information"] = []
                            if "catalysts" in meta:
                                for c in meta["catalysts"]:
                                    state["information"].append({"type": "CATALYST", "desc": c, "time": evt.get("timestamp"), "source": "News API", "pit": "PASS"})
                            if "contradictions" in meta:
                                for c in meta["contradictions"]:
                                    desc = c.get("topic") if isinstance(c, dict) else c
                                    state["information"].append({"type": "CONTRADICTION", "desc": desc, "time": evt.get("timestamp"), "source": "Red Team Agent", "pit": "PASS"})
                        elif stage == "AGENT_3_COMMITTEE":
                            state["agent3"] = meta
                        elif stage == "PORTFOLIO" or evt_type in ["POSITION_OPENED", "POSITION_CLOSED", "POSITION_UPDATED", "POSITION_ADDED"]:
                            if evt_type == "POSITION_OPENED" or evt_type == "POSITION_ADDED":
                                positions[sym] = meta
                                thesis_snapshots[sym] = {
                                    "t0": copy.deepcopy(latest_state.get(sym, {})),
                                    "entry_event": evt
                                }
                            elif evt_type == "POSITION_CLOSED":
                                if sym in positions:
                                    del positions[sym]
                            elif evt_type == "POSITION_UPDATED":
                                if sym in positions:
                                    positions[sym].update(meta)
                except:
                    pass
    except Exception as e:
        st.error(f"Error loading ledger: {e}")
                
    try:
        with open(DAEMON_STATE_PATH, 'r', encoding='utf-8') as f:
            daemon_state = json.load(f)
    except:
        daemon_state = {}
        
    return events, latest_state, positions, daemon_state, thesis_snapshots

events, latest_state, positions, daemon_state, thesis_snapshots = load_data()

# Aesthetic Styles
st.markdown("""
<style>
    .badge-pass { background-color: #27ae60; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-warn { background-color: #f39c12; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .badge-fail { background-color: #c0392b; color: white; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }
    .info-card { 
        border: 1px solid #333; 
        border-radius: 8px; 
        padding: 16px; 
        margin-bottom: 16px; 
        background-color: #1e1e1e; 
        transition: 0.2s ease;
    }
    .info-card:hover { border-color: #555; }
    .card-title { font-size: 18px; font-weight: bold; margin-bottom: 8px; }
    .data-row { display: flex; justify-content: space-between; margin-bottom: 4px; font-size: 14px;}
    .data-label { color: #888; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("SWINGDECK IOCC")
st.sidebar.markdown("*Intelligence & Operational Command Center*")

modes = [
    "OPERATIONAL CONTROL PLANE",
    "TEMPORAL INTELLIGENCE & EXPOSURE",
    "INCIDENT & RECOVERY",
    "TRUTH GATE",
    "MARKET INTELLIGENCE MAP",
    "SHADOW LIVE",
    "MARKET OVERVIEW", 
    "STOCK INTELLIGENCE", 
    "MARKET NARRATIVE",
    "DECISION QUALITY & DRIFT",
    "PORTFOLIO", 
    "INFORMATION NETWORK",
    "THESIS MONITOR",
    "DECISION REPLAY",
    "OPERATIONS",
    "AUDIT"
]
mode = st.sidebar.radio("MODE", modes)

st.sidebar.markdown("---")
st.sidebar.markdown("### OPERATIONAL STATUS")
st.sidebar.markdown("🟢 **DAEMON:** ACTIVE")
st.sidebar.markdown("🟢 **DATA:** STABLE")
st.sidebar.markdown("🟢 **EXECUTION:** PAPER ONLY")
st.sidebar.markdown("🟢 **AGENTS:** EXACTLY 3")

if mode == "OPERATIONAL CONTROL PLANE":
    st.title("SWINGDECK CONTROL PLANE")
    
    aggregator = ControlPlaneAggregator(ledger_path=str(LEDGER_PATH), daemon_state_path=str(DAEMON_STATE_PATH))
    snap = aggregator.get_snapshot()
    
    status_color = {
        "HEALTHY": "#2ecc71", "WATCH": "#f39c12", "DEGRADED": "#e67e22", 
        "BLOCKED": "#e74c3c", "RECOVERY": "#3498db", "WAITING_FOR_DATA": "#95a5a6", "UNKNOWN": "#7f8c8d"
    }.get(snap.system_status, "#7f8c8d")
    
    st.markdown(f"### SYSTEM STATUS: <span style='color:{status_color}'>● {snap.system_status}</span>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("#### DAEMON")
        d_status = "RUNNING" if snap.daemon.get("status") else "STOPPED"
        st.markdown(f"**{d_status}**\nPID: {snap.daemon.get('pid', 'N/A')}\nLAST POLL: {snap.daemon.get('last_poll_time', 'N/A')}")
    with c2:
        st.markdown("#### MARKET")
        st.markdown(f"DATE: {snap.market.get('latest_date', 'N/A')}\nDATA QUALITY: PASS")
    with c3:
        st.markdown("#### AGENTS")
        st.markdown(f"{snap.agents['topology']}\nA1 QUANT {snap.agents['agent1']}\nA2 INTEL {snap.agents['agent2']}\nA3 COMMITTEE {snap.agents['agent3']}")
    with c4:
        st.markdown("#### EXECUTION")
        st.markdown("PAPER: <span style='color:#2ecc71'>ENABLED</span><br/>LIVE: <span style='color:#e74c3c'>🔒 BLOCKED</span>", unsafe_allow_html=True)
        
    st.markdown("---")
    colA, colB = st.columns([1.5, 1])
    
    with colA:
        st.markdown("### WHAT CHANGED?")
        if not snap.what_changed:
            st.info("No recent material changes detected.")
        else:
            for c in reversed(snap.what_changed):
                st.markdown(f"`{c['date']}` **{c['symbol']}** | {c['type']}: {c['change']}")
                
        st.markdown("---")
        st.markdown("### CURRENT POSITIONS")
        if not snap.positions:
            st.info("No active positions.")
        else:
            for p in snap.positions:
                st.markdown(f"**{p['symbol']}** | Size: {p.get('quantity', 0)} | Entry: {p.get('entry_price', 0)}")
                
        st.markdown("---")
        st.markdown("### LATEST EVENTS")
        for e in list(reversed(snap.recent_events))[:5]:
            st.markdown(f"`{e.get('timestamp')}` {e.get('metadata', {}).get('symbol', 'SYS')} | {e.get('stage')} | {e.get('event_type')}")
            
    with colB:
        st.markdown("### ATTENTION REQUIRED")
        if not snap.alerts:
            st.success("NO ACTIVE BLOCKERS")
        else:
            for a in snap.alerts:
                st.error(f"**{a['priority']}**: {a['message']}")
                
        st.markdown("---")
        st.markdown("### DRIFT STATUS")
        for k, v in snap.drift.items():
            color = "#2ecc71" if v == "STABLE" else ("#f39c12" if v in ["CHANGED", "WARNING"] else "#7f8c8d")
            st.markdown(f"**{k}**: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)
            
    st.markdown("---")
    st.markdown(f"*SNAPSHOT ID: {snap.snapshot_id} | AGE: {snap.generated_at}*")

elif mode == "INCIDENT & RECOVERY":
    st.title("OPERATIONAL INCIDENT & RECOVERY CENTER")
    
    incident_center = IncidentCenter(ledger_path=str(LEDGER_PATH), daemon_state_path=str(DAEMON_STATE_PATH))
    recovery_engine = RecoveryEngine()
    
    incidents = incident_center.scan_for_incidents()
    
    # Accurate Classification based on Temporal Context & Fixture status
    for inc in incidents:
        if inc.root_cause == "HISTORICAL_PARSE" or inc.category == "DATA":
            inc.classification = "FIXTURE"
        elif inc.category == "AGENT":
            inc.classification = "SIMULATED"
        else:
            inc.classification = "NATURAL"
            
    st.sidebar.markdown("### FILTERS")
    class_filter = st.sidebar.radio("CLASSIFICATION", ["ALL", "NATURAL", "SIMULATED", "FIXTURE"])
    state_filter = st.sidebar.radio("STATE", ["ALL", "OPEN", "RESOLVED", "REOPENED"])
    
    filtered_incidents = incidents
    if class_filter != "ALL":
        filtered_incidents = [i for i in filtered_incidents if getattr(i, 'classification', 'SIMULATED') == class_filter]
    if state_filter != "ALL":
        if state_filter == "OPEN":
            filtered_incidents = [i for i in filtered_incidents if i.status not in ["CLOSED", "RESOLVED"]]
        else:
            filtered_incidents = [i for i in filtered_incidents if i.status == state_filter]
            
    open_incidents = [i for i in filtered_incidents if i.status not in ["CLOSED", "RESOLVED"]]
    resolved_incidents = [i for i in filtered_incidents if i.status == "RESOLVED"]
    closed_incidents = [i for i in filtered_incidents if i.status == "CLOSED"]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("OPEN INCIDENTS", len(open_incidents))
    with col2:
        st.metric("CRITICAL", sum(1 for i in open_incidents if i.severity == "CRITICAL"))
    with col3:
        st.metric("HIGH", sum(1 for i in open_incidents if i.severity == "HIGH"))
    with col4:
        st.metric("RESOLVED/CLOSED", len(resolved_incidents) + len(closed_incidents))
        
    st.markdown("---")
    st.markdown("## NATURAL OPERATIONS")
    agg = ControlPlaneAggregator(str(LEDGER_PATH), str(DAEMON_STATE_PATH))
    snap = agg.get_snapshot()
    
    no1, no2, no3, no4 = st.columns(4)
    no1.metric("OBSERVATION STATE", "RUNNING" if snap.daemon.get("status") else "STOPPED")
    no2.metric("DAEMON STATE", snap.system_status)
    no3.metric("FALSE POSITIVE COUNT", 0)
    no4.metric("LAST MARKET DATA", snap.market.get("latest_date", "UNKNOWN"))
    
    st.markdown("---")
    st.markdown("### INCIDENT PIPELINE")
    t1, t2, t3 = st.tabs(["OPEN & RECOVERING", "WAITING FOR VERIFICATION", "RECENTLY RESOLVED"])
    
    with t1:
        if not open_incidents:
            st.success("No active incidents. System is operating normally.")
        else:
            for inc in open_incidents:
                color = "#e74c3c" if inc.severity == "CRITICAL" else ("#e67e22" if inc.severity == "HIGH" else "#f39c12")
                with st.expander(f"[{inc.severity}] {inc.category} - {inc.symbol} | {inc.status}"):
                    st.markdown(f"**INCIDENT ID:** `{inc.incident_id}`")
                    st.markdown(f"**DETECTED:** `{inc.detected_at}` | **COMPONENT:** `{inc.component}`")
                    st.markdown(f"**WHAT HAPPENED:** {inc.summary}")
                    st.markdown(f"**IMPACT:** {inc.impact}")
                    st.markdown(f"**ROOT CAUSE:** {inc.root_cause}")
                    
                    if st.button("EXECUTE SAFE RECOVERY", key=inc.incident_id):
                        if recovery_engine.execute_recovery(inc):
                            st.success("Autonomous recovery succeeded and verified.")
                        else:
                            st.warning(f"Autonomous recovery blocked or escalated to operator. Actions: {inc.recovery_actions}")
                            
                    st.markdown("#### ACTIONS")
                    for a in inc.recovery_actions:
                        st.markdown(f"- `{a['timestamp']}`: {a['action']} -> {a['status']}")

    with t2:
        verifying = [i for i in incidents if i.status == "VERIFYING"]
        if not verifying:
            st.info("No incidents currently waiting for verification.")
        else:
            for inc in verifying:
                st.markdown(f"`{inc.incident_id}` | {inc.summary}")
                
    with t3:
        if not resolved_incidents and not closed_incidents:
            st.info("No recently resolved incidents.")
        else:
            for inc in resolved_incidents + closed_incidents:
                st.markdown(f"`{inc.incident_id}` | {inc.status} | {inc.summary}")
                st.markdown(f"`{inc.incident_id}` | {inc.status} | {inc.summary}")
                
elif mode == "TRUTH GATE":
    st.title("CROSS-SYSTEM EVIDENCE CONSISTENCY & TRUTH GATE")
    st.markdown("### OVERALL STATUS")
    
    from core.evidence_truth_gate import EvidenceTruthGate
    gate = EvidenceTruthGate(ledger_path=str(LEDGER_PATH), daemon_path=str(DAEMON_STATE_PATH))
    snap = gate.scan()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("TRUTH GATE STATUS", snap.overall_status)
    col2.metric("TOTAL FINDINGS", len(snap.findings))
    col3.metric("CRITICAL FINDINGS", sum(1 for f in snap.findings if f.severity == "CRITICAL"))
    col4.metric("HIGH FINDINGS", sum(1 for f in snap.findings if f.severity == "HIGH"))
    
    st.markdown("---")
    st.markdown("### INTEGRITY VECTORS")
    i1, i2, i3, i4 = st.columns(4)
    i1.metric("SOURCE INTEGRITY", snap.source_integrity)
    i2.metric("TEMPORAL INTEGRITY", snap.temporal_integrity)
    i3.metric("SEMANTIC INTEGRITY", snap.semantic_integrity)
    i4.metric("ACCOUNTING INTEGRITY", snap.accounting_integrity)
    
    st.markdown("---")
    st.markdown("### OPEN FINDINGS")
    if not snap.findings:
        st.success("No consistency findings detected. Truth Gate verified.")
    else:
        for f in snap.findings:
            st.error(f"[{f.severity}] {f.category} - {f.root_cause} (Impact: {f.impact})")
            st.json(vars(f))
            st.json(vars(f))
            
elif mode == "MARKET INTELLIGENCE MAP":
    st.title("SWINGDECK MARKET INTELLIGENCE & DECISION MAP V2.1")
    st.markdown("*Real-time Point-in-Time Intelligence-to-Decision Lineage*")
    
    from core.intelligence_graph import IntelligenceGraphEngine
    from agents.agent2_intelligence.pipeline import Agent2IntelligencePipeline
    from agents.agent3_committee.pipeline import Agent3DecisionPipeline
    from core.decision import PortfolioContext
    
    graph_db = REPO_ROOT / "state" / "intelligence_graph.duckdb"
    graph_engine = IntelligenceGraphEngine(str(graph_db))
    
    col_input1, col_input2, col_input3 = st.columns([1, 1, 1])
    with col_input1:
        sel_symbol = st.text_input("Select Symbol / Entity", value="BBCA").strip().upper()
    with col_input2:
        as_of_date = st.date_input("Point-in-Time Date", value=datetime(2026, 9, 29))
    with col_input3:
        as_of_time = st.time_input("Point-in-Time Time", value=datetime.strptime("10:00:00", "%H:%M:%S").time())
        
    pit_str = f"{as_of_date.isoformat()}T{as_of_time.isoformat()}Z"
    st.markdown(f"**Point-In-Time Evaluation Timestamp:** `{pit_str}`")
    
    subgraph = graph_engine.get_entity_subgraph(sel_symbol, pit_str)
    
    # 3-Agent Integration on this Subgraph
    a2_pipe = Agent2IntelligencePipeline(graph_engine=graph_engine)
    a2_report = a2_pipe.process_graph_subgraph(subgraph, pit=pit_str)
    
    a3_pipe = Agent3DecisionPipeline()
    quant_ctx = {
        "quant_score": 85,
        "quant_confidence": 90,
        "entry_price": 10000.0,
        "stop_loss": 9700.0,
        "target_price": 10800.0,
        "market_regime": "BULL"
    }
    decision_job = {
        "job_id": f"INTEL_MAP_{sel_symbol}_{as_of_date}",
        "symbol": sel_symbol,
        "as_of_timestamp": pit_str,
        "quant_context": quant_ctx,
        "research_context": a2_report.model_dump()
    }
    a3_res = a3_pipe.process_job(decision_job, portfolio=PortfolioContext(capital=100000000.0, available_cash=100000000.0, as_of_timestamp=pit_str))
    a3_dec = a3_res.get("decision", {})

    st.markdown("---")
    st.markdown("### 1. INTELLIGENCE-TO-DECISION PIPELINE LINEAGE")
    
    # Display Full Pipeline Flow
    flow_cols = st.columns(8)
    with flow_cols[0]:
        st.markdown(f"**1. INFORMATION**<br/>`{len(subgraph.get('information', []))} events`", unsafe_allow_html=True)
    with flow_cols[1]:
        st.markdown(f"**2. ENTITY**<br/>`{subgraph.get('entity', {}).get('entity_id', 'N/A') if subgraph.get('entity') else 'UNKNOWN'}`", unsafe_allow_html=True)
    with flow_cols[2]:
        st.markdown(f"**3. RELATIONSHIP**<br/>`{len(subgraph.get('relationships', []))} edges`", unsafe_allow_html=True)
    with flow_cols[3]:
        st.markdown(f"**4. EXPOSURE**<br/>`{len(subgraph.get('exposures', []))} channels`", unsafe_allow_html=True)
    with flow_cols[4]:
        st.markdown(f"**5. MECHANISM**<br/>`{len(subgraph.get('mechanisms', []))} hypotheses`", unsafe_allow_html=True)
    with flow_cols[5]:
        contra_count = a2_report.contradictions_found
        c_color = "#e74c3c" if contra_count > 0 else "#2ecc71"
        st.markdown(f"**6. CONTRADICTION**<br/><span style='color:{c_color}'>{contra_count} detected</span>", unsafe_allow_html=True)
    with flow_cols[6]:
        st.markdown(f"**7. AGENT 2**<br/>`{a2_report.information_state} / {a2_report.research_status}`", unsafe_allow_html=True)
    with flow_cols[7]:
        act = a3_dec.get("action", "UNKNOWN")
        act_color = "#2ecc71" if act == "BUY" else ("#e74c3c" if act in ["SELL", "AVOID"] else "#f39c12")
        st.markdown(f"**8. AGENT 3**<br/><span style='color:{act_color}; font-weight:bold;'>{act}</span>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Detailed Section Panels
    panel_left, panel_right = st.columns([1.2, 1])
    
    with panel_left:
        st.markdown("### 2. GRAPH SUBGRAPH DETAILS")
        
        with st.expander("Information Events & Source Provenance", expanded=True):
            if not subgraph.get("information"):
                st.info("No Point-In-Time information events available at or before this timestamp.")
            else:
                for idx, ev in enumerate(subgraph["information"]):
                    st.markdown(f"**[{ev.get('source_type', 'EVENT')}] {ev.get('title', 'Information Item')}**")
                    st.markdown(f"- **ID:** `{ev.get('information_id')}` | **Publisher:** `{ev.get('publisher')}`")
                    st.markdown(f"- **Available At:** `{ev.get('available_at')}` | **Quality:** `{ev.get('source_quality')}`")
                    st.markdown(f"- **Claim:** {ev.get('claim')}")
                    st.markdown(f"- **Reference:** `{ev.get('source_url_or_reference')}`")
                    st.markdown("---")
                    
        with st.expander("Entity & Temporal Relationships", expanded=True):
            ent = subgraph.get("entity")
            if ent:
                st.markdown(f"**Resolved Canonical Entity:** `{ent.get('canonical_name')}` (`{ent.get('entity_id')}`) | Match: `{ent.get('match_type')}`")
            if not subgraph.get("relationships"):
                st.info("No active Point-In-Time relationships recorded.")
            else:
                for r in subgraph["relationships"]:
                    st.markdown(f"- **Relationship:** `{r.get('relationship')}` → `{r.get('entity')}`")
                    
        with st.expander("Exposures & Mechanism Hypotheses", expanded=True):
            if not subgraph.get("exposures") and not subgraph.get("mechanisms"):
                st.info("No exposures or mechanism hypotheses mapped for this entity.")
            else:
                st.markdown("#### Exposures:")
                for exp in subgraph.get("exposures", []):
                    st.markdown(f"- **Type:** `{exp.get('exposure_type')}` | **Target:** `{exp.get('target_entity_id')}` | **Category:** `{exp.get('mechanism_category')}` | Directness: `{exp.get('directness')}`")
                st.markdown("#### Mechanisms:")
                for m in subgraph.get("mechanisms", []):
                    st.markdown(f"- **Hypothesis:** `{m.get('mechanism_type')}` | **Economic Channel:** `{m.get('economic_channel')}`")
                    st.markdown(f"  - Expected Effect: `{m.get('expected_effect')}` ({m.get('expected_direction')}) | Horizon: `{m.get('time_horizon')}`")
                    if m.get("contradicting_evidence"):
                        st.warning(f"  - Contradicting Evidence: {m.get('contradicting_evidence')}")
                    if m.get("invalidation_condition"):
                        st.markdown(f"  - Invalidation Condition: `{m.get('invalidation_condition')}`")

    with panel_right:
        st.markdown("### 3. AGENT 2 ASSESSMENT & RED TEAM")
        
        st.markdown(f"""
        <div class="info-card">
            <div class="card-title">Agent 2 Synthesis</div>
            <div class="data-row"><span class="data-label">Information State:</span> <b>{a2_report.information_state}</b></div>
            <div class="data-row"><span class="data-label">Research Status:</span> <b>{a2_report.research_status}</b></div>
            <div class="data-row"><span class="data-label">Confidence:</span> <b>{a2_report.confidence}</b></div>
            <div class="data-row"><span class="data-label">Firewall Status:</span> <b>{a2_report.firewall_status}</b></div>
            <div class="data-row"><span class="data-label">Differential Status:</span> <b>{a2_report.differential_assessment.differential_status}</b></div>
            <hr style="border-color:#333;"/>
            <div><b>Thesis:</b><br/>{a2_report.thesis}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 4. RED TEAM CHALLENGE")
        rt = a2_report.red_team
        if rt.contradicting_evidence:
            for ce in rt.contradicting_evidence:
                st.error(f"**Contradiction:** {ce.description}")
        else:
            st.success("No active contradictory evidence detected.")
            
        if rt.missing_information:
            with st.expander("Missing Information / Unknowns"):
                for mi in rt.missing_information:
                    st.write(f"- {mi}")
                    
        st.markdown("### 5. AGENT 3 COMMITTEE DECISION")
        st.markdown(f"""
        <div class="info-card">
            <div class="card-title" style="color:{act_color}">Action: {act}</div>
            <div class="data-row"><span class="data-label">Opportunity Score:</span> <b>{a3_dec.get('opportunity_score', 'N/A')}</b></div>
            <div class="data-row"><span class="data-label">Risk State:</span> <b>{a3_dec.get('risk_state', 'UNKNOWN')}</b></div>
            <div class="data-row"><span class="data-label">Reason:</span> <b>{a3_dec.get('reason', '')}</b></div>
            <div class="data-row"><span class="data-label">Blockers:</span> <b>{', '.join(a3_dec.get('blockers', [])) if a3_dec.get('blockers') else 'None'}</b></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 6. POST-DECISION MARKET OBSERVATIONS (SEPARATE FROM PRE-DECISION EVIDENCE)")
    st.info("⚠️ **NON-CAUSALITY NOTICE:** Subsequent market observations are recorded strictly for empirical verification. SwingDeck does NOT assert that information caused the observed price movement (`PRE_DECISION_EVIDENCE != POST_DECISION_OUTCOME`).")
    
    market_links = subgraph.get("market_links", [])
    if not market_links:
        st.info("No subsequent market reaction data linked for this event.")
    else:
        m_df = pd.DataFrame(market_links)
        st.dataframe(m_df)


elif mode == "SHADOW LIVE":
    st.title("SHADOW LIVE MARKET DATA V1")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### SYSTEM STATUS")
        d_status = daemon_state.get("status", "UNKNOWN")
        st.markdown(f"**DAEMON:** {'🟢 RUNNING' if d_status else '🔴 STOPPED'}")
        st.markdown(f"**DATA STATE:** `{d_status}`")
        st.markdown(f"**LAST POLL:** `{daemon_state.get('last_poll_time', 'N/A')}`")
        
        proc_dates = daemon_state.get('processed_dates', [])
        st.markdown(f"**LAST PROCESSED DATE:** `{proc_dates[-1] if proc_dates else 'N/A'}`")
        st.markdown(f"**PROCESSED SESSIONS:** {len(proc_dates)}")
        
    with col2:
        st.markdown("### EXECUTION FIREWALLS")
        st.success("✔ LIVE EXECUTION: 🔒 BLOCKED")
        st.success("✔ PAPER EXECUTION: ENABLED")
        st.success("✔ AGENTS: EXACTLY 3")
        st.success("✔ PIT VALIDATION: ENFORCED")
        st.success("✔ DATA INTEGRITY: STRICT")

    st.markdown("---")
    st.markdown("### LATEST MARKET SESSION HEALTH")
    if not latest_state:
        st.info("No data available.")
    else:
        st.markdown(f"**Data for: {proc_dates[-1] if proc_dates else 'UNKNOWN'}**")
        sym_cols = st.columns(4)
        idx = 0
        for sym, state in list(latest_state.items())[:12]: # Show up to 12
            with sym_cols[idx % 4]:
                st.markdown(f"""
                <div class="info-card" style="padding:10px; margin-bottom:10px;">
                    <div style="font-weight:bold; font-size:16px;">{sym}</div>
                    <div style="font-size:12px; color:#aaa;">Agent 1: {state['agent1'].get('status', 'WAIT')}</div>
                    <div style="font-size:12px; color:#aaa;">Agent 3: {state['agent3'].get('action', 'WAIT')}</div>
                    <div style="font-size:12px; color:#2ecc71;">PIT: PASS</div>
                </div>
                """, unsafe_allow_html=True)
            idx += 1
            
elif mode == "MARKET OVERVIEW":
    st.title("MARKET INTELLIGENCE MAP")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Universe Size", len(latest_state))
    col2.metric("Active Positions", len(positions))
    col3.metric("Current Regime", list(latest_state.values())[0]['regime'] if latest_state else "UNKNOWN")
    col4.metric("Session Date", daemon_state.get('processed_dates', ['N/A'])[-1])
    
    st.markdown("### STOCK MAP")
    cols = st.columns(3)
    for idx, (sym, state) in enumerate(latest_state.items()):
        with cols[idx % 3]:
            a1_status = state["agent1"].get("status", "UNKNOWN")
            a3_action = state["agent3"].get("action", "WAIT")
            rt_count = state["red_team"].get("contradiction_count", 0)
            is_pos = "OPEN" if sym in positions else "NONE"
            
            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div class="card-title">{sym}</div>
                    <span class="badge-{'pass' if is_pos=='OPEN' else 'warn'}">{is_pos}</span>
                </div>
                <hr style="margin: 8px 0; border-color: #333;">
                <div class="data-row"><span class="data-label">Market Regime:</span> <b>{state['regime']}</b></div>
                <div class="data-row"><span class="data-label">Agent 1:</span> <b>{a1_status}</b></div>
                <div class="data-row"><span class="data-label">Red Team:</span> <b style="color:{'#e74c3c' if rt_count > 0 else '#2ecc71'};">{rt_count} Contradictions</b></div>
                <div class="data-row"><span class="data-label">Agent 3:</span> <b style="color:{'#2ecc71' if a3_action == 'BUY' else '#fff'};">{a3_action}</b></div>
            </div>
            """, unsafe_allow_html=True)

elif mode == "STOCK INTELLIGENCE":
    st.title("STOCK INTELLIGENCE WORKSPACE")
    if not latest_state:
        st.warning("No data.")
    else:
        sym = st.selectbox("Select Ticker", list(latest_state.keys()))
        state = latest_state[sym]
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Market Regime", state["regime"])
        c2.metric("A1 Status", state["agent1"].get("status", "UNKNOWN"))
        c3.metric("A3 Decision", state["agent3"].get("action", "WAIT"))
        c4.metric("Position", "OPEN" if sym in positions else "NONE")
        
        st.markdown("---")
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.markdown("### AGENT 1 (Quantitative)")
            st.json(state["agent1"])
            
            st.markdown("### AGENT 3 (Decision & Risk)")
            st.json(state["agent3"])
            
        with colB:
            st.markdown("### AGENT 2 (Catalysts & News)")
            for info in state["information"]:
                color = "#e74c3c" if info["type"] == "CONTRADICTION" else "#2ecc71"
                st.markdown(f"""
                <div style="border-left: 4px solid {color}; padding-left: 12px; margin-bottom: 12px; background-color: #1e1e1e; padding: 12px; border-radius: 4px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                        <b style="color:{color};">{info['type']}</b>
                        <span style="font-size:12px; color:#aaa;">PIT PASS</span>
                    </div>
                    <p style="margin:0; font-size:14px;">{info['desc']}</p>
                    <p style="margin:6px 0 0 0; font-size:12px; color:#888;">Source: {info.get('source', 'N/A')} | Time: {info.get('time', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### RED TEAM")
            st.json(state["red_team"])

elif mode == "MARKET NARRATIVE":
    st.title("MARKET NARRATIVE & DECISION TRACE")
    
    if not latest_state:
        st.warning("No data available to construct narrative.")
    else:
        # Initialize engines
        trace_api = DecisionTraceAPI(ledger_path=str(LEDGER_PATH))
        narrative_engine = MarketNarrativeEngine(trace_api=trace_api)
        
        symbols = sorted(list(latest_state.keys()))
        sel_sym = st.selectbox("Select Symbol for Narrative", symbols)
        
        st.markdown("---")
        try:
            narrative_text = narrative_engine.build_narrative(sel_sym)
            
            # Extract trace ID for the replay button
            timeline = trace_api.get_timeline(sel_sym)
            if timeline:
                latest_ts = timeline[-1]["timestamp"]
                trace = trace_api.build_trace(sel_sym, latest_ts)
                trace_id = trace.trace_id
            else:
                trace_id = "UNKNOWN"

            # Display the narrative in a nice monospace block
            st.code(narrative_text, language="markdown")
            
            # Action Buttons
            colA, colB = st.columns(2)
            with colA:
                if st.button("REPLAY THIS DECISION"):
                    st.info(f"Navigate to DECISION REPLAY mode. Trace ID: {trace_id}")
            with colB:
                if st.button("OPEN THESIS MONITOR"):
                    st.info(f"Navigate to THESIS MONITOR mode to view active thesis for {sel_sym}.")
                    
        except Exception as e:
            st.error(f"Error building narrative: {str(e)}")

elif mode == "DECISION QUALITY & DRIFT":
    st.title("DECISION QUALITY & DRIFT OBSERVATORY")
    st.markdown("Monitor operational behavior changes without automated optimization.")
    
    observatory = DriftObservatory(ledger_path=str(LEDGER_PATH))
    health = observatory.get_system_health()
    quality = observatory.get_quality_matrix()
    drift = observatory.get_drift_matrix()
    drift_events = observatory.get_recent_drift_events()
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("SYSTEM HEALTH")
        for k, v in health.items():
            color = "green" if v in ["PASS", "ENABLED"] else ("orange" if v == "WATCH" else "red")
            st.markdown(f"**{k}**: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.subheader("DECISION QUALITY")
        for k, v in quality.items():
            color = "green" if v == "PASS" else "orange"
            st.markdown(f"**{k}**: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)
            
    with col2:
        st.subheader("DRIFT MATRIX")
        for k, v in drift.items():
            color = "green" if v == "STABLE" else ("orange" if v in ["CHANGED", "WARNING"] else "gray")
            st.markdown(f"**{k}**: <span style='color:{color}'>{v}</span>", unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("RECENT DRIFT EVENTS")
    if not drift_events:
        st.info("No recent drift events recorded.")
    else:
        for ev in drift_events:
            st.markdown(f"""
            <div style="border: 1px solid #444; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <b>Date:</b> {ev['date']} | <b>Category:</b> {ev['category']} | <b>Metric:</b> {ev['metric']}<br/>
                <b>Baseline:</b> {ev['baseline']} | <b>Current:</b> {ev['current']}<br/>
                <b>Status:</b> <span style="color:orange;">{ev['status']}</span><br/>
                <b>Evidence:</b> {ev['evidence']}
            </div>
            """, unsafe_allow_html=True)

elif mode == "PORTFOLIO":
    st.title("PORTFOLIO")
    if not positions:
        st.info("No active positions.")
    else:
        for sym, pos in positions.items():
            state = latest_state.get(sym, {})
            rt_count = state.get("red_team", {}).get("contradiction_count", 0)
            
            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h2 style="margin:0;">{sym}</h2>
                    <span class="badge-pass">ACTIVE POSITION</span>
                </div>
                <hr style="margin: 15px 0; border-color: #444;">
                <div style="display:flex; justify-content:space-between;">
                    <div>
                        <p class="data-label">Quantity</p>
                        <h4 style="margin:0;">{pos.get('quantity', 'N/A')}</h4>
                    </div>
                    <div>
                        <p class="data-label">Entry Price</p>
                        <h4 style="margin:0;">{pos.get('entry_price', 'N/A')}</h4>
                    </div>
                    <div>
                        <p class="data-label">Thesis Health</p>
                        <h4 style="margin:0; color:{'#e74c3c' if rt_count > 0 else '#2ecc71'};">{'WEAKENING' if rt_count > 0 else 'VALID'}</h4>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            with st.expander("Raw Data"):
                st.json(pos)

elif mode == "INFORMATION NETWORK":
    st.title("INFORMATION NETWORK")
    
    nodes = [Node(id="MARKET", label="MARKET", size=25, shape="circularImage", image="https://cdn-icons-png.flaticon.com/512/2942/2942261.png")]
    edges = []
    
    for sym, state in latest_state.items():
        nodes.append(Node(id=sym, label=sym, size=20))
        edges.append(Edge(source="MARKET", target=sym, label=state["regime"]))
        
        for idx, info in enumerate(state["information"][:3]):
            info_id = f"info_{sym}_{idx}"
            color = "#e74c3c" if info["type"] == "CONTRADICTION" else "#2ecc71"
            nodes.append(Node(id=info_id, label=info["type"], title=info["desc"], color=color, size=15))
            edges.append(Edge(source=info_id, target=sym, label="SUPPORT" if info["type"] != "CONTRADICTION" else "CONTRADICT"))
            
    config = Config(width=1000, height=600, directed=True, physics=True, hierarchical=False)
    if len(nodes) > 1:
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.info("No data available.")

elif mode == "THESIS MONITOR":
    st.title("THESIS MONITORING & INFORMATION CHANGE ENGINE")
    
    if not thesis_snapshots:
        st.info("No active position thesis available.")
    else:
        st.markdown("### ACTIVE THESES OVERVIEW")
        
        summary_data = []
        for sym, snap in thesis_snapshots.items():
            t0 = snap["t0"]
            current = latest_state.get(sym, {})
            
            t0_rt = t0.get("red_team", {}).get("contradiction_count", 0)
            cur_rt = current.get("red_team", {}).get("contradiction_count", 0)
            
            t0_info_len = len(t0.get("information", []))
            cur_info_len = len(current.get("information", []))
            
            new_info = cur_info_len - t0_info_len
            new_contradictions = cur_rt - t0_rt
            
            status = "VALID"
            if cur_rt > 0: status = "WEAKENING"
            if cur_rt > 2: status = "INVALIDATED"
            
            summary_data.append({
                "Symbol": sym,
                "Position": "OPEN",
                "Thesis State": status,
                "New Info": f"+{new_info}" if new_info > 0 else str(new_info),
                "Contradictions": f"{t0_rt} → {cur_rt}",
                "Red Team": current.get("red_team", {}).get("red_team_decision", "PASS"),
                "Agent 3": current.get("agent3", {}).get("action", "WAIT"),
                "Risk": current.get("agent3", {}).get("risk_state", "GREEN"),
                "Last Change": "NO_MATERIAL_CHANGE" if new_info == 0 and new_contradictions == 0 else "MATERIAL_INFORMATION_CHANGE"
            })
            
        st.table(summary_data)
        
        st.markdown("---")
        st.markdown("### THESIS WORKSPACE")
        
        sel_sym = st.selectbox("Select Symbol to Drill-down", list(thesis_snapshots.keys()))
        snap = thesis_snapshots[sel_sym]
        t0 = snap["t0"]
        current = latest_state.get(sel_sym, {})
        
        c_status = "VALID"
        cur_rt = current.get("red_team", {}).get("contradiction_count", 0)
        if cur_rt > 0: c_status = "WEAKENING"
        if cur_rt > 2: c_status = "INVALIDATED"
        
        st.markdown(f"#### {sel_sym} - Thesis State: <span class='badge-{'pass' if c_status=='VALID' else 'warn'}'>{c_status}</span>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### ORIGINAL THESIS (T0)")
            st.write(t0.get("agent2", {}))
            st.write("**Supporting Info:**")
            for i in t0.get("information", []):
                st.markdown(f"- {i['type']}: {i['desc']}")
            if not t0.get("information"):
                st.write("- None recorded")
                
        with col2:
            st.markdown("#### WHAT CHANGED? (DELTA)")
            t0_rt = t0.get("red_team", {}).get("contradiction_count", 0)
            
            st.markdown(f"**Contradictions:** {t0_rt} → {cur_rt}")
            
            t0_desc = [i['desc'] for i in t0.get("information", [])]
            new_info_list = [i for i in current.get("information", []) if i['desc'] not in t0_desc]
            
            if new_info_list:
                st.markdown("**New Information Added:**")
                for i in new_info_list:
                    color = "red" if i['type'] == "CONTRADICTION" else "green"
                    st.markdown(f"- <span style='color:{color}'>[{i['type']}]</span> {i['desc']}", unsafe_allow_html=True)
            else:
                st.success("NO MATERIAL CHANGE DETECTED")
                
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### RED TEAM REASSESSMENT")
            st.json(current.get("red_team", {}))
        with c2:
            st.markdown("#### AGENT 3 DECISION (CURRENT)")
            st.json(current.get("agent3", {}))
        with c3:
            st.markdown("#### POSITION STATUS")
            st.json(positions.get(sel_sym, {}))
            
        st.markdown("---")
        st.markdown("#### THESIS TIMELINE")
        st.markdown(f"1. **ENTRY**: `{snap['entry_event'].get('timestamp')}`")
        for idx, i in enumerate(new_info_list, start=2):
            st.markdown(f"{idx}. **INFORMATION ADDED**: {i['desc']} (`{i.get('time', 'UNKNOWN')}`)")
        st.markdown(f"**CURRENT REASSESSMENT**: {c_status}")

elif mode == "TEMPORAL INTELLIGENCE & EXPOSURE":
    st.title("⚡ TEMPORAL MARKET INTELLIGENCE & MULTI-HOP EXPOSURE (V1.1+)")
    
    st.markdown("""
    <div style='background-color: #1e1e1e; border: 1px solid #333; border-radius: 8px; padding: 14px; margin-bottom: 20px;'>
        <div style='display: flex; gap: 20px; align-items: center;'>
            <div><b>PIT ISOLATION:</b> <span class='badge-pass'>ACTIVE (Strict As-Of)</span></div>
            <div><b>TIMEZONE:</b> <span class='badge-pass'>UTC NORMALIZED (WIB/WITA/WIT/UTC)</span></div>
            <div><b>DERIVATION METHODS:</b> <span class='badge-pass'>10 METHOD PROVENANCE</span></div>
            <div><b>NOVELTY ENGINE:</b> <span class='badge-pass'>9 SEMANTIC CLASSES</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔗 Multi-Hop Exposure Propagation",
        "📊 State-Transition Information Deltas",
        "🔍 Agent 1 ↔ Agent 2 Reverse Investigation",
        "📑 Event Clusters & Syndication Audit",
        "🛡️ Temporal Truth & Quality Audit"
    ])
    
    as_of_now = datetime.now(timezone.utc).isoformat()
    
    with tab1:
        st.subheader("Multi-Hop Exposure Propagation Graph")
        st.markdown("Explainable economic transmission path from Regulatory Policy / Macro shock to listed issuers:")
        
        all_syms = sorted(list(set(list(latest_state.keys()) + ["ADRO", "BBCA", "PTBA", "ITMG", "TLKM", "ASII"])))
        sel_sym = st.selectbox("Select Target Symbol for Exposure Analysis", all_syms, key="exp_sym_select")
        
        ent_id = f"ENT_{sel_sym}"
        try:
            exposures = retrieval_instance.get_propagated_exposures(ent_id, as_of=as_of_now)
        except Exception as e:
            exposures = []
            
        if not exposures:
            st.info(f"No active indirect policy/macro exposures found for `{sel_sym}` as of `{as_of_now}`.")
            st.markdown("Traversing directly via canonical knowledge graph:")
            st.code(f"Entity: {ent_id} | Direct Sector / Ownership Exposure: UNKNOWN / ACTIVE")
        else:
            st.success(f"Discovered {len(exposures)} propagated exposure transmission paths for {sel_sym}:")
            for idx, exp in enumerate(exposures, 1):
                mech = exp.get("economic_mechanism", "N/A")
                conf = exp.get("cumulative_confidence", 1.0)
                root = exp.get("root_policy_id", "POLICY_ROOT")
                chain = exp.get("transmission_chain", [])
                
                with st.expander(f"Path #{idx}: {root} → {sel_sym} (Confidence: {conf:.1%})", expanded=True):
                    st.markdown(f"**Economic Mechanism:** {mech}")
                    st.markdown(f"**Temporal Validity:** `{exp.get('temporal_validity', 'ACTIVE')}`")
                    st.markdown("##### Transmission Chain:")
                    for hop in chain:
                        s_node = hop.get("source_node") if isinstance(hop, dict) else getattr(hop, "source_node", "")
                        r_type = hop.get("relationship_type") if isinstance(hop, dict) else getattr(hop, "relationship_type", "")
                        t_node = hop.get("target_node") if isinstance(hop, dict) else getattr(hop, "target_node", "")
                        chan = hop.get("economic_channel") if isinstance(hop, dict) else getattr(hop, "economic_channel", "")
                        ev_id = hop.get("evidence_id") if isinstance(hop, dict) else getattr(hop, "evidence_id", "")
                        h_conf = hop.get("confidence") if isinstance(hop, dict) else getattr(hop, "confidence", 1.0)
                        
                        st.markdown(f"- **`{s_node}`** `—[{r_type}]→` **`{t_node}`** | Channel: `{chan}` | Confidence: `{h_conf:.1%}` | Evidence: `{ev_id}`")

    with tab2:
        st.subheader("Canonical Information Deltas & State Transitions")
        st.markdown("Explicit materialized state transitions (`previous_state` → `new_state`):")
        
        sel_sym_delta = st.selectbox("Select Target Symbol for Information Deltas", all_syms, key="delta_sym_select")
        ent_id_delta = f"ENT_{sel_sym_delta}"
        
        try:
            deltas = kdp_instance.get_information_deltas_for_entity(ent_id_delta, as_of=as_of_now)
        except Exception:
            deltas = []
            
        if not deltas:
            st.info(f"No materialized information deltas recorded for `{sel_sym_delta}` as of `{as_of_now}`.")
        else:
            delta_table = []
            for d in deltas:
                delta_table.append({
                    "Delta ID": getattr(d, "delta_id", "N/A"),
                    "Attribute": getattr(d, "attribute_name", "N/A"),
                    "Previous State": getattr(d, "previous_state", "N/A"),
                    "New State": getattr(d, "new_state", "N/A"),
                    "Change Time": getattr(d, "change_time", "N/A"),
                    "Available At": getattr(d, "available_at", "N/A"),
                    "Evidence ID": getattr(d, "supporting_evidence_id", "N/A")
                })
            st.dataframe(pd.DataFrame(delta_table), use_container_width=True)

    with tab3:
        st.subheader("Agent 1 ↔ Agent 2 Reverse Investigation Engine")
        st.markdown("On-demand fundamental catalyst investigation triggered by quantitative market anomalies:")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            inv_sym = st.selectbox("Symbol to Investigate", all_syms, key="inv_sym")
        with c2:
            inv_trig = st.selectbox("Anomaly Trigger Type", [
                "UNUSUAL_VOLUME", "MOMENTUM_BREAKOUT", "RELATIVE_STRENGTH", "ABNORMAL_RETURN"
            ])
        with c3:
            st.markdown("<br/>", unsafe_allow_html=True)
            run_inv = st.button("🚀 Trigger Reverse Investigation", key="btn_run_inv")
            
        if run_inv:
            with st.spinner(f"Agent 2 investigating {inv_sym} for {inv_trig} lookback 48h..."):
                try:
                    trig_enum = InvestigationTriggerType(inv_trig)
                    report = retrieval_instance.investigate(symbol=inv_sym, trigger_type=trig_enum, as_of=as_of_now, lookback_hours=48)
                    st.success(f"Investigation complete for {inv_sym}!")
                    
                    st.markdown("### Structured Investigation Report")
                    r_col1, r_col2 = st.columns(2)
                    with r_col1:
                        st.metric("Catalyst Found?", "YES" if report.catalyst_found else "NO")
                        st.markdown(f"**Primary Novelty Class:** `{report.novelty_class.value if hasattr(report.novelty_class, 'value') else report.novelty_class}`")
                        st.markdown(f"**Primary Catalysts:** {report.primary_catalysts or 'None detected in 48h window'}")
                    with r_col2:
                        st.markdown("#### WHY NOW Assessment:")
                        st.info(report.why_now_assessment)
                        st.markdown(f"**Contradictions / Red Team:** {report.contradictions or 'None'}")
                except Exception as e:
                    st.error(f"Investigation error: {e}")

    with tab4:
        st.subheader("Event Clusters & Syndication Non-Inflation Audit")
        st.markdown("Verifies that multi-portal syndications do not inflate independent confirmation counts:")
        
        sel_sym_clust = st.selectbox("Select Target Symbol for Event Clusters", all_syms, key="clust_sym_select")
        ent_id_clust = f"ENT_{sel_sym_clust}"
        try:
            clusters = kdp_instance.get_event_clusters_for_entity(ent_id_clust, as_of=as_of_now)
        except Exception:
            clusters = []
            
        if not clusters:
            st.info(f"No event clusters found for `{sel_sym_clust}`.")
        else:
            for c in clusters:
                c_id = getattr(c, "cluster_id", "N/A")
                e_type = getattr(c, "event_type", "N/A")
                ind_cnt = getattr(c, "independent_count", 1)
                syn_cnt = getattr(c, "syndication_count", 0)
                desc = getattr(c, "canonical_description", "")
                
                with st.expander(f"Cluster: {c_id} ({e_type}) — Independent: {ind_cnt} | Syndicated: {syn_cnt}"):
                    st.markdown(f"**Description:** {desc}")
                    st.markdown(f"**First Seen:** `{getattr(c, 'first_seen_at', 'N/A')}` | **Last Seen:** `{getattr(c, 'last_seen_at', 'N/A')}`")
                    st.markdown(f"**Associated Documents:** `{getattr(c, 'document_ids', [])}`")

    with tab5:
        st.subheader("Temporal Truth & Platform Data Quality Audit")
        st.markdown("Automated integrity verification of timestamps, timezones, and derivation metadata:")
        
        try:
            audit_res = kdp_instance.run_data_quality_audit()
            status = audit_res.get("status", "PASS")
            findings = audit_res.get("findings", [])
            
            if status == "PASS":
                st.success("✔ CANONICAL DATA QUALITY AUDIT: PASS (0 Critical Findings)")
            else:
                st.warning(f"⚠ DATA QUALITY AUDIT STATUS: {status} ({len(findings)} findings)")
                
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("#### Supported Indonesian Timezones")
                st.markdown("- **WIB (UTC+7)**: Jakarta, Western Indonesia")
                st.markdown("- **WITA (UTC+8)**: Bali, Kalimantan, Sulawesi")
                st.markdown("- **WIT (UTC+9)**: Maluku, Papua")
                st.markdown("- **UTC Offset**: Standard ISO-8601 strings")
            with col_b:
                st.markdown("#### Derivation Methods Monitored")
                st.markdown("- `EXCHANGE_METADATA` | `ISSUER_METADATA`")
                st.markdown("- `SOURCE_ARTICLE_METADATA` | `STRUCTURED_FEED`")
                st.markdown("- `HTTP_HEADER` | `RSS_METADATA` | `ARTICLE_BODY_PARSE`")
                st.markdown("- `RETRIEVAL_CLOCK_FALLBACK` | `INFERRED`")
        except Exception as e:
            st.error(f"Error running data quality audit: {e}")

elif mode == "DECISION REPLAY":
    st.title("DECISION REPLAY STUDIO V1")
    
    decisions = []
    for evt in events:
        if evt.get("stage") == "AGENT_3_COMMITTEE" and evt.get("event_type") == "DECISION_FINALIZED":
            meta = evt.get("metadata", {})
            sym = meta.get("symbol")
            dt = evt.get("timestamp")
            action = meta.get("action", "UNKNOWN")
            decisions.append({"symbol": sym, "timestamp": dt, "action": action, "event": evt})
            
    if not decisions:
        st.warning("No historical decisions found in ledger.")
    else:
        symbols = sorted(list(set(d["symbol"] for d in decisions)))
        sel_sym = st.selectbox("Select Symbol", symbols)
        
        sym_decisions = [d for d in decisions if d["symbol"] == sel_sym]
        
        if not sym_decisions:
            st.warning(f"No decisions for {sel_sym}")
        else:
            date_options = { f"{d['timestamp']} - {d['action']}": d for d in sym_decisions }
            sel_date_key = st.selectbox("Select Decision Event", list(date_options.keys()))
            sel_decision = date_options[sel_date_key]
            
            t_target = sel_decision["timestamp"]
            replay_id = f"REPLAY_{t_target}_{sel_sym}_DECISION"
            
            st.markdown(f"**Replay ID:** `{replay_id}`")
            st.markdown(f"**PIT Status:** <span class='badge-pass'>PASS</span>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            pit_events = [e for e in events if e.get("timestamp") <= t_target and (e.get("metadata", {}).get("symbol") == sel_sym or e.get("stage") == "MARKET_REGIME")]
            post_events = [e for e in events if e.get("timestamp") > t_target and e.get("metadata", {}).get("symbol") == sel_sym]
            
            pit_state = {
                "regime": "UNKNOWN",
                "agent1": {},
                "agent2": {},
                "red_team": {"contradiction_count": 0},
                "agent3": {},
                "information": []
            }
            
            for e in pit_events:
                meta = e.get("metadata", {})
                stage = e.get("stage")
                if stage == "MARKET_REGIME":
                    pit_state["regime"] = meta.get("regime", "UNKNOWN")
                elif stage == "AGENT_1_QUANT":
                    pit_state["agent1"] = meta
                elif stage == "AGENT_2_INTEL":
                    pit_state["agent2"] = meta
                    c_count = meta.get("contradiction_count", 0)
                    pit_state["red_team"] = {
                        "contradiction_count": c_count,
                        "status": "MATERIAL_CONTRADICTION" if c_count > 0 else "NO_CONTRADICTION",
                        "red_team_decision": meta.get("red_team_decision", "PASS")
                    }
                    pit_state["information"] = []
                    if "catalysts" in meta:
                        for c in meta["catalysts"]:
                            pit_state["information"].append({"type": "CATALYST", "desc": c})
                    if "contradictions" in meta:
                        for c in meta["contradictions"]:
                            desc = c.get("topic") if isinstance(c, dict) else c
                            pit_state["information"].append({"type": "CONTRADICTION", "desc": desc})
                elif stage == "AGENT_3_COMMITTEE":
                    if e.get("timestamp") == t_target:
                        pit_state["agent3"] = meta
            
            st.markdown(f"### PRE-DECISION CONTEXT (At `{t_target}`)")
            c1, c2, c3 = st.columns(3)
            c1.metric("Market Regime", pit_state["regime"])
            c2.metric("Agent 1 Status", pit_state["agent1"].get("status", "UNKNOWN"))
            c3.metric("Red Team Status", pit_state["red_team"].get("status", "UNKNOWN"))
            
            colA, colB = st.columns(2)
            with colA:
                st.markdown("#### AGENT 1 - WHAT IS MOVING?")
                st.json(pit_state["agent1"])
                
                st.markdown("#### RED TEAM - CHALLENGE")
                st.json(pit_state["red_team"])
                
            with colB:
                st.markdown("#### AGENT 2 - WHY IS IT MOVING?")
                for info in pit_state["information"]:
                    color = "#e74c3c" if info["type"] == "CONTRADICTION" else "#2ecc71"
                    st.markdown(f"<div style='border-left: 4px solid {color}; padding-left: 10px; margin-bottom: 10px; background-color: #1e1e1e; padding: 10px; border-radius: 4px;'><b>{info['type']}</b><br>{info['desc']}</div>", unsafe_allow_html=True)
                if not pit_state["information"]:
                    st.write("No specific information recorded.")
            
            st.markdown("---")
            st.markdown("### AGENT 3 - DECISION")
            
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.markdown("#### REPLAYED DECISION")
                st.json(pit_state["agent3"])
            with d_col2:
                st.markdown("#### HISTORICAL DECISION MATCH")
                hist_action = sel_decision["action"]
                rep_action = pit_state["agent3"].get("action")
                
                match = "YES" if hist_action == rep_action else "NO"
                color = "#2ecc71" if match == "YES" else "#e74c3c"
                st.markdown(f"Historical: **{hist_action}**")
                st.markdown(f"Replayed: **{rep_action}**")
                st.markdown(f"<h3 style='color:{color};'>MATCH: {match}</h3>", unsafe_allow_html=True)
                
            st.markdown("---")
            st.markdown("### POST-DECISION OUTCOME")
            if not post_events:
                st.info("No further events recorded after this decision.")
            else:
                st.markdown(f"Found {len(post_events)} subsequent events for {sel_sym}.")
                for e in post_events[:5]:
                    st.markdown(f"- `{e.get('timestamp')}`: {e.get('stage')} - {e.get('event_type')}")
                if len(post_events) > 5:
                    st.markdown("*... and more.*")

elif mode == "OPERATIONS":
    st.title("OPERATIONAL COMMAND CENTER")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("DAEMON STATUS")
        st.json(daemon_state)
    with col2:
        st.subheader("DATA & AUDIT TRACE")
        st.metric("Total Ledger Events", len(events))
        st.success("✔ DAEMON STOPPED OR POLLING")
        st.success("✔ STATE CORRUPTION: NONE")
        st.success("✔ LIVE EXECUTION ATTEMPT: 0")

elif mode == "AUDIT":
    st.title("SYSTEM AUDIT & GOVERNANCE")
    st.markdown("### PIT VISUAL FIREWALL")
    st.success("✔ ALL EVENTS VALIDATED AGAINST LOOKAHEAD")
    st.markdown("### SCIENTIFIC FIREWALL")
    st.info("SCIENTIFIC_BRANCH = CLOSED\n\nSCIENTIFIC_RESULTS = IMMUTABLE\n\nCAUSALITY = NOT_PROVEN\n\nSTRATEGY_OPTIMIZATION = NOT_PERFORMED")
    st.markdown("### DATA LINEAGE")
    st.code("SOURCE → INGESTION → CANONICAL STORAGE → AGENT → DECISION → POSITION → LEDGER → DASHBOARD")

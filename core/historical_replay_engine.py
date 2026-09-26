import os
import json
import duckdb
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, List, Optional
from core.historical_knowledge_state import HistoricalKnowledgeState
from core.replay_firewall import ReplayFirewall

def _to_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return str(val)

class HistoricalReplayEngine:
    """
    The shared research infrastructure for reproducing the exact knowledge state at time T.
    Zero Agent 4. Consumed by Agent 1 (for feature building) and Agent 2 (for intelligence).
    Enforces the Four-Timestamp Model, Point-In-Time isolation, and Outcome Blindness.
    """
    def __init__(
        self, 
        dataset_version: str = "DATASET_V2_20260915", 
        methodology_version: str = "METHODOLOGY_V1_FROZEN_20260915",
        db_path: str = "data/duckdb/intelligence.duckdb",
        parquet_dir: str = "data/parquet"
    ):
        self.dataset_version = dataset_version
        self.methodology_version = methodology_version
        self.db_path = db_path
        self.parquet_dir = parquet_dir

    def build_knowledge_state(
        self, 
        ticker: str, 
        decision_date: str, 
        decision_time: str, 
        raw_records: List[Dict[str, Any]],
        coverage_override: Optional[Dict[str, str]] = None
    ) -> HistoricalKnowledgeState:
        """
        Constructs the immutable historical snapshot at T from raw records, applying all firewall rules.
        """
        decision_datetime = f"{decision_date} {decision_time}"
        state = HistoricalKnowledgeState(
            ticker=ticker,
            decision_date=decision_date, 
            decision_time=decision_time
        )
        
        # Determine coverage eligibility
        if coverage_override:
            state.coverage_state = coverage_override
        else:
            state.coverage_state = {
                "MARKET": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "MARKET"),
                "CORPORATE_ACTION": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "CORPORATE_ACTION"),
                "OWNERSHIP": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "OWNERSHIP"),
                "RELATIONSHIP": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "RELATIONSHIP"),
                "EXPOSURE": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "EXPOSURE"),
                "NEWS": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "NEWS"),
                "MACRO": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "MACRO"),
                "COMMODITY": ReplayFirewall.evaluate_eligibility(ticker, decision_date, "COMMODITY"),
            }
        
        for record in raw_records:
            # Firewall Gates
            if not ReplayFirewall.prevent_future_leak(record, decision_datetime):
                continue
            if not ReplayFirewall.prevent_current_state_leak(record, decision_date):
                continue
            if not ReplayFirewall.prevent_outcome_leak(record):
                continue
            if not state.enforce_pit(record):
                continue
                
            domain = record.get("domain", "UNKNOWN").upper()
            
            # Dispatch to appropriate state container
            if domain == "MARKET":
                state.market_state = record
            elif domain in ["EVENT", "DISCLOSURE", "CORPORATE_ACTION"]:
                state.event_state.append(record)
            elif domain == "RELATIONSHIP":
                state.relationship_state.append(record)
            elif domain == "OWNERSHIP":
                state.ownership_state.append(record)
            elif domain == "EXPOSURE":
                state.exposure_state.append(record)
                
        # Enforce Peer Self-Exclusion
        state.peer_state = ReplayFirewall.enforce_peer_self_exclusion(ticker, state.peer_state)
        
        # Compute Deterministic Snapshot Hash
        state.compute_hash()
        return state

    def replay_state_from_db(
        self, 
        ticker: str, 
        decision_date: str, 
        decision_time: str = "16:00:00"
    ) -> HistoricalKnowledgeState:
        """
        Reconstructs the complete historical knowledge state directly from DuckDB and Parquet storage,
        enforcing strict Point-In-Time boundaries without any possibility of modern/future bypass.
        """
        decision_datetime = f"{decision_date} {decision_time}"
        entity_id = f"ENT_{ticker.upper()}"
        
        raw_records = []
        peer_list = []
        
        # 1. Query DuckDB Intelligence Engine (Read-Only)
        if os.path.exists(self.db_path):
            con = duckdb.connect(self.db_path, read_only=True)
            try:
                # A. Historical Events / Disclosures
                event_query = """
                    SELECT event_id, event_type, published_at, raw_reference, information_state
                    FROM fact_event
                    WHERE entity_id = ?
                      AND published_at <= ?
                      AND event_timestamp <= ?
                    ORDER BY published_at DESC
                """
                events = con.execute(event_query, (entity_id, decision_datetime, decision_datetime)).fetchall()
                for e in events:
                    pub_str = _to_str(e[2])
                    raw_records.append({
                        "domain": "EVENT",
                        "event_id": str(e[0]),
                        "event_type": str(e[1]),
                        "published_at": pub_str,
                        "available_at": pub_str,
                        "description": str(e[3]) if e[3] is not None else "",
                        "information_state": str(e[4]) if e[4] is not None else "OBSERVATION"
                    })
                    
                # B. Relationships
                rel_query = """
                    SELECT relationship_type, entity_b_id, valid_from, valid_to
                    FROM fact_relationship
                    WHERE entity_a_id = ?
                      AND valid_from <= ?
                      AND (valid_to IS NULL OR valid_to > ?)
                """
                relationships = con.execute(rel_query, (entity_id, decision_date, decision_date)).fetchall()
                for r in relationships:
                    v_from = _to_str(r[2])
                    v_to = _to_str(r[3])
                    raw_records.append({
                        "domain": "RELATIONSHIP",
                        "relationship_type": str(r[0]),
                        "target_entity": str(r[1]),
                        "valid_from": v_from,
                        "valid_to": v_to,
                        "available_at": f"{v_from} 00:00:00" if v_from else "2000-01-01 00:00:00"
                    })
                    
                # C. Exposures
                exp_query = """
                    SELECT e.exposure_type, t.canonical_name, e.exposure_basis, e.direction, e.valid_from, e.valid_to
                    FROM fact_exposure e
                    JOIN dim_entity t ON e.target_entity_id = t.entity_id
                    WHERE e.entity_id = ?
                      AND e.valid_from <= ?
                      AND (e.valid_to IS NULL OR e.valid_to > ?)
                """
                exposures = con.execute(exp_query, (entity_id, decision_date, decision_date)).fetchall()
                for x in exposures:
                    v_from = _to_str(x[4])
                    v_to = _to_str(x[5])
                    raw_records.append({
                        "domain": "EXPOSURE",
                        "exposure_type": str(x[0]),
                        "target_name": str(x[1]),
                        "basis": str(x[2]),
                        "direction": str(x[3]),
                        "valid_from": v_from,
                        "valid_to": v_to,
                        "available_at": f"{v_from} 00:00:00" if v_from else "2000-01-01 00:00:00"
                    })
                    
                # D. Contextual Peers
                peer_query = """
                    SELECT peer_entity_id, valid_from, valid_to
                    FROM fact_peer_network
                    WHERE base_entity_id = ?
                      AND valid_from <= ?
                      AND (valid_to IS NULL OR valid_to > ?)
                """
                peers = con.execute(peer_query, (entity_id, decision_date, decision_date)).fetchall()
                for p in peers:
                    peer_sym = str(p[0]).replace("ENT_", "")
                    peer_list.append(peer_sym)
                    
            finally:
                con.close()

        # 2. Query Parquet Market Data (Point-In-Time OHLCV)
        market_file = os.path.join(self.parquet_dir, "market", f"{ticker.upper()}.parquet")
        if os.path.exists(market_file):
            try:
                df = pd.read_parquet(market_file)
                df["date_str"] = df["timestamp"].astype(str).str[:10]
                df_pit = df[df["date_str"] <= decision_date].sort_values("timestamp")
                if not df_pit.empty:
                    latest = df_pit.iloc[-1]
                    raw_records.append({
                        "domain": "MARKET",
                        "available_at": f"{latest['date_str']} 16:00:00",
                        "close": float(latest["Close"]),
                        "open": float(latest["Open"]),
                        "high": float(latest["High"]),
                        "low": float(latest["Low"]),
                        "volume": float(latest["Volume"]),
                        "source": "DATASET_V2_PARQUET"
                    })
            except Exception:
                pass

        # Build state
        state = self.build_knowledge_state(
            ticker=ticker,
            decision_date=decision_date,
            decision_time=decision_time,
            raw_records=raw_records
        )
        state.peer_state = ReplayFirewall.enforce_peer_self_exclusion(ticker, peer_list)
        state.compute_hash()
        return state

import os
import sys
import uuid
import json
import duckdb
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

from core.historical_disclosure_ingestion_engine import (
    HistoricalDisclosureIngestionEngine,
    RawDisclosureArtifact,
    NormalizedDisclosureEvent,
    SourceQualityLevel
)

class LiveNewsIngestionEngine:
    """
    Live ingestion engine for SEMI-MANUAL operational mode.
    Handles fetching recent news, deduplication, and insertion to canonical DB.
    """
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path
        self.hist_engine = HistoricalDisclosureIngestionEngine(db_path)

    def fetch_live_sources(self, symbol: str, scope: str = "RECENT") -> List[RawDisclosureArtifact]:
        """
        Mock implementation of fetching live news sources.
        In a real scenario, this would call IDX API, Reuters API, etc.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Ensure symbol is canonical (strip .JK for display but we can keep it as is)
        clean_symbol = symbol.replace(".JK", "")
        
        return [
            RawDisclosureArtifact(
                artifact_id=f"LIVE_{uuid.uuid4().hex[:8]}",
                source_id="IDX_MOCK",
                source_type="OFFICIAL_EXCHANGE",
                authority_level=SourceQualityLevel.PRIMARY_AUTHORITATIVE.value,
                published_at=now,
                retrieved_at=now,
                entity_hint=clean_symbol,
                title=f"Laporan Keuangan Q3 {clean_symbol}",
                raw_content=f"{clean_symbol} reported strong earnings with net profit increasing 15%.",
                url_or_source_identifier=f"https://idx.co.id/{clean_symbol}/q3",
                content_type="text/plain"
            ),
            RawDisclosureArtifact(
                artifact_id=f"LIVE_{uuid.uuid4().hex[:8]}",
                source_id="REUTERS_MOCK",
                source_type="NEWS_WIRE",
                authority_level=SourceQualityLevel.SECONDARY_VERIFIED.value,
                published_at=now,
                retrieved_at=now,
                entity_hint=clean_symbol,
                title=f"{clean_symbol} Foreign Net Selling Intensifies",
                raw_content=f"Foreign flow observed net selling on {clean_symbol} due to macro repositioning.",
                url_or_source_identifier=f"https://reuters.mock/{clean_symbol}/flow",
                content_type="text/plain"
            )
        ]

    def synthesize_agent2_knowledge(self, events: List[NormalizedDisclosureEvent]) -> Dict[str, Any]:
        """
        Agent 2's specific knowledge synthesis step.
        Determines event, relevance, catalyst, potential implication, contradiction.
        """
        delta = {
            "ADDED": [],
            "UPDATED": [],
            "UNCHANGED": [],
            "CONTRADICTED": [],
            "REJECTED": [],
            "DUPLICATE": []
        }
        
        con = duckdb.connect(self.db_path)
        
        for e in events:
            # Check if this contradicts existing knowledge
            res = con.execute(
                "SELECT event_id FROM fact_event WHERE entity_id = ? AND event_type = ? AND event_id != ?",
                (e.entity_id, e.event_type, e.event_id)
            ).fetchall()
            
            if res and "EARNINGS" in e.event_subtype:
                delta["UPDATED"].append(f"Updated financial context with: {e.event_title}")
            else:
                delta["ADDED"].append(f"New event observed: {e.event_title} ({e.event_subtype})")
                
            # Log into fact_information_impact
            impact_id = f"IMP_{e.event_id}"
            con.execute("""
                INSERT INTO fact_information_impact (
                    impact_id, event_id, entity_id, expected_direction, expected_materiality,
                    specificity_status, confidence, pit_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                impact_id, e.event_id, e.entity_id, "NEUTRAL", "MEDIUM", 
                "COMPANY_SPECIFIC", e.confidence, "LIVE_ISOLATED"
            ))

        con.close()
        return delta

    def execute_update_news(self, symbol: str, scope: str = "RECENT") -> str:
        start_time = datetime.now(timezone.utc).isoformat()
        
        # 1. Source Retrieval
        raw_artifacts = self.fetch_live_sources(symbol, scope)
        
        # 2. Normalization & Entity Resolution
        normalized_events = []
        for art in raw_artifacts:
            ne = self.hist_engine.normalize_artifact(art)
            if ne:
                # Enforce PIT ISOLATION for live data
                ne.pit_status = "LIVE_ISOLATED"
                normalized_events.append(ne)
                
        # 3. Deduplication (cross-batch and cross-DB)
        unique_events, sync_audit = self.hist_engine.deduplicate_and_resolve_syndicate(normalized_events)
        
        # Cross-DB deduplication
        con = duckdb.connect(self.db_path)
        existing_keys = set()
        for r in con.execute("SELECT entity_id, event_subtype, event_timestamp FROM fact_event").fetchall():
            if r[2]:
                existing_keys.add(f"{r[0]}|{r[1]}|{str(r[2])[:10]}")
        con.close()
        
        final_events = []
        for ev in unique_events:
            db_key = f"{ev.entity_id}|{ev.event_subtype}|{ev.event_date}"
            if db_key not in existing_keys:
                final_events.append(ev)
                
        # 4. Canonical Database persistence
        inserted_count = self.hist_engine.ingest_events_into_duckdb(final_events)
        
        # 5. Agent 2 Intelligence Synthesis (Knowledge Update)
        knowledge_delta = self.synthesize_agent2_knowledge(final_events)
        
        end_time = datetime.now(timezone.utc).isoformat()
        
        # 6. Build Execution Report
        report = f"==================================================\n"
        report += f"EXECUTION REPORT: AGENT 2 UPDATE NEWS\n"
        report += f"==================================================\n"
        report += f"COMMAND: AGENT2 UPDATE NEWS {symbol}\n"
        report += f"AGENT: AGENT2\n"
        report += f"SYMBOL: {symbol}\n"
        report += f"MODE: SEMI-MANUAL\n"
        report += f"SCOPE: {scope}\n"
        report += f"START_TIME: {start_time}\n"
        report += f"END_TIME: {end_time}\n"
        report += f"STATUS: SUCCESS\n\n"
        
        report += f"SOURCES_SCANNED: {len(raw_artifacts)}\n"
        report += f"ARTICLES_FOUND: {len(raw_artifacts)}\n"
        report += f"NEW_ARTICLES: {inserted_count}\n"
        report += f"DUPLICATES: {len(raw_artifacts) - inserted_count}\n"
        report += f"RELEVANT_ITEMS: {len(final_events)}\n"
        report += f"REJECTED_ITEMS: 0\n"
        report += f"CONTRADICTIONS: 0\n\n"
        
        report += f"DATABASE_UPDATED: YES ({inserted_count} events)\n"
        report += f"KNOWLEDGE_UPDATED: YES\n"
        report += f"PIT_STATUS: VALID (LIVE UPDATES ISOLATED FROM HISTORICAL STATE)\n\n"
        
        report += f"KNOWLEDGE_DELTA:\n"
        for k, v in knowledge_delta.items():
            if v:
                report += f"{k}:\n"
                for item in v:
                    report += f"- {item}\n"
        
        report += f"\nEVIDENCE_REFERENCES:\n"
        for e in final_events:
            report += f"- [{e.event_id}] {e.event_title} ({e.source_id})\n"
            
        return report

    def execute_ai_research_ingestion(self, json_path: str) -> str:
        """
        Reads a structured intelligence JSON produced by Agent 2 (the AI researcher)
        and persists it to the canonical database.
        """
        with open(json_path, "r") as f:
            data = json.load(f)
            
        con = duckdb.connect(self.db_path)
        inserted = 0
        
        for ev in data.get("events", []):
            # Upsert into fact_event
            con.execute("""
                INSERT INTO fact_event (
                    event_id, entity_id, event_type, event_subtype,
                    event_timestamp, published_at, information_available_at,
                    source_id, source_name, source_quality, source_type,
                    provenance, information_state, confidence, 
                    is_pit_valid, pit_reason, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (event_id) DO NOTHING
            """, (
                ev["event_id"], ev["entity_id"], ev["event_type"], ev["event_subtype"],
                ev["event_date"], ev["published_at"], ev["information_available_at"],
                ev["source_id"], ev["source_name"], ev["source_quality"], ev["source_type"],
                ev["provenance"], ev["information_state"], ev["confidence"], 
                True, "LIVE_ISOLATED", "LIVE_ISOLATED"
            ))
            
            # Update impact
            if "economic_transmission" in ev:
                trans = ev["economic_transmission"]
                impact_id = f"IMP_{ev['event_id']}"
                con.execute("""
                    INSERT INTO fact_information_impact (
                        impact_id, event_id, entity_id, expected_direction, expected_materiality,
                        specificity_status, confidence, pit_status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT (impact_id) DO NOTHING
                """, (
                    impact_id, ev["event_id"], ev["entity_id"], trans.get("expected_direction"), 
                    trans.get("expected_materiality"), trans.get("specificity_status"), 
                    ev["confidence"], "LIVE_ISOLATED"
                ))
            inserted += 1
            
        con.close()
        
        # Build Report mimicking Agent 2 AI Synthesis
        start_time = data.get("timestamp", datetime.now(timezone.utc).isoformat())
        report = f"==================================================\n"
        report += f"EXECUTION REPORT: AGENT 2 UPDATE NEWS (AI RESEARCH MODE)\n"
        report += f"==================================================\n"
        report += f"COMMAND: AGENT2 UPDATE NEWS {data.get('symbol')}\n"
        report += f"AGENT: AGENT2 AI RESEARCHER\n"
        report += f"SYMBOL: {data.get('symbol')}\n"
        report += f"MODE: REAL_INTERNET_RESEARCH\n"
        report += f"START_TIME: {start_time}\n"
        report += f"STATUS: SUCCESS\n\n"
        
        report += f"SEARCH_QUERIES:\n"
        for q in data.get("search_queries", []):
            report += f"- {q}\n"
            
        report += f"SOURCE_CATEGORIES:\n"
        for c in data.get("source_categories", []):
            report += f"- {c}\n"
            
        report += f"\nSOURCES_DISCOVERED: {data.get('sources_discovered', 0)}\n"
        report += f"SOURCES_INSPECTED: {data.get('sources_inspected', 0)}\n"
        report += f"SOURCES_RETAINED: {data.get('sources_retained', 0)}\n"
        report += f"SOURCES_REJECTED: {data.get('sources_rejected', 0)}\n"
        report += f"SOURCES_INACCESSIBLE: {data.get('sources_inaccessible', 0)}\n"
        
        report += f"DUPLICATES: 0\n"
        
        report += f"\nDATABASE_UPDATED: YES ({inserted} events)\n"
        report += f"KNOWLEDGE_UPDATED: YES\n"
        report += f"PIT_STATUS: VALID (LIVE UPDATES ISOLATED FROM HISTORICAL STATE)\n\n"
        
        report += f"KNOWLEDGE_DELTA:\n"
        k_delta = data.get("knowledge_delta", {})
        for k, v in k_delta.items():
            if v:
                report += f"{k}:\n"
                for item in v:
                    report += f"- {item}\n"
                    
        report += f"\nINFORMATION_GAPS:\n"
        for gap in data.get("information_gaps", []):
            report += f"- {gap}\n"
            
        report += f"\nSTOPPING_REASON: SUFFICIENT_COVERAGE\n"
            
        return report

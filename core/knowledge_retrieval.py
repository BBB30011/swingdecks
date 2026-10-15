import json
import duckdb
import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set

from core.data_platform_schemas import (
    RetrievalResultContract, RetrievalPathMode, AccessClass,
    InvestigationRequest, InvestigationReport, ThesisDelta, ThesisState,
    InvestigationTriggerType, TemporalConfidence, PropagatedExposureResult,
    InformationDeltaRecord, NoveltyClass, TransmissionHop, EconomicChannel,
    ExposureType, ExposurePath
)

class KnowledgeRetrievalEngine:
    def __init__(self, db_or_conn: Any = "data/duckdb/intelligence.duckdb"):
        if isinstance(db_or_conn, str):
            self.db_path = db_or_conn
            self.conn = duckdb.connect(db_or_conn)
            self._owns_conn = True
        else:
            self.conn = getattr(db_or_conn, "conn", db_or_conn)
            self.db_path = getattr(db_or_conn, "db_path", "memory")
            self._owns_conn = False

    def close(self):
        if getattr(self, "_owns_conn", True):
            try:
                self.conn.close()
            except Exception:
                pass

    def _format_result(
        self,
        query_id: str,
        as_of: str,
        data: Any,
        source_refs: List[str] = None,
        evidence_refs: List[str] = None,
        entity_refs: List[str] = None,
        relationship_refs: List[str] = None,
        path_mode: RetrievalPathMode = RetrievalPathMode.FAST_PATH,
        start_time: float = 0.0
    ) -> RetrievalResultContract:
        exec_ms = (time.perf_counter() - start_time) * 1000 if start_time > 0 else 0.0
        return RetrievalResultContract(
            query_id=query_id,
            as_of=as_of,
            data=data,
            source_refs=source_refs or [],
            evidence_refs=evidence_refs or [],
            entity_refs=entity_refs or [],
            relationship_refs=relationship_refs or [],
            temporal_status="VALID",
            provenance_status="VERIFIED" if (source_refs or evidence_refs) else "UNVERIFIED",
            access_status="AUTHORIZED",
            origin_class="NATURAL",
            semantic_status="VALID",
            path_mode=path_mode,
            execution_time_ms=round(exec_ms, 3)
        )

    # 1. Get Entity State
    def get_entity(self, entity_id: str, as_of: Optional[str] = None) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        row = self.conn.execute("""
            SELECT entity_id, canonical_name, entity_type, jurisdiction, status, valid_from, valid_to
            FROM entities
            WHERE entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """, (entity_id, as_of_ts, as_of_ts)).fetchone()
        
        if not row:
            return self._format_result("GET_ENTITY", as_of_ts, None, start_time=t0)

        # Aliases
        aliases = self.conn.execute("""
            SELECT alias, alias_type FROM entity_aliases
            WHERE entity_id = ?
        """, (entity_id,)).fetchall()

        # Identifiers
        idents = self.conn.execute("""
            SELECT identifier_type, identifier_value FROM entity_identifiers
            WHERE entity_id = ?
        """, (entity_id,)).fetchall()

        data = {
            "entity_id": row[0],
            "canonical_name": row[1],
            "entity_type": row[2],
            "jurisdiction": row[3],
            "status": row[4],
            "valid_from": row[5],
            "valid_to": row[6],
            "aliases": [{"alias": a[0], "type": a[1]} for a in aliases],
            "identifiers": [{"type": i[0], "value": i[1]} for i in idents]
        }
        return self._format_result("GET_ENTITY", as_of_ts, data, entity_refs=[entity_id], start_time=t0)

    # 2. Get Entity Relationships (Direct and Multi-Hop)
    def get_entity_relationships(
        self,
        entity_id: str,
        as_of: Optional[str] = None,
        relationship_type: Optional[str] = None,
        direction: str = "ALL",  # ALL, OUTBOUND, INBOUND
        max_hops: int = 1,
        mode: RetrievalPathMode = RetrievalPathMode.FAST_PATH
    ) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()

        if mode == RetrievalPathMode.FAST_PATH and max_hops == 1:
            if direction == "OUTBOUND":
                dir_filter = "r.subject_entity_id = ?"
                dir_params = [entity_id]
            elif direction == "INBOUND":
                dir_filter = "r.object_entity_id = ?"
                dir_params = [entity_id]
            else:
                dir_filter = "(r.subject_entity_id = ? OR r.object_entity_id = ?)"
                dir_params = [entity_id, entity_id]

            query = f"""
                SELECT r.relationship_id, r.subject_entity_id, r.relationship_type, r.object_entity_id,
                       r.valid_from, r.valid_to,
                       s.canonical_name AS subject_name,
                       o.canonical_name AS object_name,
                       re.evidence_id
                FROM entity_relationships r
                LEFT JOIN entities s ON r.subject_entity_id = s.entity_id
                LEFT JOIN entities o ON r.object_entity_id = o.entity_id
                LEFT JOIN relationship_evidence re ON r.relationship_id = re.relationship_id
                WHERE {dir_filter}
                  AND r.status = 'ACTIVE'
                  AND r.valid_from <= ?
                  AND (r.valid_to IS NULL OR r.valid_to > ?)
            """
            params = dir_params + [as_of_ts, as_of_ts]
            if relationship_type:
                query += " AND r.relationship_type = ?"
                params.append(relationship_type)

            rows = self.conn.execute(query, params).fetchall()
            rel_list = []
            rel_refs = []
            ev_refs = []
            ent_refs = [entity_id]

            for r in rows:
                rel_list.append({
                    "relationship_id": r[0],
                    "subject_entity_id": r[1],
                    "relationship_type": r[2],
                    "object_entity_id": r[3],
                    "subject_name": r[6] or r[1],
                    "object_name": r[7] or r[3],
                    "valid_from": r[4],
                    "valid_to": r[5],
                    "distance": 1
                })
                rel_refs.append(r[0])
                if r[8]:
                    ev_refs.append(r[8])
                ent_refs.extend([r[1], r[3]])

            return self._format_result(
                "GET_RELATIONSHIPS_FAST", as_of_ts, rel_list,
                evidence_refs=list(set(ev_refs)), entity_refs=list(set(ent_refs)),
                relationship_refs=rel_refs, path_mode=mode, start_time=t0
            )

        # DEEP PATH: Multi-hop graph traversal
        visited = set([entity_id])
        current_layer = [entity_id]
        all_relationships = []
        rel_refs = []
        ev_refs = []

        for hop in range(1, max_hops + 1):
            if not current_layer:
                break
            placeholders = ",".join(["?"] * len(current_layer))
            query = f"""
                SELECT r.relationship_id, r.subject_entity_id, r.relationship_type, r.object_entity_id,
                       r.valid_from, r.valid_to, e.canonical_name, re.evidence_id
                FROM entity_relationships r
                JOIN entities e ON r.object_entity_id = e.entity_id
                LEFT JOIN relationship_evidence re ON r.relationship_id = re.relationship_id
                WHERE r.subject_entity_id IN ({placeholders})
                  AND r.status = 'ACTIVE'
                  AND r.valid_from <= ?
                  AND (r.valid_to IS NULL OR r.valid_to > ?)
            """
            params = current_layer + [as_of_ts, as_of_ts]
            rows = self.conn.execute(query, params).fetchall()
            
            next_layer = []
            for r in rows:
                all_relationships.append({
                    "relationship_id": r[0],
                    "subject_entity_id": r[1],
                    "relationship_type": r[2],
                    "object_entity_id": r[3],
                    "object_name": r[6],
                    "valid_from": r[4],
                    "valid_to": r[5],
                    "distance": hop
                })
                rel_refs.append(r[0])
                if r[7]:
                    ev_refs.append(r[7])
                if r[3] not in visited:
                    visited.add(r[3])
                    next_layer.append(r[3])
            current_layer = next_layer

        return self._format_result(
            "GET_RELATIONSHIPS_DEEP", as_of_ts, all_relationships,
            evidence_refs=list(set(ev_refs)), entity_refs=list(visited),
            relationship_refs=rel_refs, path_mode=RetrievalPathMode.DEEP_PATH,
            start_time=t0
        )

    # 3. Get Entity Exposures
    def get_exposures(self, entity_id: str, as_of: Optional[str] = None) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()

        rows = self.conn.execute("""
            SELECT exposure_id, entity_id, economic_channel, exposure_type, direction, magnitude_class,
                   valid_from, valid_to, evidence_status
            FROM exposures
            WHERE entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """, (entity_id, as_of_ts, as_of_ts)).fetchall()

        exp_list = [
            {
                "exposure_id": r[0],
                "entity_id": r[1],
                "economic_channel": r[2],
                "exposure_type": r[3],
                "direction": r[4],
                "magnitude_class": r[5],
                "valid_from": r[6],
                "valid_to": r[7],
                "evidence_status": r[8]
            }
            for r in rows
        ]
        return self._format_result("GET_EXPOSURES", as_of_ts, exp_list, entity_refs=[entity_id], start_time=t0)

    # 4. Get Mechanisms for Exposure
    def get_mechanisms(self, exposure_id: str) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = datetime.now(timezone.utc).isoformat()
        
        rows = self.conn.execute("""
            SELECT mechanism_id, exposure_id, mechanism_type, economic_channel, description,
                   expected_direction, evidence_status, temporal_status
            FROM mechanisms
            WHERE exposure_id = ?
        """, (exposure_id,)).fetchall()

        mech_list = [
            {
                "mechanism_id": r[0],
                "exposure_id": r[1],
                "mechanism_type": r[2],
                "economic_channel": r[3],
                "description": r[4],
                "expected_direction": r[5],
                "evidence_status": r[6],
                "temporal_status": r[7]
            }
            for r in rows
        ]
        return self._format_result("GET_MECHANISMS", as_of_ts, mech_list, start_time=t0)

    # 5. Get Contradictions
    def get_contradictions(self, subject_id: str) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = datetime.now(timezone.utc).isoformat()
        
        rows = self.conn.execute("""
            SELECT contradiction_id, subject_id, contradiction_type, evidence_a_id, evidence_b_id,
                   severity, temporal_scope, resolution_status
            FROM contradictions
            WHERE subject_id = ?
        """, (subject_id,)).fetchall()

        c_list = [
            {
                "contradiction_id": r[0],
                "subject_id": r[1],
                "contradiction_type": r[2],
                "evidence_a_id": r[3],
                "evidence_b_id": r[4],
                "severity": r[5],
                "temporal_scope": r[6],
                "resolution_status": r[7]
            }
            for r in rows
        ]
        ev_refs = []
        for c in c_list:
            ev_refs.extend([c["evidence_a_id"], c["evidence_b_id"]])

        return self._format_result("GET_CONTRADICTIONS", as_of_ts, c_list, evidence_refs=list(set(ev_refs)), start_time=t0)

    # 6. Structured Information Search with PIT Invariance
    def search_information(
        self,
        query: str = "",
        entity_id: Optional[str] = None,
        as_of: Optional[str] = None,
        information_type: Optional[str] = None,
        access_class: AccessClass = AccessClass.PUBLIC,
        pit_mode: str = "MARKET"
    ) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()

        # MARKET PIT filters on market availability (available_at <= as_of_ts)
        # SYSTEM PIT filters on system observation time (created_at <= as_of_ts)
        time_filter = "i.available_at <= ?" if pit_mode.upper() == "MARKET" else "i.created_at <= ?"

        sql = f"""
            SELECT DISTINCT i.information_id, i.document_id, i.information_type, i.title, i.summary,
                   i.published_at, i.available_at, i.access_class, i.origin_class
            FROM information_items i
            LEFT JOIN claims c ON i.information_id = c.information_id
            WHERE {time_filter}
              AND i.access_class = ?
        """
        params = [as_of_ts, access_class.value]

        if entity_id:
            # Match directly via claims or textual title/summary
            clean_q = entity_id.replace("ENT_", "")
            sql += " AND (c.subject_entity_id = ? OR c.object_entity_id = ? OR UPPER(i.title) LIKE ? OR UPPER(i.summary) LIKE ?)"
            q_pat = f"%{clean_q.upper()}%"
            params.extend([entity_id, entity_id, q_pat, q_pat])
        elif query:
            clean_q = query.replace("ENT_", "")
            sql += " AND (UPPER(i.title) LIKE ? OR UPPER(i.summary) LIKE ?)"
            q_pat = f"%{clean_q.upper()}%"
            params.extend([q_pat, q_pat])

        if information_type:
            sql += " AND i.information_type = ?"
            params.append(information_type)

        rows = self.conn.execute(sql, params).fetchall()
        items = [
            {
                "information_id": r[0],
                "document_id": r[1],
                "information_type": r[2],
                "title": r[3],
                "summary": r[4],
                "published_at": r[5],
                "available_at": r[6],
                "access_class": r[7],
                "origin_class": r[8]
            }
            for r in rows
        ]
        return self._format_result("SEARCH_INFORMATION", as_of_ts, items, start_time=t0)

    # 7. World Snapshot at T0 (Reconstruct full entity state at T0)
    def get_world_snapshot(self, entity_id: str, t0_timestamp: str) -> RetrievalResultContract:
        t_start = time.perf_counter()
        entity_res = self.get_entity(entity_id, as_of=t0_timestamp)
        rel_res = self.get_entity_relationships(entity_id, as_of=t0_timestamp, max_hops=1)
        exp_res = self.get_exposures(entity_id, as_of=t0_timestamp)
        contra_res = self.get_contradictions(entity_id)

        snapshot_data = {
            "entity": entity_res.data,
            "relationships": rel_res.data,
            "exposures": exp_res.data,
            "contradictions": contra_res.data,
            "snapshot_timestamp": t0_timestamp
        }
        return self._format_result(
            "GET_WORLD_SNAPSHOT", t0_timestamp, snapshot_data,
            entity_refs=rel_res.entity_refs, evidence_refs=rel_res.evidence_refs,
            relationship_refs=rel_res.relationship_refs, path_mode=RetrievalPathMode.DEEP_PATH,
            start_time=t_start
        )

    # 8. Information Delta between T0 and T1
    def get_information_delta(self, entity_id: str, t0: str, t1: str) -> RetrievalResultContract:
        start_time = time.perf_counter()
        
        # New relationships appearing between t0 and t1
        new_rels = self.conn.execute("""
            SELECT relationship_id, relationship_type, object_entity_id, valid_from
            FROM entity_relationships
            WHERE subject_entity_id = ?
              AND valid_from > ?
              AND valid_from <= ?
        """, (entity_id, t0, t1)).fetchall()

        # Expired relationships
        expired_rels = self.conn.execute("""
            SELECT relationship_id, relationship_type, object_entity_id, valid_to
            FROM entity_relationships
            WHERE subject_entity_id = ?
              AND valid_to > ?
              AND valid_to <= ?
        """, (entity_id, t0, t1)).fetchall()

        delta_data = {
            "entity_id": entity_id,
            "t0": t0,
            "t1": t1,
            "new_relationships": [{"id": r[0], "type": r[1], "target": r[2], "from": r[3]} for r in new_rels],
            "expired_relationships": [{"id": r[0], "type": r[1], "target": r[2], "to": r[3]} for r in expired_rels],
            "total_changes": len(new_rels) + len(expired_rels)
        }
        return self._format_result("GET_INFORMATION_DELTA", t1, delta_data, entity_refs=[entity_id], start_time=start_time)

    # 9. Unified Retrieve for Agent Consumption
    def retrieve(
        self,
        entity_query: str,
        as_of: Optional[str] = None,
        path_mode: str = "FAST_PATH",
        pit_mode: str = "MARKET"
    ) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        # 1. Resolve entity_id from query (direct ID, alias, ticker, or canonical name)
        resolved_entity_id = None
        row = self.conn.execute("SELECT entity_id FROM entities WHERE entity_id = ?", (entity_query,)).fetchone()
        if row:
            resolved_entity_id = row[0]
        else:
            row = self.conn.execute("SELECT entity_id FROM entity_aliases WHERE UPPER(alias) = ?", (entity_query.upper(),)).fetchone()
            if row:
                resolved_entity_id = row[0]
            else:
                row = self.conn.execute("SELECT entity_id FROM entity_identifiers WHERE UPPER(identifier_value) = ?", (entity_query.upper(),)).fetchone()
                if row:
                    resolved_entity_id = row[0]
                else:
                    row = self.conn.execute("SELECT entity_id FROM entities WHERE UPPER(canonical_name) LIKE ?", (f"%{entity_query.upper()}%",)).fetchone()
                    if row:
                        resolved_entity_id = row[0]

        data = {
            "entity": None,
            "relationships": [],
            "information_items": [],
            "exposures": [],
            "contradictions": []
        }
        source_refs: Set[str] = set()
        evidence_refs: Set[str] = set()
        entity_refs: Set[str] = set()
        relationship_refs: Set[str] = set()

        if resolved_entity_id:
            entity_refs.add(resolved_entity_id)
            # Entity Details
            ent_res = self.get_entity(resolved_entity_id, as_of=as_of_ts)
            data["entity"] = ent_res.data
            
            # Relationships
            mode_enum = RetrievalPathMode.DEEP_PATH if path_mode == "DEEP_PATH" else RetrievalPathMode.FAST_PATH
            rel_res = self.get_entity_relationships(
                resolved_entity_id,
                as_of=as_of_ts,
                max_hops=2 if mode_enum == RetrievalPathMode.DEEP_PATH else 1,
                mode=mode_enum
            )
            data["relationships"] = rel_res.data
            relationship_refs.update(rel_res.relationship_refs)
            entity_refs.update(rel_res.entity_refs)
            evidence_refs.update(rel_res.evidence_refs)

            # Exposures
            exp_res = self.get_exposures(resolved_entity_id, as_of=as_of_ts)
            data["exposures"] = exp_res.data

            # Contradictions
            contra_res = self.get_contradictions(resolved_entity_id)
            data["contradictions"] = contra_res.data
            evidence_refs.update(contra_res.evidence_refs)

        # Search information items (PIT-compliant: available_at <= as_of_ts and access_class = 'PUBLIC')
        info_res = self.search_information(query=entity_query, entity_id=resolved_entity_id, as_of=as_of_ts, pit_mode=pit_mode)
        data["information_items"] = info_res.data
        for item in info_res.data:
            if "information_id" in item:
                ev_rows = self.conn.execute("""
                    SELECT evidence_id, source_id FROM evidence WHERE information_id = ?
                """, (item["information_id"],)).fetchall()
                for ev_r in ev_rows:
                    evidence_refs.add(ev_r[0])
                    source_refs.add(ev_r[1])

        # Find sources for any evidence collected
        if evidence_refs:
            placeholders = ",".join(["?"] * len(evidence_refs))
            src_rows = self.conn.execute(f"""
                SELECT DISTINCT source_id FROM evidence WHERE evidence_id IN ({placeholders})
            """, list(evidence_refs)).fetchall()
            for sr in src_rows:
                source_refs.add(sr[0])

        mode_enum = RetrievalPathMode.DEEP_PATH if path_mode == "DEEP_PATH" else RetrievalPathMode.FAST_PATH
        return self._format_result(
            query_id=f"RETRIEVE_{entity_query}_{as_of_ts[:10]}",
            as_of=as_of_ts,
            data=data,
            source_refs=list(source_refs),
            evidence_refs=list(evidence_refs),
            entity_refs=list(entity_refs),
            relationship_refs=list(relationship_refs),
            path_mode=mode_enum,
            start_time=t0
        )

    # 10. Agent 1 <-> Agent 2 Reverse Investigation Lookup
    def investigate(
        self,
        symbol: str,
        trigger_type: InvestigationTriggerType = InvestigationTriggerType.UNUSUAL_VOLUME,
        as_of: Optional[str] = None,
        lookback_hours: int = 48,
        trigger_context: Optional[Dict[str, Any]] = None
    ) -> InvestigationReport:
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        try:
            dt_as_of = datetime.fromisoformat(as_of_ts.replace("Z", "+00:00"))
            import datetime as dt_mod
            dt_start = dt_as_of - dt_mod.timedelta(hours=lookback_hours)
            start_ts = dt_start.isoformat()
        except Exception:
            start_ts = "1970-01-01T00:00:00Z"

        # Resolve entity
        ent_res = self.conn.execute("""
            SELECT e.entity_id, e.canonical_name
            FROM entity_identifiers i
            JOIN entities e ON i.entity_id = e.entity_id
            WHERE UPPER(i.identifier_value) = ?
        """, (symbol.upper(),)).fetchone()
        
        if not ent_res:
            ent_res = self.conn.execute("SELECT entity_id, canonical_name FROM entities WHERE UPPER(canonical_name) LIKE ?", (f"%{symbol.upper()}%",)).fetchone()
            
        entity_id = ent_res[0] if ent_res else f"ENT_{symbol.upper()}"

        # 1. Search recent information items in [start_ts, as_of_ts]
        info_rows = self.conn.execute("""
            SELECT information_id, document_id, information_type, title, summary, published_at, available_at
            FROM information_items
            WHERE available_at <= ? AND available_at >= ?
              AND (UPPER(title) LIKE ? OR UPPER(summary) LIKE ?)
              AND access_class = 'PUBLIC'
        """, (as_of_ts, start_ts, f"%{symbol.upper()}%", f"%{symbol.upper()}%")).fetchall()

        recent_info = [
            {"information_id": r[0], "document_id": r[1], "type": r[2], "title": r[3], "summary": r[4], "published_at": r[5], "available_at": r[6]}
            for r in info_rows
        ]

        # 2. Search information deltas
        delta_rows = self.conn.execute("""
            SELECT delta_id, entity_id, information_id, cluster_id, attribute_name,
                   previous_state, new_state, novelty_class, change_time, available_at, supporting_evidence_id
            FROM information_deltas
            WHERE entity_id = ? AND available_at <= ? AND available_at >= ?
        """, (entity_id, as_of_ts, start_ts)).fetchall()

        deltas = [
            InformationDeltaRecord(
                delta_id=r[0], entity_id=r[1], information_id=r[2], cluster_id=r[3],
                attribute_name=r[4], previous_state=r[5], new_state=r[6],
                novelty_class=NoveltyClass(r[7]) if r[7] in [e.value for e in NoveltyClass] else NoveltyClass.STATUS_UPDATE,
                change_time=r[8], available_at=r[9], supporting_evidence_id=r[10]
            )
            for r in delta_rows
        ]

        # 3. Active mechanisms and exposures
        exp_res = self.get_exposures(entity_id, as_of=as_of_ts)
        active_mechs = []
        for exp in exp_res.data:
            mech_res = self.get_mechanisms(exp["exposure_id"])
            active_mechs.extend(mech_res.data)

        # 4. Contradictions
        contra_res = self.get_contradictions(entity_id)

        has_catalyst = len(recent_info) > 0 or len(deltas) > 0 or len(active_mechs) > 0
        novelty_str = "NEW_CATALYST" if len(deltas) == 0 and len(recent_info) > 0 else ("STATUS_UPDATE" if len(deltas) > 0 else "NONE")

        trig_name = trigger_type.value if hasattr(trigger_type, 'value') else str(trigger_type)
        why_now = f"Detected {trig_name}. "
        if recent_info:
            why_now += f"Correlated with recent catalyst: '{recent_info[0]['title']}'."
        elif active_mechs:
            why_now += f"Backed by active transmission mechanism ({active_mechs[0]['mechanism_type']})."
        else:
            why_now += "No material public catalyst found in lookback window (UNEXPLAINED_FLOW)."

        return InvestigationReport(
            request_id=f"INV_{symbol}_{as_of_ts[:10]}_{trig_name}",
            symbol=symbol,
            entity_id=entity_id,
            has_matching_catalyst=has_catalyst,
            novelty_summary=novelty_str,
            information_deltas=deltas,
            recent_information=recent_info,
            active_mechanisms=active_mechs,
            contradictions_found=contra_res.data,
            why_now_assessment=why_now,
            investigation_status="COMPLETED",
            as_of=as_of_ts
        )

    # 11. Dynamic Thesis Delta for Active Position Exit Intelligence (Gate 6)
    def get_thesis_delta(
        self,
        symbol: str,
        position_id: str,
        entry_timestamp: str,
        as_of: Optional[str] = None
    ) -> ThesisDelta:
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        # Resolve entity
        ent_res = self.conn.execute("""
            SELECT e.entity_id FROM entity_identifiers i
            JOIN entities e ON i.entity_id = e.entity_id
            WHERE UPPER(i.identifier_value) = ?
        """, (symbol.upper(),)).fetchone()
        entity_id = ent_res[0] if ent_res else f"ENT_{symbol.upper()}"

        # 1. Check for new negative information / corporate events after entry
        new_info = self.conn.execute("""
            SELECT information_id, title, summary, available_at
            FROM information_items
            WHERE available_at > ? AND available_at <= ?
              AND (UPPER(title) LIKE ? OR UPPER(summary) LIKE ?)
              AND access_class = 'PUBLIC'
        """, (entry_timestamp, as_of_ts, f"%{symbol.upper()}%", f"%{symbol.upper()}%")).fetchall()

        # 2. Check for new contradictions created after entry
        new_contras = self.conn.execute("""
            SELECT contradiction_id, contradiction_type, severity, resolution_status
            FROM contradictions
            WHERE subject_id = ? AND created_at > ?
        """, (entity_id, entry_timestamp)).fetchall()

        # 3. Check for new information deltas
        deltas = self.conn.execute("""
            SELECT delta_id, attribute_name, previous_state, new_state, novelty_class
            FROM information_deltas
            WHERE entity_id = ? AND available_at > ? AND available_at <= ?
        """, (entity_id, entry_timestamp, as_of_ts)).fetchall()

        new_ev_ids = [r[0] for r in new_info]
        contra_dicts = [{"id": c[0], "type": c[1], "severity": c[2]} for c in new_contras]

        has_high_contra = any(c[2] in ["HIGH", "CRITICAL"] for c in new_contras)
        has_negative_text = any(any(k in r[1].lower() or k in r[2].lower() for k in ["batal", "rugi", "tuntutan", "suspensi", "penurunan", "cancelled", "lawsuit", "investigation"]) for r in new_info)

        if has_high_contra or has_negative_text:
            thesis_state = ThesisState.INVALIDATED
            action = "EXIT"
            reason = f"Thesis invalidated by material negative catalyst / high contradiction since entry ({entry_timestamp})."
        elif len(new_contras) > 0 or any(d[4] == "REVISION" for d in deltas):
            thesis_state = ThesisState.WEAKENING
            action = "WAIT"
            reason = f"Thesis weakening due to newly detected contradiction or revision since entry."
        elif len(new_info) > 0 or len(deltas) > 0:
            thesis_state = ThesisState.SUPPORTING
            action = "HOLD"
            reason = f"New supporting information/catalysts emerged since entry ({len(new_info)} items)."
        else:
            thesis_state = ThesisState.NEUTRAL
            action = "HOLD"
            reason = "No material thesis changes detected since entry."

        return ThesisDelta(
            delta_id=f"THESIS_DELTA_{symbol}_{position_id}_{as_of_ts[:10]}",
            symbol=symbol,
            position_id=position_id,
            as_of_timestamp=as_of_ts,
            thesis_state=thesis_state,
            reason=reason,
            new_evidence_ids=new_ev_ids,
            contradictions=contra_dicts,
            recommended_action=action
        )

    # 12. Multi-Hop Propagated Exposures (Gate 3)
    def get_propagated_exposures(self, entity_id: str, as_of: Optional[str] = None) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        rows = self.conn.execute("""
            SELECT propagation_id, origin_entity_id, policy_or_event_id, target_entity_id,
                   economic_channel, exposure_type, transmission_path_json, direction,
                   magnitude_class, valid_from, valid_to
            FROM propagated_exposures
            WHERE target_entity_id = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """, (entity_id, as_of_ts, as_of_ts)).fetchall()

        results = []
        for r in rows:
            hops_raw = json.loads(r[6]) if r[6] else []
            hops = [TransmissionHop(**h) for h in hops_raw]
            results.append(PropagatedExposureResult(
                propagation_id=r[0],
                origin_entity_id=r[1],
                policy_or_event_id=r[2],
                target_entity_id=r[3],
                economic_channel=EconomicChannel(r[4]) if r[4] in [e.value for e in EconomicChannel] else EconomicChannel.REGULATORY_COST,
                exposure_type=ExposureType(r[5]) if r[5] in [e.value for e in ExposureType] else ExposureType.DIRECT,
                transmission_path=hops,
                direction=r[7],
                magnitude_class=r[8],
                valid_from=r[9],
                valid_to=r[10]
            ))

        return self._format_result(
            "GET_PROPAGATED_EXPOSURES", as_of_ts, [r.model_dump() for r in results],
            entity_refs=[entity_id], path_mode=RetrievalPathMode.DEEP_PATH, start_time=t0
        )

    def traverse_multi_hop_exposure(
        self,
        origin_entity_id: str,
        target_entity_id: Optional[str] = None,
        as_of: Optional[str] = None,
        max_hops: int = 3,
        allowed_relationship_types: Optional[List[str]] = None,
        allowed_entity_types: Optional[List[str]] = None,
        allowed_economic_channels: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        access_class_filter: Optional[List[str]] = None
    ) -> RetrievalResultContract:
        t0 = time.perf_counter()
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()

        # If we have access to kdp object, use its traverse method
        if hasattr(self.conn, "traverse_multi_hop_exposure"):
            paths = self.conn.traverse_multi_hop_exposure(
                origin_entity_id=origin_entity_id,
                target_entity_id=target_entity_id,
                as_of=as_of_ts,
                max_hops=max_hops,
                allowed_relationship_types=allowed_relationship_types,
                allowed_entity_types=allowed_entity_types,
                allowed_economic_channels=allowed_economic_channels,
                min_confidence=min_confidence,
                access_class_filter=access_class_filter
            )
        else:
            # Native traversal on connection
            from core.knowledge_data_platform import KnowledgeDataPlatform
            kdp = KnowledgeDataPlatform(self.db_path) if isinstance(self.db_path, str) else None
            if kdp:
                paths = kdp.traverse_multi_hop_exposure(
                    origin_entity_id=origin_entity_id,
                    target_entity_id=target_entity_id,
                    as_of=as_of_ts,
                    max_hops=max_hops,
                    allowed_relationship_types=allowed_relationship_types,
                    allowed_entity_types=allowed_entity_types,
                    allowed_economic_channels=allowed_economic_channels,
                    min_confidence=min_confidence,
                    access_class_filter=access_class_filter
                )
            else:
                paths = []

        refs = [origin_entity_id]
        if target_entity_id:
            refs.append(target_entity_id)

        return self._format_result(
            "TRAVERSE_MULTI_HOP_EXPOSURE", as_of_ts, [p.model_dump() for p in paths],
            entity_refs=refs, path_mode=RetrievalPathMode.DEEP_PATH, start_time=t0
        )

    def explain_exposure(
        self,
        origin_entity_id: str,
        target_entity_id: str,
        as_of: Optional[str] = None
    ) -> Optional[ExposurePath]:
        res = self.traverse_multi_hop_exposure(
            origin_entity_id=origin_entity_id,
            target_entity_id=target_entity_id,
            as_of=as_of,
            max_hops=5
        )
        if res.data:
            return ExposurePath(**res.data[0])
        return None



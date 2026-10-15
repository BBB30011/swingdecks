import duckdb
import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import asdict
from core.intelligence_models import (
    Entity, EntityRelationship, InformationEvent, Exposure, 
    MechanismHypothesis, InformationMarketLink, ContradictionRecord
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, AccessClass, EvidenceClassification,
    validate_entity_semantic_type, validate_relationship_semantics,
    validate_policy_transmission_chain
)

logger = logging.getLogger("IntelligenceGraph")

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"disregard\s+(?:all\s+)?previous",
    r"system\s+override",
    r"prompt\s+injection",
    r"you\s+are\s+now\s+a",
    r"bypass\s+rules",
    r"jailbreak",
    r"buy\s+[a-z]{4}\s+immediately",
    r"agent3\s+must\s+approve",
    r"delete\s+contradiction",
    r"mark\s+source\s+as\s+official"
]

class IntelligenceGraphEngine:
    def __init__(self, db_path: str = "state/intelligence_graph.duckdb"):
        self.db_path = db_path
        self.conn = duckdb.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id VARCHAR PRIMARY KEY, canonical_name VARCHAR, entity_type VARCHAR,
                jurisdiction VARCHAR, aliases VARCHAR, former_names VARCHAR, ticker VARCHAR,
                status VARCHAR, source_refs VARCHAR, first_seen VARCHAR, last_seen VARCHAR,
                semantic_status VARCHAR, evidence_classification VARCHAR
            );
            CREATE TABLE IF NOT EXISTS relationships (
                relationship_id VARCHAR PRIMARY KEY, source_entity VARCHAR, target_entity VARCHAR,
                relationship_type VARCHAR, valid_from VARCHAR, valid_to VARCHAR, observed_at VARCHAR,
                source_refs VARCHAR, evidence_refs VARCHAR, confidence VARCHAR, status VARCHAR,
                pit_status VARCHAR, evidence VARCHAR, semantic_status VARCHAR, temporal_status VARCHAR,
                access_class VARCHAR, evidence_classification VARCHAR
            );
            CREATE TABLE IF NOT EXISTS information (
                information_id VARCHAR PRIMARY KEY, source_id VARCHAR, source_type VARCHAR,
                source_url_or_reference VARCHAR, publisher VARCHAR, published_at VARCHAR,
                available_at VARCHAR, captured_at VARCHAR, title VARCHAR, summary VARCHAR,
                claim VARCHAR, information_type VARCHAR, topic VARCHAR, subtopic VARCHAR,
                entities VARCHAR, sectors VARCHAR, geographies VARCHAR, source_quality VARCHAR,
                evidence_quality VARCHAR, confidence VARCHAR, access_class VARCHAR,
                trading_eligibility VARCHAR, pit_status VARCHAR, status VARCHAR, semantic_status VARCHAR,
                evidence_classification VARCHAR, event_cluster_id VARCHAR, effective_at VARCHAR,
                supersedes VARCHAR, superseded_by VARCHAR, evidence_refs VARCHAR
            );
            CREATE TABLE IF NOT EXISTS exposures (
                exposure_id VARCHAR PRIMARY KEY, entity_id VARCHAR, target_entity_id VARCHAR,
                exposure_type VARCHAR, directness VARCHAR, mechanism_category VARCHAR,
                economic_channel VARCHAR, valid_from VARCHAR, valid_to VARCHAR, evidence_refs VARCHAR,
                confidence VARCHAR, pit_status VARCHAR, status VARCHAR, semantic_status VARCHAR,
                evidence_classification VARCHAR
            );
            CREATE TABLE IF NOT EXISTS mechanisms (
                mechanism_id VARCHAR PRIMARY KEY, information_id VARCHAR, entity_id VARCHAR,
                exposure_id VARCHAR, mechanism_type VARCHAR, economic_channel VARCHAR,
                expected_effect VARCHAR, expected_direction VARCHAR, time_horizon VARCHAR,
                supporting_evidence VARCHAR, contradicting_evidence VARCHAR, invalidation_condition VARCHAR,
                confidence VARCHAR, pit_status VARCHAR, status VARCHAR, semantic_status VARCHAR,
                evidence_classification VARCHAR
            );
            CREATE TABLE IF NOT EXISTS market_links (
                information_id VARCHAR, market_symbol VARCHAR, information_available_at VARCHAR,
                reaction_window VARCHAR, observed_return FLOAT, observed_volume_change FLOAT,
                observed_volatility_change FLOAT, sector_context VARCHAR, benchmark_context VARCHAR,
                pit_status VARCHAR, evidence_classification VARCHAR, non_causality_disclaimer VARCHAR,
                PRIMARY KEY(information_id, market_symbol)
            );
            CREATE TABLE IF NOT EXISTS contradictions (
                contradiction_id VARCHAR PRIMARY KEY, contradiction_type VARCHAR,
                source_a_id VARCHAR, source_b_id VARCHAR, claim_a VARCHAR, claim_b VARCHAR,
                entity_id VARCHAR, severity VARCHAR, detected_at VARCHAR, resolution_status VARCHAR,
                evidence_classification VARCHAR
            );
        """)

    def insert_entity(self, entity: Entity):
        d = asdict(entity)
        is_valid, reason, canonical_type = validate_entity_semantic_type(d['entity_id'], d['entity_type'])
        if not is_valid:
            d['semantic_status'] = "SEMANTIC_VIOLATION"
            d['status'] = "UNVERIFIED"
        else:
            if not d.get('semantic_status'):
                d['semantic_status'] = "VALIDATED"

        self.conn.execute("""
            INSERT INTO entities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (entity_id) DO UPDATE SET 
                canonical_name = excluded.canonical_name, aliases = excluded.aliases,
                former_names = excluded.former_names, ticker = excluded.ticker,
                status = excluded.status, last_seen = excluded.last_seen,
                semantic_status = excluded.semantic_status,
                evidence_classification = excluded.evidence_classification
        """, (
            d['entity_id'], d['canonical_name'], d['entity_type'], d.get('jurisdiction', 'ID'), 
            json.dumps(d['aliases']), json.dumps(d['former_names']), d['ticker'],
            d['status'], json.dumps(d['source_refs']), d['first_seen'], d['last_seen'],
            d.get('semantic_status', 'VALIDATED'), d.get('evidence_classification', 'CONTROLLED')
        ))

    def insert_relationship(self, rel: EntityRelationship):
        d = asdict(rel)
        if d['status'] == "UNSUPPORTED":
            return

        # Check temporal order
        if d.get('valid_to') and d['valid_to'] < d['valid_from']:
            d['status'] = "UNSUPPORTED"
            d['temporal_status'] = "TEMPORAL_INVERSION"
            d['semantic_status'] = "INVALID_TEMPORAL"
            return
        elif not d.get('valid_to'):
            d['temporal_status'] = "OPEN_ENDED_UNVERIFIED"
        else:
            d['temporal_status'] = "BOUNDED"

        # Lookup source & target entity types if present in DB
        src_row = self.conn.execute("SELECT entity_type FROM entities WHERE entity_id = ?", (d['source_entity'],)).fetchone()
        tgt_row = self.conn.execute("SELECT entity_type FROM entities WHERE entity_id = ?", (d['target_entity'],)).fetchone()

        if src_row and tgt_row:
            src_type = src_row[0]
            tgt_type = tgt_row[0]
            is_valid, reason = validate_relationship_semantics(src_type, d['relationship_type'], tgt_type)
            if not is_valid:
                d['semantic_status'] = "SEMANTIC_VIOLATION"
                d['status'] = "UNSUPPORTED"
                return

        if not d.get('semantic_status'):
            d['semantic_status'] = "VALIDATED"

        self.conn.execute("""
            INSERT INTO relationships VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (relationship_id) DO UPDATE SET
                valid_to = excluded.valid_to, status = excluded.status,
                evidence = excluded.evidence, confidence = excluded.confidence,
                semantic_status = excluded.semantic_status,
                temporal_status = excluded.temporal_status
        """, (
            d['relationship_id'], d['source_entity'], d['target_entity'], d['relationship_type'],
            d['valid_from'], d['valid_to'], d['observed_at'], json.dumps(d['source_refs']),
            json.dumps(d['evidence_refs']), d['confidence'], d['status'], d['pit_status'], d['evidence'],
            d.get('semantic_status', 'VALIDATED'), d.get('temporal_status', 'BOUNDED'),
            d.get('access_class', 'PUBLIC'), d.get('evidence_classification', 'CONTROLLED')
        ))

    def insert_information(self, info: InformationEvent):
        d = asdict(info)
        text_corpus = f"{d.get('title', '')} {d.get('summary', '')} {d.get('claim', '')}".lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_corpus):
                d['status'] = "UNTRUSTED_CONTENT"
                d['semantic_status'] = "PROMPT_INJECTION_DETECTED"
                d['trading_eligibility'] = "BLOCKED"
                break

        # Check access class & private info firewall
        if d.get('access_class') not in ["PUBLIC", "AUTHORIZED_PRIVATE", None, ""]:
            d['status'] = "RESTRICTED_MNPI"
            d['semantic_status'] = "MNPI_DETECTED"
            d['trading_eligibility'] = "BLOCKED"
        elif d.get('access_class') == "AUTHORIZED_PRIVATE":
            # Authorized private is storage-authorized but decision-ineligible by default
            d['trading_eligibility'] = "RESTRICTED"

        if not d.get('semantic_status'):
            d['semantic_status'] = "VALIDATED"

        self.conn.execute("""
            INSERT INTO information VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (information_id) DO UPDATE SET 
                status = excluded.status, superseded_by = excluded.superseded_by, 
                trading_eligibility = excluded.trading_eligibility,
                semantic_status = excluded.semantic_status
        """, (
            d['information_id'], d['source_id'], d['source_type'], d['source_url_or_reference'],
            d['publisher'], d['published_at'], d['available_at'], d['captured_at'],
            d['title'], d['summary'], d['claim'], d['information_type'], d['topic'], d['subtopic'],
            json.dumps(d['entities']), json.dumps(d['sectors']), json.dumps(d['geographies']),
            d['source_quality'], d['evidence_quality'], d['confidence'], d['access_class'],
            d['trading_eligibility'], d['pit_status'], d['status'], d.get('semantic_status', 'VALIDATED'),
            d.get('evidence_classification', 'CONTROLLED'), d['event_cluster_id'],
            d['effective_at'], d['supersedes'], d['superseded_by'], json.dumps(d['evidence_refs'])
        ))

    def insert_exposure(self, exp: Exposure):
        d = asdict(exp)
        if d.get('status') == "UNSUPPORTED":
            return
        if not d.get('semantic_status'):
            d['semantic_status'] = "VALIDATED"
            
        self.conn.execute("""
            INSERT INTO exposures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (exposure_id) DO UPDATE SET valid_to = excluded.valid_to, status = excluded.status
        """, (
            d['exposure_id'], d['entity_id'], d['target_entity_id'], d['exposure_type'],
            d['directness'], d['mechanism_category'], d.get('economic_channel', 'UNKNOWN'),
            d['valid_from'], d['valid_to'], json.dumps(d['evidence_refs']), d['confidence'], 
            d['pit_status'], d['status'], d.get('semantic_status', 'VALIDATED'),
            d.get('evidence_classification', 'CONTROLLED')
        ))

    def insert_mechanism(self, mech: MechanismHypothesis):
        d = asdict(mech)
        if d.get('status') == "UNSUPPORTED":
            return
        if not d.get('semantic_status'):
            d['semantic_status'] = "VALIDATED"
            
        self.conn.execute("""
            INSERT INTO mechanisms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (mechanism_id) DO UPDATE SET
                contradicting_evidence = excluded.contradicting_evidence, invalidation_condition = excluded.invalidation_condition
        """, (
            d['mechanism_id'], d['information_id'], d['entity_id'], d['exposure_id'],
            d['mechanism_type'], d['economic_channel'], d['expected_effect'], d['expected_direction'],
            d['time_horizon'], json.dumps(d['supporting_evidence']), json.dumps(d['contradicting_evidence']),
            d['invalidation_condition'], d['confidence'], d['pit_status'], d['status'],
            d.get('semantic_status', 'VALIDATED'), d.get('evidence_classification', 'CONTROLLED')
        ))

    def insert_market_link(self, link: InformationMarketLink):
        d = asdict(link)
        self.conn.execute("""
            INSERT INTO market_links VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (information_id, market_symbol) DO UPDATE SET observed_return = excluded.observed_return
        """, (
            d['information_id'], d['market_symbol'], d['information_available_at'], d['reaction_window'],
            d['observed_return'], d['observed_volume_change'], d['observed_volatility_change'],
            d['sector_context'], d['benchmark_context'], d['pit_status'],
            d.get('evidence_classification', 'CONTROLLED'),
            d.get('non_causality_disclaimer', 'PRE_DECISION_EVIDENCE != POST_DECISION_OUTCOME. Observational correlation does not prove causation.')
        ))

    def insert_contradiction(self, con: ContradictionRecord):
        d = asdict(con)
        self.conn.execute("""
            INSERT INTO contradictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (contradiction_id) DO UPDATE SET resolution_status = excluded.resolution_status
        """, (
            d['contradiction_id'], d['contradiction_type'], d['source_a_id'], d['source_b_id'],
            d['claim_a'], d['claim_b'], d['entity_id'], d['severity'], d['detected_at'],
            d['resolution_status'], d.get('evidence_classification', 'CONTROLLED')
        ))

    def resolve_entity(self, identifier: str) -> Optional[Dict]:
        res = self.conn.execute("SELECT * FROM entities").fetchall()
        for r in res:
            if r[1] and r[1].lower() == identifier.lower():
                return {"entity_id": r[0], "canonical_name": r[1], "entity_type": r[2], "match_type": "MATCH_EXACT"}
            if r[6] and r[6].lower() == identifier.lower():
                return {"entity_id": r[0], "canonical_name": r[1], "entity_type": r[2], "match_type": "MATCH_TICKER"}
            aliases = json.loads(r[4]) if r[4] else []
            if identifier.lower() in [a.lower() for a in aliases]:
                return {"entity_id": r[0], "canonical_name": r[1], "entity_type": r[2], "match_type": "MATCH_ALIAS"}
            former = json.loads(r[5]) if r[5] else []
            if identifier.lower() in [f.lower() for f in former]:
                return {"entity_id": r[0], "canonical_name": r[1], "entity_type": r[2], "match_type": "MATCH_FORMER_NAME"}
            if r[0].lower() == identifier.lower():
                return {"entity_id": r[0], "canonical_name": r[1], "entity_type": r[2], "match_type": "MATCH_ID"}
        return None

    def get_related_entities(self, entity_id: str, point_in_time: str) -> List[Dict]:
        query = """
            SELECT relationship_type, target_entity as entity FROM relationships 
            WHERE source_entity = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)
              AND status = 'SUPPORTED' AND (semantic_status IS NULL OR semantic_status != 'SEMANTIC_VIOLATION')
            UNION
            SELECT relationship_type, source_entity as entity FROM relationships 
            WHERE target_entity = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)
              AND status = 'SUPPORTED' AND (semantic_status IS NULL OR semantic_status != 'SEMANTIC_VIOLATION')
        """
        return [{"relationship": r[0], "entity": r[1]} for r in self.conn.execute(query, (entity_id, point_in_time, point_in_time, entity_id, point_in_time, point_in_time)).fetchall()]

    def find_shortest_evidence_path(self, source_entity_id: str, target_entity_id: str, pit: str) -> List[str]:
        visited = set([source_entity_id])
        queue = [[source_entity_id]]
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == target_entity_id:
                return path
            rels = self.get_related_entities(node, pit)
            for r in rels:
                if r['entity'] not in visited:
                    visited.add(r['entity'])
                    queue.append(path + [r['entity']])
        return []

    def get_information_events(self, entity_id: str, point_in_time: str) -> List[Dict[str, Any]]:
        query = """
            SELECT information_id, source_id, source_type, source_url_or_reference, publisher,
                   published_at, available_at, title, summary, claim, information_type,
                   topic, subtopic, source_quality, evidence_quality, confidence,
                   access_class, trading_eligibility, status, evidence_refs, semantic_status
            FROM information
            WHERE available_at <= ?
              AND status NOT IN ('UNTRUSTED_CONTENT', 'RESTRICTED_MNPI')
              AND trading_eligibility = 'ELIGIBLE'
            ORDER BY available_at DESC
        """
        rows = self.conn.execute(query, (point_in_time,)).fetchall()
        matching = []
        for r in rows:
            ent_query = "SELECT entities FROM information WHERE information_id = ?"
            ent_raw = self.conn.execute(ent_query, (r[0],)).fetchone()[0]
            entities = json.loads(ent_raw) if ent_raw else []
            if not entities or entity_id in entities:
                matching.append({
                    "information_id": r[0],
                    "source_id": r[1],
                    "source_type": r[2],
                    "source_url_or_reference": r[3],
                    "publisher": r[4],
                    "published_at": r[5],
                    "available_at": r[6],
                    "title": r[7],
                    "summary": r[8],
                    "claim": r[9],
                    "information_type": r[10],
                    "topic": r[11],
                    "subtopic": r[12],
                    "source_quality": r[13],
                    "evidence_quality": r[14],
                    "confidence": r[15],
                    "access_class": r[16],
                    "trading_eligibility": r[17],
                    "status": r[18],
                    "evidence_refs": json.loads(r[19]) if r[19] else [],
                    "semantic_status": r[20]
                })
        return matching

    def get_exposures(self, entity_id: str, point_in_time: str) -> List[Dict[str, Any]]:
        query = """
            SELECT exposure_id, entity_id, target_entity_id, exposure_type, directness,
                   mechanism_category, economic_channel, valid_from, valid_to, evidence_refs, confidence, status
            FROM exposures
            WHERE (entity_id = ? OR target_entity_id = ?)
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
              AND status = 'SUPPORTED'
        """
        rows = self.conn.execute(query, (entity_id, entity_id, point_in_time, point_in_time)).fetchall()
        return [
            {
                "exposure_id": r[0],
                "entity_id": r[1],
                "target_entity_id": r[2],
                "exposure_type": r[3],
                "directness": r[4],
                "mechanism_category": r[5],
                "economic_channel": r[6],
                "valid_from": r[7],
                "valid_to": r[8],
                "evidence_refs": json.loads(r[9]) if r[9] else [],
                "confidence": r[10],
                "status": r[11]
            }
            for r in rows
        ]

    def get_mechanisms(self, entity_id: str, point_in_time: str) -> List[Dict[str, Any]]:
        query = """
            SELECT mechanism_id, information_id, entity_id, exposure_id, mechanism_type,
                   economic_channel, expected_effect, expected_direction, time_horizon,
                   supporting_evidence, contradicting_evidence, invalidation_condition,
                   confidence, status
            FROM mechanisms
            WHERE entity_id = ?
              AND status = 'SUPPORTED'
        """
        rows = self.conn.execute(query, (entity_id,)).fetchall()
        return [
            {
                "mechanism_id": r[0],
                "information_id": r[1],
                "entity_id": r[2],
                "exposure_id": r[3],
                "mechanism_type": r[4],
                "economic_channel": r[5],
                "expected_effect": r[6],
                "expected_direction": r[7],
                "time_horizon": r[8],
                "supporting_evidence": json.loads(r[9]) if r[9] else [],
                "contradicting_evidence": json.loads(r[10]) if r[10] else [],
                "invalidation_condition": r[11],
                "confidence": r[12],
                "status": r[13]
            }
            for r in rows
        ]

    def get_market_links(self, information_id: str) -> List[Dict[str, Any]]:
        query = """
            SELECT information_id, market_symbol, information_available_at, reaction_window,
                   observed_return, observed_volume_change, observed_volatility_change,
                   sector_context, benchmark_context, pit_status
            FROM market_links
            WHERE information_id = ?
        """
        rows = self.conn.execute(query, (information_id,)).fetchall()
        return [
            {
                "information_id": r[0],
                "market_symbol": r[1],
                "information_available_at": r[2],
                "reaction_window": r[3],
                "observed_return": r[4],
                "observed_volume_change": r[5],
                "observed_volatility_change": r[6],
                "sector_context": r[7],
                "benchmark_context": r[8],
                "pit_status": r[9]
            }
            for r in rows
        ]

    def get_entity_subgraph(self, identifier: str, point_in_time: str) -> Dict[str, Any]:
        resolved = self.resolve_entity(identifier)
        if not resolved:
            return {
                "status": "ENTITY_NOT_FOUND",
                "entity": None,
                "relationships": [],
                "information": [],
                "exposures": [],
                "mechanisms": [],
                "market_links": []
            }
        
        ent_id = resolved["entity_id"]
        rels = self.get_related_entities(ent_id, point_in_time)
        info_events = self.get_information_events(ent_id, point_in_time)
        exps = self.get_exposures(ent_id, point_in_time)
        mechs = self.get_mechanisms(ent_id, point_in_time)
        
        links = []
        for info in info_events:
            links.extend(self.get_market_links(info["information_id"]))
            
        return {
            "status": "VALID",
            "entity": resolved,
            "relationships": rels,
            "information": info_events,
            "exposures": exps,
            "mechanisms": mechs,
            "market_links": links
        }

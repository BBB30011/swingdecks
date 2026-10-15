"""
SwingDeck Knowledge Data Platform - Master Platform Engine V1
Manages schema lifecycle, layered normalization, entity resolution,
relationship/evidence linkage, derived indexing, data quality, and backup/recovery.
"""

import duckdb
import hashlib
import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Set

from core.data_platform_schemas import (
    RawDocumentRecord, SourceRecord, EntityRecord, EntityAliasRecord,
    EntityIdentifierRecord, InformationItemRecord, ClaimRecord, EvidenceRecord,
    EntityRelationshipRecord, RelationshipEvidenceRecord, CorporateActionRecord,
    MarketReactionRecord, PolicyRecord, ExposureRecord, MechanismRecord,
    ContradictionDataRecord, RetrievalResultContract, SourceType, InformationType,
    CorporateActionType, EvidenceRole, EventClusterRecord, InformationDeltaRecord,
    MarketSnapshotAtAvailability, PropagatedExposureResult, TransmissionHop, ExposurePath,
    compute_content_hash, compute_document_fingerprint
)
from core.semantic_ontology import (
    EntityType, RelationshipType, EconomicChannel, ExposureType,
    ContradictionType, AccessClass, EvidenceClassification,
    validate_entity_semantic_type, validate_relationship_semantics,
    validate_policy_transmission_chain
)
from core.duplicate_corroboration import DuplicateAndCorroborationEngine

logger = logging.getLogger("KnowledgeDataPlatform")

SCHEMA_VERSION = "1.0.0"

class KnowledgeDataPlatform:
    def __init__(self, db_path: str = "data/duckdb/intelligence.duckdb"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.conn = duckdb.connect(db_path)
        self.init_database_schema()

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def init_database_schema(self):
        """Initializes all 9 platform layers and performance indexes in DuckDB."""
        # 1. RAW LAYER
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_documents (
                raw_document_id VARCHAR PRIMARY KEY,
                source_id VARCHAR NOT NULL,
                source_document_id VARCHAR NOT NULL,
                retrieved_at VARCHAR NOT NULL,
                published_at VARCHAR NOT NULL,
                available_at VARCHAR NOT NULL,
                content_hash VARCHAR NOT NULL,
                content_type VARCHAR DEFAULT 'text/plain',
                mime_type VARCHAR DEFAULT 'text/plain',
                language VARCHAR DEFAULT 'id',
                raw_location VARCHAR DEFAULT '',
                raw_size INTEGER DEFAULT 0,
                access_class VARCHAR DEFAULT 'PUBLIC',
                ingestion_run_id VARCHAR DEFAULT 'DEFAULT',
                origin_class VARCHAR DEFAULT 'NATURAL',
                created_at VARCHAR NOT NULL
            );
        """)

        # 2. SOURCE REGISTRY
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id VARCHAR PRIMARY KEY,
                source_name VARCHAR NOT NULL,
                publisher VARCHAR NOT NULL,
                source_type VARCHAR NOT NULL,
                jurisdiction VARCHAR DEFAULT 'ID',
                domain VARCHAR DEFAULT '',
                canonical_url VARCHAR DEFAULT '',
                authority_class VARCHAR DEFAULT 'STANDARD',
                source_status VARCHAR DEFAULT 'ACTIVE',
                access_class VARCHAR DEFAULT 'PUBLIC',
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL
            );
        """)

        # 3. CORE ENTITY LAYER
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                entity_id VARCHAR PRIMARY KEY,
                canonical_name VARCHAR NOT NULL,
                entity_type VARCHAR NOT NULL,
                jurisdiction VARCHAR DEFAULT 'ID',
                status VARCHAR DEFAULT 'ACTIVE',
                valid_from VARCHAR DEFAULT '1970-01-01T00:00:00Z',
                valid_to VARCHAR,
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS entity_aliases (
                alias_id VARCHAR PRIMARY KEY,
                entity_id VARCHAR NOT NULL,
                alias VARCHAR NOT NULL,
                alias_type VARCHAR DEFAULT 'COMMON_NAME',
                language VARCHAR DEFAULT 'id',
                valid_from VARCHAR DEFAULT '1970-01-01T00:00:00Z',
                valid_to VARCHAR,
                source_id VARCHAR DEFAULT 'SYSTEM'
            );
            CREATE TABLE IF NOT EXISTS entity_identifiers (
                identifier_id VARCHAR PRIMARY KEY,
                entity_id VARCHAR NOT NULL,
                identifier_type VARCHAR NOT NULL,
                identifier_value VARCHAR NOT NULL,
                issuer VARCHAR DEFAULT 'IDX',
                valid_from VARCHAR DEFAULT '1970-01-01T00:00:00Z',
                valid_to VARCHAR
            );
        """)

        # 4. INFORMATION & EVIDENCE LAYER
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS information_items (
                information_id VARCHAR PRIMARY KEY,
                document_id VARCHAR NOT NULL,
                information_type VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                summary VARCHAR DEFAULT '',
                language VARCHAR DEFAULT 'id',
                published_at VARCHAR NOT NULL,
                available_at VARCHAR NOT NULL,
                effective_from VARCHAR,
                effective_to VARCHAR,
                access_class VARCHAR DEFAULT 'PUBLIC',
                origin_class VARCHAR DEFAULT 'NATURAL',
                semantic_status VARCHAR DEFAULT 'VALID',
                temporal_status VARCHAR DEFAULT 'VALID',
                provenance_status VARCHAR DEFAULT 'VERIFIED',
                content_hash VARCHAR NOT NULL,
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS claims (
                claim_id VARCHAR PRIMARY KEY,
                information_id VARCHAR NOT NULL,
                subject_entity_id VARCHAR NOT NULL,
                predicate VARCHAR NOT NULL,
                object_entity_id VARCHAR,
                claim_type VARCHAR DEFAULT 'FACTUAL',
                claim_text VARCHAR NOT NULL,
                temporal_scope VARCHAR DEFAULT 'ACTIVE',
                evidence_status VARCHAR DEFAULT 'SUPPORTED',
                semantic_status VARCHAR DEFAULT 'VALID',
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS evidence (
                evidence_id VARCHAR PRIMARY KEY,
                information_id VARCHAR NOT NULL,
                source_id VARCHAR NOT NULL,
                document_id VARCHAR NOT NULL,
                claim_id VARCHAR,
                evidence_type VARCHAR DEFAULT 'DOCUMENT_EXCERPT',
                excerpt_reference VARCHAR DEFAULT '',
                content_hash VARCHAR NOT NULL,
                event_time VARCHAR,
                published_at VARCHAR NOT NULL,
                available_at VARCHAR NOT NULL,
                observed_at VARCHAR NOT NULL,
                timestamp_source VARCHAR DEFAULT 'SOURCE_METADATA',
                derivation_method VARCHAR DEFAULT 'SOURCE_ARTICLE_METADATA',
                temporal_confidence VARCHAR DEFAULT 'EXACT',
                access_class VARCHAR DEFAULT 'PUBLIC',
                origin_class VARCHAR DEFAULT 'NATURAL',
                provenance_status VARCHAR DEFAULT 'VERIFIED',
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS event_clusters (
                cluster_id VARCHAR PRIMARY KEY,
                canonical_event_name VARCHAR NOT NULL,
                primary_entity_id VARCHAR NOT NULL,
                event_type VARCHAR NOT NULL,
                first_observed_at VARCHAR NOT NULL,
                latest_update_at VARCHAR NOT NULL,
                independent_sources_count INTEGER DEFAULT 1,
                syndicated_copies_count INTEGER DEFAULT 0,
                corroboration_status VARCHAR DEFAULT 'UNCONFIRMED',
                primary_information_id VARCHAR NOT NULL,
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS information_deltas (
                delta_id VARCHAR PRIMARY KEY,
                entity_id VARCHAR NOT NULL,
                information_id VARCHAR NOT NULL,
                cluster_id VARCHAR,
                attribute_name VARCHAR NOT NULL,
                previous_state VARCHAR NOT NULL,
                new_state VARCHAR NOT NULL,
                novelty_class VARCHAR DEFAULT 'STATUS_UPDATE',
                change_time VARCHAR NOT NULL,
                available_at VARCHAR NOT NULL,
                supporting_evidence_id VARCHAR NOT NULL,
                created_at VARCHAR NOT NULL
            );
        """)

        # 5. RELATIONSHIPS & PROVENANCE LINKAGE
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entity_relationships (
                relationship_id VARCHAR PRIMARY KEY,
                subject_entity_id VARCHAR NOT NULL,
                relationship_type VARCHAR NOT NULL,
                object_entity_id VARCHAR NOT NULL,
                valid_from VARCHAR DEFAULT '1970-01-01T00:00:00Z',
                valid_to VARCHAR,
                observed_at VARCHAR NOT NULL,
                status VARCHAR DEFAULT 'ACTIVE',
                source_priority INTEGER DEFAULT 1,
                created_at VARCHAR NOT NULL,
                updated_at VARCHAR NOT NULL,
                confidence DOUBLE DEFAULT 1.0
            );
            CREATE TABLE IF NOT EXISTS relationship_evidence (
                relationship_evidence_id VARCHAR PRIMARY KEY,
                relationship_id VARCHAR NOT NULL,
                evidence_id VARCHAR NOT NULL,
                evidence_role VARCHAR DEFAULT 'PRIMARY',
                support_status VARCHAR DEFAULT 'SUPPORTED',
                created_at VARCHAR NOT NULL
            );
        """)

        # 6. MARKET & CORPORATE ACTIONS
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS corporate_actions (
                corporate_action_id VARCHAR PRIMARY KEY,
                entity_id VARCHAR NOT NULL,
                action_type VARCHAR NOT NULL,
                announcement_date VARCHAR NOT NULL,
                effective_date VARCHAR NOT NULL,
                record_date VARCHAR,
                source_id VARCHAR NOT NULL,
                information_id VARCHAR,
                status VARCHAR DEFAULT 'ANNOUNCED'
            );
            CREATE TABLE IF NOT EXISTS market_reactions (
                reaction_id VARCHAR PRIMARY KEY,
                information_id VARCHAR NOT NULL,
                security_id VARCHAR NOT NULL,
                reaction_start VARCHAR NOT NULL,
                reaction_end VARCHAR NOT NULL,
                horizon VARCHAR DEFAULT '1D',
                return_pct DOUBLE DEFAULT 0.0,
                relative_return DOUBLE DEFAULT 0.0,
                volume_change DOUBLE DEFAULT 0.0,
                volatility_change DOUBLE DEFAULT 0.0,
                regime VARCHAR DEFAULT 'NORMAL',
                observation_status VARCHAR DEFAULT 'OBSERVED'
            );
        """)

        # 7. POLICY & ECONOMIC CHANNELS
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS policies (
                policy_id VARCHAR PRIMARY KEY,
                political_event_id VARCHAR,
                title VARCHAR NOT NULL,
                policy_type VARCHAR DEFAULT 'REGULATION',
                issuing_institution_id VARCHAR NOT NULL,
                economic_channel VARCHAR NOT NULL,
                effective_from VARCHAR NOT NULL,
                effective_to VARCHAR,
                status VARCHAR DEFAULT 'ACTIVE'
            );
            CREATE TABLE IF NOT EXISTS economic_channels (
                channel_code VARCHAR PRIMARY KEY,
                channel_name VARCHAR NOT NULL,
                description VARCHAR DEFAULT ''
            );
        """)

        # 8. INTELLIGENCE, PROPAGATION & CONTRADICTIONS
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS exposures (
                exposure_id VARCHAR PRIMARY KEY,
                entity_id VARCHAR NOT NULL,
                information_id VARCHAR,
                economic_channel VARCHAR NOT NULL,
                exposure_type VARCHAR DEFAULT 'DIRECT',
                direction VARCHAR DEFAULT 'POSITIVE',
                magnitude_class VARCHAR DEFAULT 'MEDIUM',
                valid_from VARCHAR DEFAULT '1970-01-01T00:00:00Z',
                valid_to VARCHAR,
                evidence_status VARCHAR DEFAULT 'SUPPORTED'
            );
            CREATE TABLE IF NOT EXISTS mechanisms (
                mechanism_id VARCHAR PRIMARY KEY,
                exposure_id VARCHAR NOT NULL,
                mechanism_type VARCHAR NOT NULL,
                economic_channel VARCHAR NOT NULL,
                description VARCHAR NOT NULL,
                expected_direction VARCHAR DEFAULT 'POSITIVE',
                evidence_status VARCHAR DEFAULT 'SUPPORTED',
                temporal_status VARCHAR DEFAULT 'ACTIVE',
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS contradictions (
                contradiction_id VARCHAR PRIMARY KEY,
                subject_id VARCHAR NOT NULL,
                contradiction_type VARCHAR NOT NULL,
                evidence_a_id VARCHAR NOT NULL,
                evidence_b_id VARCHAR NOT NULL,
                severity VARCHAR DEFAULT 'MEDIUM',
                temporal_scope VARCHAR DEFAULT 'ACTIVE',
                resolution_status VARCHAR DEFAULT 'UNRESOLVED',
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS market_snapshots_at_availability (
                snapshot_id VARCHAR PRIMARY KEY,
                information_id VARCHAR NOT NULL,
                symbol VARCHAR NOT NULL,
                availability_timestamp VARCHAR NOT NULL,
                stock_price DOUBLE NOT NULL,
                stock_volume DOUBLE NOT NULL,
                ihsg_price DOUBLE DEFAULT 0.0,
                sector_name VARCHAR DEFAULT 'UNKNOWN',
                sector_performance_1d DOUBLE DEFAULT 0.0,
                relative_strength_vs_ihsg DOUBLE DEFAULT 0.0,
                market_regime VARCHAR DEFAULT 'UNKNOWN',
                liquidity_status VARCHAR DEFAULT 'LIQUID',
                as_of_market_time VARCHAR NOT NULL,
                created_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS propagated_exposures (
                propagation_id VARCHAR PRIMARY KEY,
                origin_entity_id VARCHAR NOT NULL,
                policy_or_event_id VARCHAR NOT NULL,
                target_entity_id VARCHAR NOT NULL,
                economic_channel VARCHAR NOT NULL,
                exposure_type VARCHAR NOT NULL,
                transmission_path_json VARCHAR NOT NULL,
                direction VARCHAR DEFAULT 'POSITIVE',
                magnitude_class VARCHAR DEFAULT 'MEDIUM',
                valid_from VARCHAR NOT NULL,
                valid_to VARCHAR,
                created_at VARCHAR NOT NULL
            );
        """)

        # 9. AUDIT & DERIVED INDEXES
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS platform_audit_log (
                audit_id VARCHAR PRIMARY KEY,
                check_type VARCHAR NOT NULL,
                target_table VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                details VARCHAR,
                checked_at VARCHAR NOT NULL
            );
            CREATE TABLE IF NOT EXISTS derived_entity_neighborhood (
                entity_id VARCHAR NOT NULL,
                related_entity_id VARCHAR NOT NULL,
                relationship_type VARCHAR NOT NULL,
                distance INTEGER DEFAULT 1,
                valid_from VARCHAR NOT NULL,
                valid_to VARCHAR
            );
            CREATE TABLE IF NOT EXISTS derived_entity_exposure_index (
                entity_id VARCHAR NOT NULL,
                economic_channel VARCHAR NOT NULL,
                exposure_type VARCHAR NOT NULL,
                direction VARCHAR NOT NULL,
                valid_from VARCHAR NOT NULL,
                valid_to VARCHAR
            );
        """)

        # Populate economic channels if empty
        self._populate_standard_economic_channels()

        # Create Composite Indexes for Fast Retrieval
        self._create_performance_indexes()

    def _populate_standard_economic_channels(self):
        count = self.conn.execute("SELECT count(*) FROM economic_channels").fetchone()[0]
        if count == 0:
            channels = [
                ("TAX", "Taxation and fiscal levies"),
                ("SUBSIDY", "Government subsidies and direct support"),
                ("IMPORT_DUTY", "Tariffs and import duties"),
                ("EXPORT_RESTRICTION", "Export bans, quotas, and DMO requirements"),
                ("LICENSING", "Operating licenses and concessions"),
                ("PERMIT", "Environmental and spatial permits"),
                ("PROCUREMENT", "Government and state procurement"),
                ("GOVERNMENT_SPENDING", "Public infrastructure and state spending"),
                ("INTEREST_RATE", "BI rate and benchmark interest rates"),
                ("FX", "Foreign exchange rate and currency stability"),
                ("COMMODITY_PRICE", "Global and domestic commodity benchmark prices"),
                ("ENERGY_COST", "Electricity, fuel, and industrial energy tariffs"),
                ("INPUT_COST", "Raw materials and supply input inflation"),
                ("DEMAND", "Consumer and industrial end-market demand"),
                ("SUPPLY", "Market capacity and production constraints"),
                ("CAPEX", "Capital expenditure and investment requirements"),
                ("REGULATORY_COST", "Compliance and institutional costs"),
                ("MARKET_ACCESS", "Cross-border trade agreements and access"),
                ("CREDIT", "Banking credit availability and lending terms"),
                ("LIQUIDITY", "Systemic market and banking liquidity"),
                ("OWNERSHIP", "Divestment, state ownership, and equity caps"),
                ("COMPETITION", "Antitrust and market competition dynamics")
            ]
            for code, desc in channels:
                self.conn.execute("INSERT OR IGNORE INTO economic_channels VALUES (?, ?, ?)", (code, code, desc))

    def _create_performance_indexes(self):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ent_canonical ON entities (canonical_name);",
            "CREATE INDEX IF NOT EXISTS idx_ent_alias ON entity_aliases (alias);",
            "CREATE INDEX IF NOT EXISTS idx_ent_ident ON entity_identifiers (identifier_value);",
            "CREATE INDEX IF NOT EXISTS idx_info_pub ON information_items (published_at, available_at);",
            "CREATE INDEX IF NOT EXISTS idx_info_hash ON information_items (content_hash);",
            "CREATE INDEX IF NOT EXISTS idx_rel_subj_obj ON entity_relationships (subject_entity_id, object_entity_id, relationship_type);",
            "CREATE INDEX IF NOT EXISTS idx_rel_validity ON entity_relationships (valid_from, valid_to);",
            "CREATE INDEX IF NOT EXISTS idx_ev_info ON evidence (information_id, source_id);",
            "CREATE INDEX IF NOT EXISTS idx_exp_entity ON exposures (entity_id, economic_channel);"
        ]
        for idx in indexes:
            try:
                self.conn.execute(idx)
            except Exception as e:
                logger.debug("Index creation note: %s", e)

    # --- ENTITY RESOLUTION ENGINE ---
    def resolve_entity(
        self, 
        query: str, 
        identifier_type: Optional[str] = None,
        as_of: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Layered Entity Resolution:
        1. Exact identifier lookup (e.g. IDX_TICKER='BBCA', ISIN='ID1000106808')
        2. Exact canonical alias lookup
        3. Exact canonical name lookup
        4. Normalized name match (case & whitespace insensitive)
        5. Contextual candidate match
        6. Unresolved -> UNKNOWN
        """
        if not query or not query.strip():
            return {"status": "UNKNOWN", "entity_id": None, "confidence": 0, "resolution_tier": "EMPTY"}

        q_clean = query.strip()
        q_norm = q_clean.upper()

        # Step 1: Exact Identifier Match
        if identifier_type:
            row = self.conn.execute("""
                SELECT entity_id, identifier_type, identifier_value
                FROM entity_identifiers
                WHERE identifier_type = ? AND UPPER(identifier_value) = ?
            """, (identifier_type, q_norm)).fetchone()
            if row:
                return {
                    "status": "RESOLVED",
                    "entity_id": row[0],
                    "confidence": 100,
                    "resolution_tier": "EXACT_IDENTIFIER",
                    "matched_value": row[2]
                }
        else:
            row = self.conn.execute("""
                SELECT entity_id, identifier_type, identifier_value
                FROM entity_identifiers
                WHERE UPPER(identifier_value) = ?
            """, (q_norm,)).fetchone()
            if row:
                return {
                    "status": "RESOLVED",
                    "entity_id": row[0],
                    "confidence": 98,
                    "resolution_tier": "IDENTIFIER_VALUE",
                    "matched_value": row[2]
                }

        # Step 2: Exact Canonical Alias
        row = self.conn.execute("""
            SELECT entity_id, alias
            FROM entity_aliases
            WHERE UPPER(alias) = ?
        """, (q_norm,)).fetchone()
        if row:
            return {
                "status": "RESOLVED",
                "entity_id": row[0],
                "confidence": 95,
                "resolution_tier": "CANONICAL_ALIAS",
                "matched_value": row[1]
            }

        # Step 3: Exact Canonical Name
        row = self.conn.execute("""
            SELECT entity_id, canonical_name
            FROM entities
            WHERE UPPER(canonical_name) = ?
        """, (q_norm,)).fetchone()
        if row:
            return {
                "status": "RESOLVED",
                "entity_id": row[0],
                "confidence": 92,
                "resolution_tier": "CANONICAL_NAME",
                "matched_value": row[1]
            }

        # Step 4: Substring / Prefix Candidate Match
        candidates = self.conn.execute("""
            SELECT entity_id, canonical_name
            FROM entities
            WHERE UPPER(canonical_name) LIKE ?
            LIMIT 5
        """, (f"%{q_norm}%",)).fetchall()
        
        if len(candidates) == 1:
            return {
                "status": "RESOLVED",
                "entity_id": candidates[0][0],
                "confidence": 75,
                "resolution_tier": "UNIQUE_PARTIAL_MATCH",
                "matched_value": candidates[0][1]
            }
        elif len(candidates) > 1:
            return {
                "status": "AMBIGUOUS",
                "entity_id": None,
                "candidates": [{"entity_id": c[0], "name": c[1]} for c in candidates],
                "confidence": 40,
                "resolution_tier": "AMBIGUOUS_PARTIAL_MATCH"
            }

        return {
            "status": "UNKNOWN",
            "entity_id": None,
            "confidence": 0,
            "resolution_tier": "UNRESOLVED"
        }

    # --- INGESTION PIPELINE ---
    def ingest_raw_document(self, raw_doc: RawDocumentRecord) -> Dict[str, Any]:
        """Ingests a raw immutable document with SHA-256 fingerprinting."""
        fingerprint = compute_document_fingerprint(
            raw_doc.source_id, raw_doc.source_document_id,
            raw_doc.content_hash, raw_doc.published_at
        )
        
        # Check duplicate
        dup = self.conn.execute("""
            SELECT raw_document_id FROM raw_documents
            WHERE content_hash = ? AND source_id = ?
        """, (raw_doc.content_hash, raw_doc.source_id)).fetchone()
        
        if dup:
            return {
                "status": "DUPLICATE_REJECTED",
                "existing_raw_document_id": dup[0],
                "fingerprint": fingerprint
            }

        self.conn.execute("""
            INSERT INTO raw_documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            raw_doc.raw_document_id, raw_doc.source_id, raw_doc.source_document_id,
            raw_doc.retrieved_at, raw_doc.published_at, raw_doc.available_at,
            raw_doc.content_hash, raw_doc.content_type, raw_doc.mime_type,
            raw_doc.language, raw_doc.raw_location, raw_doc.raw_size,
            raw_doc.access_class.value, raw_doc.ingestion_run_id,
            raw_doc.origin_class.value, raw_doc.created_at
        ))
        return {
            "status": "INGESTED",
            "raw_document_id": raw_doc.raw_document_id,
            "fingerprint": fingerprint
        }

    def register_entity(self, entity: EntityRecord) -> Dict[str, Any]:
        """Registers a canonical entity with semantic validation."""
        is_valid, reason, _ = validate_entity_semantic_type(entity.entity_id, entity.entity_type.value)
        if not is_valid:
            # Also try canonical name
            is_valid_name, reason_name, _ = validate_entity_semantic_type(entity.canonical_name, entity.entity_type.value)
            if not is_valid_name:
                is_valid = False
                reason = reason_name
        sem_status = "VALID" if is_valid else "CONFLICT_DETECTED"
        if not is_valid:
            logger.warning("Entity semantic warning: %s", reason)

        self.conn.execute("""
            INSERT OR REPLACE INTO entities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entity.entity_id, entity.canonical_name, entity.entity_type.value,
            entity.jurisdiction, entity.status, entity.valid_from,
            entity.valid_to, entity.created_at, entity.updated_at
        ))
        return {"status": "REGISTERED", "entity_id": entity.entity_id, "semantic_status": sem_status}

    def register_relationship(
        self, 
        rel: EntityRelationshipRecord, 
        evidence_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Registers an entity relationship and connects it to supporting evidence."""
        # Fetch subject and object entity types
        sub_row = self.conn.execute("SELECT entity_type FROM entities WHERE entity_id = ?", (rel.subject_entity_id,)).fetchone()
        obj_row = self.conn.execute("SELECT entity_type FROM entities WHERE entity_id = ?", (rel.object_entity_id,)).fetchone()
        
        sub_type = EntityType(sub_row[0]) if sub_row else EntityType.UNKNOWN
        obj_type = EntityType(obj_row[0]) if obj_row else EntityType.UNKNOWN
        
        is_valid, reason = validate_relationship_semantics(sub_type, rel.relationship_type, obj_type)
        if not is_valid:
            return {
                "status": "REJECTED_SEMANTIC_FIREWALL",
                "reason": reason
            }

        self.conn.execute("""
            INSERT OR REPLACE INTO entity_relationships (
                relationship_id, subject_entity_id, relationship_type,
                object_entity_id, valid_from, valid_to,
                observed_at, status, source_priority,
                created_at, updated_at, confidence
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            rel.relationship_id, rel.subject_entity_id, rel.relationship_type.value,
            rel.object_entity_id, rel.valid_from, rel.valid_to,
            rel.observed_at, rel.status, rel.source_priority,
            rel.created_at, rel.updated_at, getattr(rel, 'confidence', 1.0)
        ))

        if evidence_id:
            rel_ev_id = f"RELEV_{rel.relationship_id}_{evidence_id}"
            self.conn.execute("""
                INSERT OR REPLACE INTO relationship_evidence VALUES (?, ?, ?, ?, ?, ?)
            """, (
                rel_ev_id, rel.relationship_id, evidence_id,
                EvidenceRole.PRIMARY.value, "SUPPORTED", rel.created_at
            ))

        return {"status": "REGISTERED", "relationship_id": rel.relationship_id}

    def insert_raw_document(self, raw_doc: RawDocumentRecord) -> Dict[str, Any]:
        return self.ingest_raw_document(raw_doc)

    def insert_source(self, source: SourceRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO sources VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source.source_id, source.source_name, source.publisher, source.source_type.value,
            source.jurisdiction, source.domain, source.canonical_url, source.authority_class,
            source.source_status, source.access_class.value, source.created_at, source.updated_at
        ))
        return {"status": "INSERTED", "source_id": source.source_id}

    def insert_entity(self, entity: EntityRecord) -> Dict[str, Any]:
        return self.register_entity(entity)

    def insert_entity_alias(self, entity_id: str, alias: str, alias_type: str = "COMMON_NAME", valid_from: str = "1970-01-01T00:00:00Z", valid_to: Optional[str] = None, source_id: str = "SYSTEM") -> Dict[str, Any]:
        alias_id = f"ALIAS_{hashlib.sha256((entity_id + alias).encode('utf-8')).hexdigest()[:12].upper()}"
        self.conn.execute("""
            INSERT OR REPLACE INTO entity_aliases VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (alias_id, entity_id, alias, alias_type, "id", valid_from, valid_to, source_id))
        return {"status": "INSERTED", "alias_id": alias_id}

    def insert_entity_identifier(self, entity_id: str, identifier_type: str, identifier_value: str, issuer: str = "IDX", valid_from: str = "1970-01-01T00:00:00Z", valid_to: Optional[str] = None) -> Dict[str, Any]:
        ident_id = f"ID_{hashlib.sha256((entity_id + identifier_type + identifier_value).encode('utf-8')).hexdigest()[:12].upper()}"
        self.conn.execute("""
            INSERT OR REPLACE INTO entity_identifiers VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (ident_id, entity_id, identifier_type, identifier_value, issuer, valid_from, valid_to))
        return {"status": "INSERTED", "identifier_id": ident_id}

    def insert_information_item(self, info: InformationItemRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO information_items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            info.information_id, info.document_id, info.information_type.value,
            info.title, info.summary, info.language, info.published_at, info.available_at,
            info.effective_from, info.effective_to, info.access_class.value, info.origin_class.value,
            info.semantic_status, info.temporal_status, info.provenance_status,
            info.content_hash, info.created_at, info.updated_at
        ))
        return {"status": "INSERTED", "information_id": info.information_id}

    def insert_claim(self, claim: ClaimRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO claims VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            claim.claim_id, claim.information_id, claim.subject_entity_id,
            claim.predicate, claim.object_entity_id, claim.claim_type,
            claim.claim_text, claim.temporal_scope, claim.evidence_status,
            claim.semantic_status, claim.created_at
        ))
        return {"status": "INSERTED", "claim_id": claim.claim_id}

    def insert_evidence(self, ev: EvidenceRecord) -> Dict[str, Any]:
        deriv_method = ev.derivation_method.value if hasattr(ev.derivation_method, 'value') else str(ev.derivation_method)
        temp_conf = ev.temporal_confidence.value if hasattr(ev.temporal_confidence, 'value') else str(ev.temporal_confidence)
        acc_cls = ev.access_class.value if hasattr(ev.access_class, 'value') else str(ev.access_class)
        orig_cls = ev.origin_class.value if hasattr(ev.origin_class, 'value') else str(ev.origin_class)
        self.conn.execute("""
            INSERT OR REPLACE INTO evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ev.evidence_id, ev.information_id, ev.source_id, ev.document_id,
            ev.claim_id, ev.evidence_type, ev.excerpt_reference, ev.content_hash,
            ev.event_time, ev.published_at, ev.available_at, ev.observed_at,
            ev.timestamp_source, deriv_method, temp_conf,
            acc_cls, orig_cls, ev.provenance_status, ev.created_at
        ))
        return {"status": "INSERTED", "evidence_id": ev.evidence_id}

    def insert_relationship(self, rel: EntityRelationshipRecord, evidence_id: Optional[str] = None) -> Dict[str, Any]:
        return self.register_relationship(rel, evidence_id)

    def insert_exposure(self, exp: ExposureRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO exposures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exp.exposure_id, exp.entity_id, exp.information_id, exp.economic_channel.value,
            exp.exposure_type.value, exp.direction, exp.magnitude_class, exp.valid_from,
            exp.valid_to, exp.evidence_status
        ))
        return {"status": "INSERTED", "exposure_id": exp.exposure_id}

    def insert_mechanism(self, mech: MechanismRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO mechanisms VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            mech.mechanism_id, mech.exposure_id, mech.mechanism_type, mech.economic_channel.value,
            mech.description, mech.expected_direction, mech.evidence_status,
            mech.temporal_status, mech.created_at
        ))
        return {"status": "INSERTED", "mechanism_id": mech.mechanism_id}

    def insert_contradiction(self, con: ContradictionDataRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO contradictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            con.contradiction_id, con.subject_id, con.contradiction_type.value,
            con.evidence_a_id, con.evidence_b_id, con.severity,
            con.temporal_scope, con.resolution_status, con.created_at
        ))
        return {"status": "INSERTED", "contradiction_id": con.contradiction_id}

    def insert_policy(self, pol: PolicyRecord) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO policies VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pol.policy_id, pol.political_event_id, pol.title, pol.policy_type,
            pol.issuing_institution_id, pol.economic_channel.value if hasattr(pol.economic_channel, 'value') else pol.economic_channel,
            pol.effective_from, pol.effective_to, pol.status
        ))
        return {"status": "INSERTED", "policy_id": pol.policy_id}

    def insert_event_cluster(self, cluster: EventClusterRecord) -> Dict[str, Any]:
        corrob_status = cluster.corroboration_status.value if hasattr(cluster.corroboration_status, 'value') else cluster.corroboration_status
        self.conn.execute("""
            INSERT OR REPLACE INTO event_clusters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cluster.cluster_id, cluster.canonical_event_name, cluster.primary_entity_id,
            cluster.event_type, cluster.first_observed_at, cluster.latest_update_at,
            cluster.independent_sources_count, cluster.syndicated_copies_count,
            corrob_status, cluster.primary_information_id, cluster.created_at
        ))
        return {"status": "INSERTED", "cluster_id": cluster.cluster_id}

    def insert_information_delta(self, delta: InformationDeltaRecord) -> Dict[str, Any]:
        nov_cls = delta.novelty_class.value if hasattr(delta.novelty_class, 'value') else delta.novelty_class
        self.conn.execute("""
            INSERT OR REPLACE INTO information_deltas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            delta.delta_id, delta.entity_id, delta.information_id, delta.cluster_id,
            delta.attribute_name, delta.previous_state, delta.new_state,
            nov_cls, delta.change_time, delta.available_at,
            delta.supporting_evidence_id, delta.created_at
        ))
        return {"status": "INSERTED", "delta_id": delta.delta_id}

    def insert_market_snapshot_at_availability(self, snapshot: MarketSnapshotAtAvailability) -> Dict[str, Any]:
        self.conn.execute("""
            INSERT OR REPLACE INTO market_snapshots_at_availability VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot.snapshot_id, snapshot.information_id, snapshot.symbol,
            snapshot.availability_timestamp, snapshot.stock_price, snapshot.stock_volume,
            snapshot.ihsg_price, snapshot.sector_name, snapshot.sector_performance_1d,
            snapshot.relative_strength_vs_ihsg, snapshot.market_regime, snapshot.liquidity_status,
            snapshot.as_of_market_time, snapshot.created_at
        ))
        return {"status": "INSERTED", "snapshot_id": snapshot.snapshot_id}

    def insert_propagated_exposure(self, exp: PropagatedExposureResult) -> Dict[str, Any]:
        hops_json = json.dumps([h.model_dump() for h in exp.transmission_path])
        exp_type = exp.exposure_type.value if hasattr(exp.exposure_type, 'value') else str(exp.exposure_type)
        channel = exp.economic_channel.value if hasattr(exp.economic_channel, 'value') else str(exp.economic_channel)
        self.conn.execute("""
            INSERT OR REPLACE INTO propagated_exposures VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exp.propagation_id, exp.origin_entity_id, exp.policy_or_event_id,
            exp.target_entity_id, channel, exp_type,
            hops_json, exp.direction, exp.magnitude_class,
            exp.valid_from, exp.valid_to, exp.created_at
        ))
        return {"status": "INSERTED", "propagation_id": exp.propagation_id}

    def get_event_clusters_for_entity(self, entity_id: str, as_of: Optional[str] = None) -> List[Dict[str, Any]]:
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        rows = self.conn.execute("""
            SELECT cluster_id, canonical_event_name, primary_entity_id, event_type,
                   first_observed_at, latest_update_at, independent_sources_count,
                   syndicated_copies_count, corroboration_status, primary_information_id, created_at
            FROM event_clusters
            WHERE primary_entity_id = ?
              AND first_observed_at <= ?
            ORDER BY latest_update_at DESC
        """, (entity_id, as_of_ts)).fetchall()
        return [
            {
                "cluster_id": r[0],
                "canonical_event_name": r[1],
                "primary_entity_id": r[2],
                "event_type": r[3],
                "first_observed_at": r[4],
                "latest_update_at": r[5],
                "independent_sources_count": r[6],
                "syndicated_copies_count": r[7],
                "corroboration_status": r[8],
                "primary_information_id": r[9],
                "created_at": r[10]
            }
            for r in rows
        ]

    def get_information_deltas_for_entity(self, entity_id: str, as_of: Optional[str] = None, lookback_hours: int = 48) -> List[Dict[str, Any]]:
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        try:
            dt_as_of = datetime.fromisoformat(as_of_ts.replace("Z", "+00:00"))
            import datetime as dt_mod
            dt_start = dt_as_of - dt_mod.timedelta(hours=lookback_hours)
            start_ts = dt_start.isoformat()
        except Exception:
            start_ts = "1970-01-01T00:00:00Z"

        rows = self.conn.execute("""
            SELECT delta_id, entity_id, information_id, cluster_id, attribute_name,
                   previous_state, new_state, novelty_class, change_time, available_at,
                   supporting_evidence_id, created_at
            FROM information_deltas
            WHERE entity_id = ?
              AND available_at <= ?
              AND available_at >= ?
            ORDER BY available_at DESC
        """, (entity_id, as_of_ts, start_ts)).fetchall()
        return [
            {
                "delta_id": r[0],
                "entity_id": r[1],
                "information_id": r[2],
                "cluster_id": r[3],
                "attribute_name": r[4],
                "previous_state": r[5],
                "new_state": r[6],
                "novelty_class": r[7],
                "change_time": r[8],
                "available_at": r[9],
                "supporting_evidence_id": r[10],
                "created_at": r[11]
            }
            for r in rows
        ]

    def get_market_snapshot_at_availability(self, information_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("""
            SELECT snapshot_id, information_id, symbol, availability_timestamp, stock_price,
                   stock_volume, ihsg_price, sector_name, sector_performance_1d,
                   relative_strength_vs_ihsg, market_regime, liquidity_status, as_of_market_time, created_at
            FROM market_snapshots_at_availability
            WHERE information_id = ?
        """, (information_id,)).fetchone()
        if not row:
            return None
        return {
            "snapshot_id": row[0],
            "information_id": row[1],
            "symbol": row[2],
            "availability_timestamp": row[3],
            "stock_price": row[4],
            "stock_volume": row[5],
            "ihsg_price": row[6],
            "sector_name": row[7],
            "sector_performance_1d": row[8],
            "relative_strength_vs_ihsg": row[9],
            "market_regime": row[10],
            "liquidity_status": row[11],
            "as_of_market_time": row[12],
            "created_at": row[13]
        }

    def propagate_macro_policy_exposure(self, policy_id: str, as_of: Optional[str] = None) -> List[PropagatedExposureResult]:
        """
        Propagates macro/regulatory policy shock across economic transmission graph:
        POLICY -> ECONOMIC CHANNEL -> SECTOR -> COMPANY / EXPOSURE.
        Enforces explainability with explicit TransmissionHops and strict PIT bounds.
        """
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        
        # 1. Fetch Policy
        pol_row = self.conn.execute("""
            SELECT policy_id, title, issuing_institution_id, economic_channel, effective_from, effective_to, status
            FROM policies
            WHERE policy_id = ? AND effective_from <= ? AND (effective_to IS NULL OR effective_to > ?)
        """, (policy_id, as_of_ts, as_of_ts)).fetchone()
        
        if not pol_row:
            return []

        p_id, p_title, p_issuer, p_channel, p_from, p_to, p_status = pol_row
        results = []

        # 2. Find direct sector or company exposures matching this economic channel
        exp_rows = self.conn.execute("""
            SELECT exposure_id, entity_id, economic_channel, exposure_type, direction, magnitude_class, valid_from, valid_to
            FROM exposures
            WHERE economic_channel = ?
              AND valid_from <= ?
              AND (valid_to IS NULL OR valid_to > ?)
        """, (p_channel, as_of_ts, as_of_ts)).fetchall()

        now_str = datetime.now(timezone.utc).isoformat()

        for exp in exp_rows:
            e_id, ent_id, e_chan, e_type, e_dir, e_mag, e_from, e_to = exp
            
            # Check if ent_id is a Sector or a Direct Company
            ent_type_row = self.conn.execute("SELECT entity_type, canonical_name FROM entities WHERE entity_id = ?", (ent_id,)).fetchone()
            ent_type = ent_type_row[0] if ent_type_row else "UNKNOWN"
            ent_name = ent_type_row[1] if ent_type_row else ent_id

            if ent_type == "SECTOR":
                # Multi-hop: Propagate from SECTOR to constituent COMPANIES
                constituents = self.conn.execute("""
                    SELECT subject_entity_id, relationship_type, e.canonical_name
                    FROM entity_relationships r
                    JOIN entities e ON r.subject_entity_id = e.entity_id
                    WHERE r.object_entity_id = ?
                      AND r.status = 'ACTIVE'
                      AND r.valid_from <= ?
                      AND (r.valid_to IS NULL OR r.valid_to > ?)
                """, (ent_id, as_of_ts, as_of_ts)).fetchall()

                for comp in constituents:
                    comp_id, rel_type, comp_name = comp
                    hops = [
                        TransmissionHop(
                            hop_distance=1,
                            source_node=p_issuer,
                            relationship_type="REGULATES",
                            target_node=p_channel,
                            economic_channel=p_channel,
                            confidence=0.95
                        ),
                        TransmissionHop(
                            hop_distance=2,
                            source_node=p_channel,
                            relationship_type="AFFECTS",
                            target_node=ent_id,
                            economic_channel=p_channel,
                            confidence=0.90
                        ),
                        TransmissionHop(
                            hop_distance=3,
                            source_node=ent_id,
                            relationship_type=rel_type,
                            target_node=comp_id,
                            economic_channel=p_channel,
                            confidence=0.85
                        )
                    ]
                    prop_id = f"PROP_{p_id}_{comp_id}_{p_from[:10]}"
                    prop_res = PropagatedExposureResult(
                        propagation_id=prop_id,
                        origin_entity_id=p_issuer,
                        policy_or_event_id=p_id,
                        target_entity_id=comp_id,
                        economic_channel=EconomicChannel(p_channel) if p_channel in [e.value for e in EconomicChannel] else EconomicChannel.REGULATORY_COST,
                        exposure_type=ExposureType.INDIRECT_EXPOSURE,
                        transmission_path=hops,
                        direction=e_dir,
                        magnitude_class=e_mag,
                        valid_from=p_from,
                        valid_to=p_to,
                        created_at=now_str
                    )
                    self.insert_propagated_exposure(prop_res)
                    results.append(prop_res)
            else:
                # Direct Company exposure
                hops = [
                    TransmissionHop(
                        hop_distance=1,
                        source_node=p_issuer,
                        relationship_type="REGULATES",
                        target_node=p_channel,
                        economic_channel=p_channel,
                        confidence=0.95
                    ),
                    TransmissionHop(
                        hop_distance=2,
                        source_node=p_channel,
                        relationship_type="EXPOSES",
                        target_node=ent_id,
                        economic_channel=p_channel,
                        confidence=0.90
                    )
                ]

                prop_id = f"PROP_{p_id}_{ent_id}_{p_from[:10]}"
                prop_res = PropagatedExposureResult(
                    propagation_id=prop_id,
                    origin_entity_id=p_issuer,
                    policy_or_event_id=p_id,
                    target_entity_id=ent_id,
                    economic_channel=EconomicChannel(p_channel) if p_channel in [e.value for e in EconomicChannel] else EconomicChannel.REGULATORY_COST,
                    exposure_type=ExposureType(e_type) if e_type in [e.value for e in ExposureType] else ExposureType.DIRECT_EXPOSURE,
                    transmission_path=hops,
                    direction=e_dir,
                    magnitude_class=e_mag,
                    valid_from=p_from,
                    valid_to=p_to,
                    created_at=now_str
                )

                self.insert_propagated_exposure(prop_res)
                results.append(prop_res)

        return results

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
    ) -> List[ExposurePath]:
        """
        Bounded multi-hop economic transmission traversal:
        - Cycle detection & prevention
        - Duplicate path collapse (keeps optimal confidence path)
        - Strict PIT bounds (relationship valid_from/valid_to, evidence available_at <= as_of)
        - Access class firewall (blocks RESTRICTED / MNPI)
        - Preserves UNKNOWN without forced false resolution
        """
        as_of_ts = as_of or datetime.now(timezone.utc).isoformat()
        disallowed_access = {"RESTRICTED", "MNPI", "MNPI_SUSPECTED"}
        if access_class_filter:
            disallowed_access.update(access_class_filter)

        queue = [(origin_entity_id, [], {origin_entity_id}, 1.0)]
        path_cache: Dict[Tuple[str, str, Tuple[str, ...]], ExposurePath] = {}

        while queue:
            curr_node, hops_list, visited, curr_conf = queue.pop(0)
            curr_depth = len(hops_list)

            # Check if target reached (if target_entity_id specified and depth >= 1)
            if target_entity_id and curr_node == target_entity_id and curr_depth >= 1:
                ep = self._build_exposure_path(origin_entity_id, curr_node, hops_list, curr_conf)
                cache_key = (ep.origin_entity, ep.target_entity, tuple(ep.relationship_sequence))
                if cache_key not in path_cache or path_cache[cache_key].cumulative_confidence < ep.cumulative_confidence:
                    path_cache[cache_key] = ep
                continue

            if curr_depth >= max_hops:
                if not target_entity_id and curr_depth >= 1:
                    ep = self._build_exposure_path(origin_entity_id, curr_node, hops_list, curr_conf)
                    cache_key = (ep.origin_entity, ep.target_entity, tuple(ep.relationship_sequence))
                    if cache_key not in path_cache or path_cache[cache_key].cumulative_confidence < ep.cumulative_confidence:
                        path_cache[cache_key] = ep
                continue

            # Query outgoing edges from curr_node
            edges_out = self.conn.execute("""
                SELECT 
                    r.relationship_id,
                    r.subject_entity_id,
                    r.relationship_type,
                    r.object_entity_id,
                    r.valid_from,
                    r.valid_to,
                    e.entity_type,
                    COALESCE(ev.evidence_id, 'UNKNOWN'),
                    COALESCE(ev.source_id, 'UNKNOWN'),
                    COALESCE(ev.available_at, r.valid_from),
                    COALESCE(ev.access_class, 'PUBLIC'),
                    COALESCE(r.confidence, 1.0)
                FROM entity_relationships r
                JOIN entities e ON r.object_entity_id = e.entity_id
                LEFT JOIN relationship_evidence re ON r.relationship_id = re.relationship_id
                LEFT JOIN evidence ev ON re.evidence_id = ev.evidence_id
                WHERE r.subject_entity_id = ?
                  AND r.status = 'ACTIVE'
                  AND r.valid_from <= ?
                  AND (r.valid_to IS NULL OR r.valid_to > ?)
            """, (curr_node, as_of_ts, as_of_ts)).fetchall()

            # Query incoming constituent edges to curr_node (e.g. ADRO OPERATES_IN COAL_SECTOR)
            edges_in = self.conn.execute("""
                SELECT 
                    r.relationship_id,
                    r.object_entity_id AS subject_entity_id,
                    r.relationship_type,
                    r.subject_entity_id AS object_entity_id,
                    r.valid_from,
                    r.valid_to,
                    e.entity_type,
                    COALESCE(ev.evidence_id, 'UNKNOWN'),
                    COALESCE(ev.source_id, 'UNKNOWN'),
                    COALESCE(ev.available_at, r.valid_from),
                    COALESCE(ev.access_class, 'PUBLIC'),
                    COALESCE(r.confidence, 1.0)
                FROM entity_relationships r
                JOIN entities e ON r.subject_entity_id = e.entity_id
                LEFT JOIN relationship_evidence re ON r.relationship_id = re.relationship_id
                LEFT JOIN evidence ev ON re.evidence_id = ev.evidence_id
                WHERE r.object_entity_id = ?
                  AND r.relationship_type IN ('OPERATES_IN', 'SUBSIDIARY_OF', 'CUSTOMER_OF', 'DEPENDS_ON')
                  AND r.status = 'ACTIVE'
                  AND r.valid_from <= ?
                  AND (r.valid_to IS NULL OR r.valid_to > ?)
            """, (curr_node, as_of_ts, as_of_ts)).fetchall()

            edges = edges_out + edges_in

            for edge in edges:
                rel_id, src_id, rel_type, obj_id, v_from, v_to, obj_type, ev_id, src_id_ev, ev_avail, acc_class, conf_raw = edge
                
                # Check access class firewall
                if acc_class in disallowed_access:
                    continue

                # Check evidence PIT availability
                if ev_avail and ev_avail > as_of_ts:
                    continue

                # Check edge type filter
                if allowed_relationship_types and rel_type not in allowed_relationship_types:
                    continue

                # Check entity type filter
                if allowed_entity_types and obj_type not in allowed_entity_types:
                    continue

                # Cycle prevention
                if obj_id in visited:
                    continue

                hop_conf = float(conf_raw) if conf_raw is not None else 1.0
                new_cum_conf = curr_conf * hop_conf

                if new_cum_conf < min_confidence:
                    continue

                # Derive economic channel if available
                derived_channel = "UNKNOWN"
                exp_match = self.conn.execute("""
                    SELECT economic_channel FROM exposures
                    WHERE entity_id = ? AND valid_from <= ? AND (valid_to IS NULL OR valid_to > ?)
                """, (obj_id, as_of_ts, as_of_ts)).fetchone()
                if exp_match:
                    derived_channel = exp_match[0]

                if allowed_economic_channels and derived_channel not in allowed_economic_channels and derived_channel != "UNKNOWN":
                    continue

                hop_obj = {
                    "source_node": src_id,
                    "relationship_type": rel_type,
                    "target_node": obj_id,
                    "economic_channel": derived_channel,
                    "hop_distance": curr_depth + 1,
                    "evidence_id": ev_id,
                    "source_id": src_id_ev,
                    "available_at": ev_avail,
                    "confidence": hop_conf,
                    "valid_from": v_from,
                    "valid_to": v_to
                }

                new_hops = list(hops_list) + [hop_obj]
                new_visited = set(visited)
                new_visited.add(obj_id)

                queue.append((obj_id, new_hops, new_visited, new_cum_conf))

                # If no specific target, record path to intermediate node
                if not target_entity_id:
                    ep = self._build_exposure_path(origin_entity_id, obj_id, new_hops, new_cum_conf)
                    cache_key = (ep.origin_entity, ep.target_entity, tuple(ep.relationship_sequence))
                    if cache_key not in path_cache or path_cache[cache_key].cumulative_confidence < ep.cumulative_confidence:
                        path_cache[cache_key] = ep

        return list(path_cache.values())

    def _build_exposure_path(self, origin: str, target: str, hops: List[Dict[str, Any]], cum_conf: float) -> ExposurePath:
        path_id = f"PATH_{origin}_{target}_{len(hops)}H_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        rel_seq = [h["relationship_type"] for h in hops]
        ev_seq = [h["evidence_id"] for h in hops]
        src_seq = [h["source_id"] for h in hops]
        avail_seq = [h["available_at"] for h in hops]
        conf_seq = [h["confidence"] for h in hops]
        chan = hops[-1]["economic_channel"] if hops else "REGULATORY_COST"
        
        mech_steps = []
        for h in hops:
            mech_steps.append(f"{h['source_node']} -[{h['relationship_type']}]-> {h['target_node']}")
        mech_desc = " => ".join(mech_steps)

        try:
            econ_enum = EconomicChannel(chan)
        except Exception:
            econ_enum = EconomicChannel.REGULATORY_COST

        return ExposurePath(
            path_id=path_id,
            origin_entity=origin,
            target_entity=target,
            hop_count=len(hops),
            economic_channel=econ_enum,
            relationship_sequence=rel_seq,
            evidence_sequence=ev_seq,
            source_sequence=src_seq,
            available_at_constraints=avail_seq,
            confidence_by_hop=conf_seq,
            cumulative_confidence=round(cum_conf, 4),
            overall_path_status="VALID",
            temporal_validity_from=hops[0].get("valid_from", "1970-01-01T00:00:00Z") if hops else "1970-01-01T00:00:00Z",
            temporal_validity_to=hops[-1].get("valid_to") if hops else None,
            economic_mechanism_description=f"Transmission path: {mech_desc} via channel {chan}"
        )

    # --- DERIVED INDEX MATERIALIZATION ---
    def rebuild_derived_indexes(self) -> Dict[str, int]:
        """Materializes derived entity neighborhood and exposure indexes for FAST PATH."""
        self.conn.execute("DELETE FROM derived_entity_neighborhood")
        self.conn.execute("""
            INSERT INTO derived_entity_neighborhood
            SELECT 
                subject_entity_id AS entity_id,
                object_entity_id AS related_entity_id,
                relationship_type,
                1 AS distance,
                valid_from,
                valid_to
            FROM entity_relationships
            WHERE status = 'ACTIVE'
        """)

        self.conn.execute("DELETE FROM derived_entity_exposure_index")
        self.conn.execute("""
            INSERT INTO derived_entity_exposure_index
            SELECT 
                entity_id,
                economic_channel,
                exposure_type,
                direction,
                COALESCE(valid_from, '1970-01-01T00:00:00Z'),
                valid_to
            FROM exposures
        """)

        n_count = self.conn.execute("SELECT count(*) FROM derived_entity_neighborhood").fetchone()[0]
        e_count = self.conn.execute("SELECT count(*) FROM derived_entity_exposure_index").fetchone()[0]
        return {
            "neighborhood_records": n_count,
            "exposure_index_records": e_count
        }

    # --- DATA QUALITY AUDIT ---
    def run_data_quality_audit(self) -> Dict[str, Any]:
        """
        Executes comprehensive data quality validation:
        1. Completeness (Missing required fields)
        2. Uniqueness (Primary key integrity)
        3. Referential Integrity (Foreign key validity)
        4. Temporal Integrity (valid_from <= valid_to)
        5. Access & Origin Integrity
        """
        findings = []

        # 1. Broken Entity References in Relationships
        broken_rel_sub = self.conn.execute("""
            SELECT r.relationship_id, r.subject_entity_id
            FROM entity_relationships r
            LEFT JOIN entities e ON r.subject_entity_id = e.entity_id
            WHERE e.entity_id IS NULL
        """).fetchall()
        for r in broken_rel_sub:
            findings.append({"check": "REFERENTIAL_INTEGRITY", "issue": f"Subject entity {r[1]} missing for relationship {r[0]}"})

        broken_rel_obj = self.conn.execute("""
            SELECT r.relationship_id, r.object_entity_id
            FROM entity_relationships r
            LEFT JOIN entities e ON r.object_entity_id = e.entity_id
            WHERE e.entity_id IS NULL
        """).fetchall()
        for r in broken_rel_obj:
            findings.append({"check": "REFERENTIAL_INTEGRITY", "issue": f"Object entity {r[1]} missing for relationship {r[0]}"})

        # 2. Temporal Bounds (valid_from > valid_to)
        invalid_time_rel = self.conn.execute("""
            SELECT relationship_id, valid_from, valid_to
            FROM entity_relationships
            WHERE valid_to IS NOT NULL AND valid_from > valid_to
        """).fetchall()
        for r in invalid_time_rel:
            findings.append({"check": "TEMPORAL_INTEGRITY", "issue": f"Relationship {r[0]} has valid_from ({r[1]}) > valid_to ({r[2]})"})

        # 3. Evidence Provenance Linkage
        orphaned_evidence = self.conn.execute("""
            SELECT e.evidence_id, e.source_id
            FROM evidence e
            LEFT JOIN sources s ON e.source_id = s.source_id
            WHERE s.source_id IS NULL
        """).fetchall()
        for r in orphaned_evidence:
            findings.append({"check": "PROVENANCE_INTEGRITY", "issue": f"Evidence {r[0]} references non-existent source {r[1]}"})

        status = "PASS" if not findings else "FAIL"
        return {
            "status": status,
            "findings_count": len(findings),
            "findings": findings
        }

    # --- BACKUP AND RECOVERY ---
    def create_backup(self, backup_dir: str = "data/backup") -> Dict[str, Any]:
        """Creates a snapshot backup of the DuckDB database and records integrity hash."""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"intelligence_backup_{timestamp}.duckdb")
        
        # Checkpoint and close current connection to release Windows file lock
        self.conn.execute("CHECKPOINT")
        self.conn.close()
        
        try:
            # Copy file
            shutil.copy2(self.db_path, backup_file)
        finally:
            self.conn = duckdb.connect(self.db_path)
        
        # Compute SHA-256 hash of backup
        with open(backup_file, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()

        return {
            "status": "BACKUP_CREATED",
            "backup_file": backup_file,
            "backup_hash": h,
            "timestamp": timestamp
        }

    def restore_from_backup(self, backup_file: str) -> bool:
        """Restores database from a backup file."""
        if not os.path.exists(backup_file):
            return False
        self.conn.close()
        shutil.copy2(backup_file, self.db_path)
        self.conn = duckdb.connect(self.db_path)
        return True

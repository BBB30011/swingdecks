# SwingDeck Knowledge Data Platform — Database Schema Specification V1

## 1. Schema Versioning
- **Schema Version:** `1.0.0`
- **Engine:** DuckDB 1.0+ / Parquet
- **Canonical Store Path:** `data/duckdb/intelligence.duckdb`

## 2. Table Definitions

### 2.1 `raw_documents`
Stores immutable raw document ingested from external publishers or scrapers.
- `raw_document_id VARCHAR PRIMARY KEY`: Deterministic ID.
- `source_id VARCHAR NOT NULL`: Foreign key to `sources.source_id`.
- `source_document_id VARCHAR NOT NULL`: Remote document identifier.
- `retrieved_at VARCHAR NOT NULL`: Ingestion timestamp.
- `published_at VARCHAR NOT NULL`: Official publication timestamp.
- `available_at VARCHAR NOT NULL`: Availability timestamp.
- `content_hash VARCHAR NOT NULL`: SHA-256 hash of payload.
- `access_class VARCHAR DEFAULT 'PUBLIC'`: `PUBLIC`, `AUTHORIZED_PRIVATE`, `RESTRICTED`, `MNPI`.
- `origin_class VARCHAR DEFAULT 'NATURAL'`: `NATURAL`, `HISTORICAL`, `FIXTURE`, `SYNTHETIC`, `FAILURE_INJECTION`.

### 2.2 `entities`
Canonical entity master registry.
- `entity_id VARCHAR PRIMARY KEY`: Canonical ID (e.g. `ENT_BBCA`).
- `canonical_name VARCHAR NOT NULL`: Official legal name.
- `entity_type VARCHAR NOT NULL`: Semantic type from `EntityType` enum.
- `jurisdiction VARCHAR DEFAULT 'ID'`: Country code.
- `status VARCHAR DEFAULT 'ACTIVE'`: `ACTIVE`, `INACTIVE`, `MERGED`, `DISSOLVED`.
- `valid_from VARCHAR NOT NULL`: Point-in-time validity start.
- `valid_to VARCHAR`: Point-in-time validity end (or `NULL` if open-ended).

### 2.3 `entity_identifiers`
Deterministic mapping to market identifiers.
- `identifier_id VARCHAR PRIMARY KEY`: (e.g. `IDENT_BBCA_TICKER`).
- `entity_id VARCHAR NOT NULL`: Foreign key to `entities.entity_id`.
- `identifier_type VARCHAR NOT NULL`: `IDX_TICKER`, `ISIN`, `LEI`, `COMPANY_REGISTRATION`.
- `identifier_value VARCHAR NOT NULL`: (e.g. `BBCA`, `ID1000106808`).
- `issuer VARCHAR DEFAULT 'IDX'`.

### 2.4 `entity_relationships`
Directed semantic knowledge graph edges.
- `relationship_id VARCHAR PRIMARY KEY`: (e.g. `REL_ADRO_AADI_OWNERSHIP`).
- `subject_entity_id VARCHAR NOT NULL`: Subject entity ID.
- `relationship_type VARCHAR NOT NULL`: Directed predicate from `RelationshipType`.
- `object_entity_id VARCHAR NOT NULL`: Object entity ID.
- `valid_from VARCHAR NOT NULL`: Effective start date.
- `valid_to VARCHAR`: Effective end date.
- `observed_at VARCHAR NOT NULL`: Ingestion observation date.
- `status VARCHAR DEFAULT 'ACTIVE'`: `ACTIVE`, `EXPIRED`, `SUPERSEDED`.

### 2.5 `relationship_evidence`
Provenance connection between relationships and supporting evidence.
- `relationship_evidence_id VARCHAR PRIMARY KEY`.
- `relationship_id VARCHAR NOT NULL`: Foreign key to `entity_relationships`.
- `evidence_id VARCHAR NOT NULL`: Foreign key to `evidence`.
- `evidence_role VARCHAR DEFAULT 'PRIMARY'`: `PRIMARY`, `SECONDARY`, `CORROBORATING`, `CONTRADICTING`.

### 2.6 `exposures` & `mechanisms`
Structural transmission hypotheses connecting entities to economic channels.
- `exposure_id VARCHAR PRIMARY KEY`.
- `entity_id VARCHAR NOT NULL`.
- `economic_channel VARCHAR NOT NULL`: One of 22 economic channels.
- `exposure_type VARCHAR DEFAULT 'DIRECT_EXPOSURE'`: `DIRECT_EXPOSURE`, `INDIRECT_EXPOSURE`, `SECOND_ORDER_EXPOSURE`.
- `direction VARCHAR DEFAULT 'POSITIVE'`: `POSITIVE`, `NEGATIVE`, `NEUTRAL`.

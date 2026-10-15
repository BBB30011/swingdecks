# SwingDeck Natural Information Ingestion Pipeline V1

## 1. Overview & Architectural Philosophy

SwingDeck's **Natural Information Ingestion Pipeline** is a 16-stage deterministic, immutable, and governance-hardened subsystem designed to process natural language disclosures, official exchange filings, regulatory circulars, and public market information into canonical knowledge structures without compromising Point-in-Time (PIT) integrity, evidence traceability, or access boundaries.

```text
REAL SOURCE (HTTPS / Network / Stream)
    │
    ▼
[STAGE 1] LIVE FETCH & NETWORK INSPECTION
    │
    ▼
[STAGE 2] SOURCE AUTHENTICITY EVALUATION (26-Vector Audit)
    │
    ▼
[STAGE 3] RAW IMMUTABLE CAPTURE (Disk + SHA-256 Storage)
    │
    ▼
[STAGE 4] DETERMINISTIC DOCUMENT IDENTITY & DEDUPLICATION (M1-M10 Invariants)
    │
    ▼
[STAGE 5] 5-TIER ENTITY RESOLUTION & SEMANTIC FIREWALL (IDX != REGULATOR)
    │
    ▼
[STAGE 6] CLAIM EXTRACTION & SOURCE SPAN CAPTURE
    │
    ▼
[STAGE 7] EVIDENCE GENERATION & HASH ANCHORING
    │
    ▼
[STAGE 8] SEMANTIC RELATIONSHIP EXTRACTION & ONTOLOGY VALIDATION
    │
    ▼
[STAGE 9] POINT-IN-TIME (PIT) TEMPORAL VALIDATION
    │
    ▼
[STAGE 10] ACCESS CONTROL & MNPI DECISION FIREWALL
    │
    ▼
[STAGE 11] CONTRADICTION DETECTION & CONFIDENCE DEGRADATION
    │
    ▼
[STAGE 12] CANONICAL PERSISTENCE (DuckDB Intelligence Store)
    │
    ▼
[STAGE 13] DERIVED GRAPH & EXPOSURE REBUILD
    │
    ▼
[STAGE 14] FAST / DEEP PATH RETRIEVAL ENGINE
    │
    ▼
[STAGE 15] AGENT 2 INTELLIGENCE REASONING CONTRACT
    │
    ▼
[STAGE 16] AGENT 3 COMMITTEE SYNTHESIS & RISK BOUNDARY
```

---

## 2. Pipeline Stage Specifications

### Stage 1: Live Fetch & Network Inspection
- Protocol validation: Enforces `http` / `https` scheme verification. Insecure HTTP is downgraded to `PARTIALLY_VERIFIED` or rejected.
- Redirect chain tracing: Detects open redirects and domain spoofing.
- Encoding detection: Inspects Content-Type charsets and handles UTF-8 / ASCII transparently with fallback error replacement.

### Stage 2: Source Authenticity Evaluation
- Analyzes domain registry matches, publisher authority classes (`PRIMARY_OFFICIAL`, `PRIMARY_REGULATORY`, `SECONDARY_REPUTABLE`, etc.).
- Evaluates 26 distinct attack vectors including timestamp validation, lookalike domains, prompt injection payloads, and suspected MNPI phrasing.

### Stage 3: Raw Immutable Capture
- Raw content is stored as an immutable payload on disk (`data/raw/natural/<raw_doc_id>_<timestamp>.raw`).
- Calculates SHA-256 content hashes.
- Ingestion metadata is saved to `raw_documents` in DuckDB.
- **Immutability rule**: Repeated retrievals or subsequent revisions NEVER overwrite existing raw files or raw database records.

### Stage 4: Document Identity & Deduplication
Deterministic identity computation separates:
1. **Idempotent Retrieval**: Exact content hash match (`IDEMPOTENT_RETRIEVAL`) -> Reuses existing canonical record, increments retrieval observation without duplicating claims.
2. **New Revision**: Same canonical URL with modified content (`NEW_REVISION`) -> Assigns versioned `DOC_..._REV_N` identifier, preserving historical versions.
3. **Syndicated Copy**: Same content from different URL (`SYNDICATION_LINK`) -> Links lineage to original publication, preventing artificial corroboration inflation.
4. **New Document**: Unique document (`NEW_DOCUMENT`).

### Stage 5: Strict 5-Tier Entity Resolution
Resolves entities using hierarchical tiers:
- Tier 1: Exact Canonical Identifier (e.g. `ENT_BBCA`, `ENT_IDX`, `ENT_OJK`).
- Tier 2: Official Regulatory Identifier / Ticker (e.g. `BBCA`, `OJK`).
- Tier 3: Normalized Legal Name (e.g. `PT Bank Central Asia Tbk`).
- Tier 4: Contextual Alias.
- Tier 5: Candidate Match Requiring Human Review.
- Ambiguous / unknown entities resolve to `UNKNOWN` (Fail-Closed).

### Stage 6 & 7: Claim & Evidence Extraction
- Extracts atomic factual claims with exact predicates (`ANNOUNCED_OR_REPORTED`, `DIVESTS`, `REGULATES`).
- Each claim is anchored to an `EvidenceRecord` containing exact excerpt references, character spans, publication timestamps, and cryptographic hashes.

### Stage 8: Semantic Relationship Extraction
- Validates extracted relationships against the `RELATIONSHIP_COMPATIBILITY_RULES` matrix in `core/semantic_ontology.py`.
- Enforces strict semantic truths:
  - `IDX` is an `EXCHANGE` (operator), NOT a `REGULATOR`.
  - `OJK` is a `REGULATOR`, NOT an `EXCHANGE`.
  - Spinoff/divestment relationships are classified under `RelationshipType.DISPOSES`.

### Stage 9: Temporal Point-in-Time (PIT) Validation
- Enforces strict availability timestamping:
  $$\text{decision\_time} \ge \text{information\_availability\_time}$$
- Prevents lookahead bias and future data leakage during historical backtests and replay analysis.

### Stage 10: Access & MNPI Firewall
- Classifies data into `PUBLIC`, `AUTHORIZED_PRIVATE`, `RESTRICTED`, `MNPI_SUSPECTED`, `MNPI`, `UNKNOWN`.
- Restricted and suspected MNPI records are strictly blocked from Agent 2/3 decision eligibility (`BLOCKED_MNPI_OR_RESTRICTED`).

### Stage 11: Contradiction Engine
- Cross-references incoming claims against existing active assertions.
- Contradictions are stored explicitly as `ContradictionDataRecord` entries.
- Unresolved contradictions trigger confidence degradation or decision holds (`WAIT`/`AVOID`).

### Stage 12 & 13: Canonical Store & Derived Graph
- Canonical source of truth is stored in DuckDB (`intelligence.duckdb`).
- Derived graph neighborhoods (`derived_entity_neighborhood`, `derived_entity_exposure_index`) are 100% rebuildable from canonical tables.

### Stage 14, 15 & 16: Retrieval & Agent Integration
- Agent 2 accesses structured intelligence exclusively via `KnowledgeRetrievalEngine.retrieve()`.
- Agent 3 Committee receives structured evidence references and enforces risk/firewall boundaries.

---

## 3. Implementation Verification & Regression Status

The pipeline is validated by:
- Unit & Acceptance Suite: `tests/test_natural_information_ingestion.py` (21 tests, 100% PASS).
- Architecture Enforcement: `tests/test_00_architecture_enforcement.py` (PASS).
- Metamorphic Suite: Invariant tests M1 through M10 (PASS).
- Live Telemetry Execution: `scratch/execute_natural_observation.py` (PASS).

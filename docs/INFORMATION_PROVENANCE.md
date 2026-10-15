# SwingDeck Information Provenance & Evidence Traceability V1

## 1. Principle of Full Lineage

In SwingDeck, no piece of market intelligence may enter the decision-making framework without a complete, verifiable cryptographic chain of custody.

```text
RAW_DOCUMENT (SHA-256)
      │
      ▼
CANONICAL_DOCUMENT (DOC_ID)
      │
      ▼
INFORMATION_ITEM (INFO_ID)
      │
      ├──▶ CLAIM_RECORD (CLM_ID, Predicate, Subject)
      │         │
      │         ▼
      └──▶ EVIDENCE_RECORD (EV_ID, Source Span, Character Offset, Hash)
                │
                ▼
      RELATIONSHIP_EVIDENCE (REL_ID)
                │
                ▼
      AGENT 2 INTELLIGENCE PACK (Evidence References)
                │
                ▼
      AGENT 3 INVESTMENT DECISION TRACE (Audit Trail)
```

---

## 2. Granular Provenance Structures

### 2.1 Raw Document Anchoring
Every observation begins at the raw byte layer. The raw document record preserves:
- `raw_document_id`: Deterministic hash of URL, retrieval time, and content prefix.
- `content_hash`: SHA-256 digest of unaltered content.
- `raw_location`: File path on disk containing the exact immutable capture.

### 2.2 Claim-to-Evidence Linkage
Claims and evidence are structurally separated to ensure interpretations are never conflated with facts:
- `ClaimRecord`: Encodes the semantic assertion ($Subject \xrightarrow{Predicate} Object/Value$).
- `EvidenceRecord`: Contains the exact verbatim text snippet (`excerpt_reference`), character spans, and document origin.
- `EvidenceRole`: Distinguishes `PRIMARY`, `CORROBORATING`, `SECONDARY`, `CONTRADICTING`, and `DISMISSING` roles.

### 2.3 Syndication & Corroboration Lineage
When multiple publications report identical wire releases:
- Syndicated duplicates reference the canonical origin via `syndication_original_url`.
- Independent corroboration counts are only incremented when evidence originates from distinct, non-syndicated primary/secondary publishers.

---

## 3. Retrieval Contract Traceability

When Agent 2 or Agent 3 queries the Knowledge Platform, the `RetrievalResultContract` encapsulates complete lineage metadata:

```json
{
  "query_id": "RETRIEVE_BBCA_2026-09-29",
  "as_of": "2026-09-29T14:57:33Z",
  "data": { ... },
  "source_refs": ["SRC_YAHOO_FINANCE"],
  "evidence_refs": ["EV_8CEC9EEBA273"],
  "entity_refs": ["ENT_BBCA", "ENT_DJARUM_GROUP"],
  "relationship_refs": ["REL_DJARUM_BBCA_OWNS"],
  "temporal_status": "VALID",
  "provenance_status": "VERIFIED",
  "access_status": "AUTHORIZED",
  "origin_class": "NATURAL",
  "semantic_status": "VALID",
  "path_mode": "FAST_PATH",
  "execution_time_ms": 9.483
}
```

---

## 4. Audit & Forensic Replay

1. **Forward Trace**: Starting from any `raw_document_id`, the system can enumerate all derived entities, claims, relationships, and decisions influenced by that capture.
2. **Reverse Trace**: Starting from any Agent 3 `DecisionResult`, the system can trace backward through `evidence_refs` to the exact lines and byte hashes of the source documents.

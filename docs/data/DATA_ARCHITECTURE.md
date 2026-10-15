# SwingDeck Knowledge Data Platform — Data Architecture V1

## 1. Architectural Philosophy
The SwingDeck Knowledge Data Platform operates under the core principle:
> **STORE ONCE → NORMALIZE CORRECTLY → RELATE CORRECTLY → PROVENANCE EVERYTHING → PRESERVE TIME → RETRIEVE FAST → NEVER INVENT**

## 2. Layered Data Platform Architecture

```text
DATA PLATFORM LAYERS
│
├── 1. RAW LAYER (Immutable, SHA-256 Fingerprinted)
│   ├── raw_documents (Source documents, raw payloads)
│   └── raw_market_files (Parquet/CSV raw ticks)
│
├── 2. SOURCE REGISTRY (Authoritative Publisher Registry)
│   └── sources (Regulator, Exchange, Government, News, Filing)
│
├── 3. CORE ENTITY MASTER (Deterministic Identity & Layered Resolution)
│   ├── entities (Canonical entity master)
│   ├── entity_aliases (Common names, historical names)
│   └── entity_identifiers (IDX ticker, ISIN, LEI, Registration)
│
├── 4. INFORMATION & EVIDENCE (Traceable Facts & Claims)
│   ├── information_items (Canonical information objects)
│   ├── claims (Subject-predicate-object claim statements)
│   └── evidence (Document excerpts, hashes, access classes)
│
├── 5. RELATIONSHIPS & PROVENANCE (Directed Semantic Graph)
│   ├── entity_relationships (Typed directional edges)
│   └── relationship_evidence (Evidence linkage role)
│
├── 6. MARKET & CORPORATE ACTIONS (Market Context)
│   ├── corporate_actions (IPO, Spinoff, PUPS, Rights Issue)
│   └── market_reactions (Observational non-causal returns)
│
├── 7. POLICY & ECONOMIC CHANNELS (Transmission Chains)
│   ├── policies (Regulations, laws, decrees)
│   └── economic_channels (22 structural transmission channels)
│
├── 8. INTELLIGENCE & CONTRADICTIONS (Explanatory Hypotheses)
│   ├── exposures (Direct, indirect, second-order)
│   ├── mechanisms (Explanatory channel hypotheses)
│   └── contradictions (8 contradiction categories)
│
└── 9. DERIVED RETRIEVAL & AUDIT (Fast Path Materialization)
    ├── derived_entity_neighborhood (1-hop / 2-hop graph index)
    ├── derived_entity_exposure_index (Precomputed exposure index)
    └── platform_audit_log (Data quality audit logs)
```

## 3. Data Authority Matrix

| Data Class | Authoritative Canonical Store | Derived / Read-Only Layer |
| :--- | :--- | :--- |
| **Raw Documents** | `raw_documents` (DuckDB / Filesystem) | N/A (Immutable) |
| **Entities & Identifiers** | `entities`, `entity_identifiers` | `derived_entity_neighborhood` |
| **Relationships** | `entity_relationships`, `relationship_evidence`| `derived_entity_neighborhood` |
| **Information & Evidence** | `information_items`, `evidence` | Information search index |
| **Exposures & Mechanisms** | `exposures`, `mechanisms` | `derived_entity_exposure_index` |
| **Agent 2 Intelligence** | Agent 2 Output / Trace | Non-canonical (Derived reasoning) |
| **Agent 3 Decision** | Decision Ledger / Audit Trace | Immutable decision record |
| **Dashboard Views** | Read-Only Queries | Derived visualization (Never canonical) |

## 4. Governance & Firewall Invariants
1. **Access Control:** `MNPI` and `RESTRICTED` data are hard-blocked from trading decision pathways.
2. **Temporal Invariance:** $published\_at \le available\_at \le decision\_time$.
3. **Non-Causality:** Market reactions and graph mechanisms are observational explanatory structures, not empirical alpha or proof of causality.

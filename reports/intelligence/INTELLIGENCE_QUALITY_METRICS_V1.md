# SWINGDECK — INTELLIGENCE QUALITY METRICS SPECIFICATION V1.0 (RECONCILED)

## 1. GOVERNANCE & METRIC PHILOSOPHY

```text
COMPOSITE_QUALITY_SCORE = FORBIDDEN
DESCRIPTIVE_METRICS_ONLY = TRUE
COHORT_ID_REQUIRED = TRUE
NUMERATOR_DENOMINATOR_REQUIRED = TRUE
NEVER_INVENT = TRUE
UNKNOWN_PRESERVED = TRUE
```

In compliance with SwingDeck Scientific Governance and the **Gate 7.1 Metric Integrity Directive**, this specification defines **descriptive, multidimensional metrics only**. No single composite "Quality Score" or "Confidence Index" is permitted. Every metric is explicitly tied to a defined observation cohort with unambiguous numerators, denominators, and units.

---

## 2. CANONICAL OBSERVATION COHORT SPECIFICATION

All production metrics are computed against the following verified cohort:

```text
COHORT_ID: COHORT_GATE7_CANONICAL_V1
DATE_RANGE: 2024-03-15 08:00:00 to 2024-09-13 08:45:00
TOTAL_DOCUMENTS (N_DOCUMENTS): 6
TOTAL_INFORMATION_ITEMS (N_ITEMS): 6
UNIQUE_REAL_WORLD_EVENTS: 3
UNIQUE_SOURCES: 5
SOURCE_CLASSES: 6 (PRIMARY_ISSUER, PRIMARY_REGULATOR, GOVERNMENT_POLICY, SECONDARY_MEDIA, SYNDICATED_WIRE, REVISED_DOCUMENT)
INDEPENDENT_INFORMATION_LINEAGES: 3
```

---

## 3. CORE DIMENSIONAL QUALITY METRICS (RECONCILED)

Evaluated via [`core/intelligence_quality_metrics.py`](file:///d:/Project/SwingDeck/core/intelligence_quality_metrics.py):

### Dimension 1: Source Authenticity & Lineage
| Metric Name | Value | Numerator | Denominator | Unit | Description & Formula |
|---|---|---|---|---|---|
| `SOURCE_AUTHENTICITY_RATE` | **100.00%** | 6 | 6 | `%` | Proportion of observations with verified publisher authority class |
| `SOURCE_AUTHORITY_RATE` | **50.00%** | 3 | 6 | `%` | Proportion from statutory / primary authority classes (Class A, B, C) |
| `PROVENANCE_VERIFICATION_RATE` | **100.00%** | 6 | 6 | `%` | Items with verified cryptographic raw sha256 hash and known source ID |
| `PROVENANCE_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Items with complete cryptographic source $\rightarrow$ doc hash lineage |
| `SOURCE_METADATA_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Observations containing valid URL, raw hash, and doc ID |

> [!NOTE]
> `SOURCE_AUTHENTICITY` measures publisher verification. It does NOT assert or guarantee `CLAIM_SUPPORT` or `CLAIM_TRUTH` for forward-looking corporate statements.

### Dimension 2: Temporal & Point-In-Time (PIT) Precision
| Metric Name | Value | Numerator | Denominator | Unit | Description & Formula |
|---|---|---|---|---|---|
| `EVENT_TIME_COMPLETENESS` | **66.67%** | 4 | 6 | `%` | Presence of explicit real-world event occurrence timestamp (2 items preserved as `None`) |
| `PUBLICATION_TIME_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Presence of verified publication timestamp |
| `AVAILABILITY_TIME_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Presence of verified market availability timestamp |
| `OBSERVED_TIME_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Presence of system ingestion timestamp |
| `MARKET_PIT_RATE` | **100.00%** | 6 | 6 | `%` | Items satisfying $\text{available\_at} \le T_{\text{decision}}$ |
| `SYSTEM_PIT_RATE` | **100.00%** | 6 | 6 | `%` | Items satisfying $\text{observed\_at} \le T_{\text{decision}}$ |
| `PIT_VIOLATION_RATE` | **0.00%** | 0 | 6 | `%` | Rate of lookahead leaks in historical queries |

#### Timestamp Derivation Distribution
- `EXCHANGE_METADATA`: **33.33%** (2 / 6)
- `SOURCE_ARTICLE_METADATA`: **50.00%** (3 / 6)
- `STRUCTURED_FEED`: **16.67%** (1 / 6)
- `RETRIEVAL_CLOCK_FALLBACK`: **0.00%** (0 / 6)

#### Temporal Precision Distribution
- `EXACT`: **100.00%** (6 / 6)
- `DERIVED`: **0.00%** (0 / 6)
- `FALLBACK`: **0.00%** (0 / 6)
- `UNKNOWN`: **0.00%** (0 / 6)

### Dimension 3: Entity Resolution & Ambiguity
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `ENTITY_RESOLUTION_RATE` | **100.00%** | 6 | 6 | `%` | Clean exact resolution against canonical entity ground truth |
| `ENTITY_AMBIGUITY_RATE` | **0.00%** | 0 | 6 | `%` | Rate of ambiguous candidate matches in canonical set |
| `UNKNOWN_ENTITY_RATE` | **0.00%** | 0 | 6 | `%` | Rate of unresolvable entity queries |

### Dimension 4: Information Novelty & State Changes
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `UNKNOWN_NOVELTY_RATE` | **0.00%** | 0 | 6 | `%` | Rate of unclassified novelty items |
| `REVISION_RATE` | **16.67%** | 1 | 6 | `%` | Rate of documents modifying prior filings (Errata/Revisions) |
| `CANONICAL_COHORT_CONTRADICTION_RATE` | **0.00%** | 0 | 6 | `%` | Rate of conflicting factual claims in canonical cohort |
| `ADVERSARIAL_INJECTION_RATE` | **50.00%** | 1 | 2 | `%` | Injected contradiction pairs in isolated stress tests |
| `ADVERSARIAL_DETECTION_RATE` | **100.00%** | 2 | 2 | `%` | Contradiction detection efficiency in stress tests |

#### Novelty Class Distribution (Primary Classification — Mutually Exclusive, $\sum = 100.00\%$)
- `NEW_CATALYST`: **33.33%** (2 / 6)
- `MATERIAL_CHANGE`: **16.67%** (1 / 6)
- `STATUS_UPDATE`: **16.67%** (1 / 6)
- `SYNDICATION`: **16.67%** (1 / 6)
- `REVISION`: **16.67%** (1 / 6)
- **Sum**: **100.00%** (6 / 6)

### Dimension 5: Event Clustering & Syndication Control
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `EVENT_CLUSTER_RATE` | **100.00%** | 6 | 6 | `%` | Proportion of news mapped to canonical event clusters |
| `SYNDICATION_RATE` | **16.67%** | 1 | 6 | `%` | Proportion of documents identified as verbatim wire replication |
| `INDEPENDENT_CORROBORATION_RATE` | **83.33%** | 5 | 6 | `%` | Non-syndicated distinct source corroborations |
| `SYNDICATION_INFLATION_RATE` | **0.00%** | 0 | 6 | `%` | Syndications falsely counted as independent confirmations |

### Dimension 6: Information Delta & State Transition
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `DELTA_DETECTION_RATE` | **100.00%** | 6 | 6 | `%` | Identification of state changes vs prior world snapshot |
| `DELTA_SUPPORT_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Presence of supporting evidence for every recorded state delta |
| `STATE_TRANSITION_CONSISTENCY` | **100.00%** | 6 | 6 | `%` | Valid transition sequences without orphaned states |

### Dimension 7: Multi-Hop Exposure & Mechanism
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `EXPOSURE_PATH_VALIDITY` | **100.00%** | 6 | 6 | `%` | Traversed paths conforming to semantic ontology rules |
| `EXPOSURE_PROVENANCE_COMPLETENESS` | **100.00%** | 6 | 6 | `%` | Exposure hops backed by cryptographic evidence references |
| `UNKNOWN_EXPOSURE_RATE` | **0.00%** | 0 | 6 | `%` | Unresolved exposure classifications |

### Dimension 8: Operational Reliability & Reproducibility
| Metric Name | Value | Numerator | Denominator | Unit | Description |
|---|---|---|---|---|---|
| `INGESTION_SUCCESS_RATE` | **100.00%** | 6 | 6 | `%` | Successful raw document parsing and indexing |
| `INGESTION_FAILURE_RATE` | **0.00%** | 0 | 6 | `%` | Ingestion pipeline exceptions or schema dropouts |
| `RETRIEVAL_FAILURE_RATE` | **0.00%** | 0 | 6 | `%` | Failed retrieval queries |
| `REPRODUCIBILITY_RATE` | **100.00%** | 6 | 6 | `%` | Exact replay reproducibility from canonical DuckDB state |

---

## 4. PERFORMANCE BENCHMARK DISTRIBUTION

Benchmark results measured across 100 iterations on Windows (`.venv`, Python 3.12, DuckDB):

| Operation | N | p50 (ms) | p95 (ms) | p99 (ms) | Min (ms) | Max (ms) |
|---|---|---|---|---|---|---|
| **Entity Lookup** | 100 | **0.213** | **0.321** | **0.430** | 0.178 | 0.539 |
| **Information Lookup** | 100 | **0.420** | **0.529** | **0.665** | 0.383 | 0.666 |
| **PIT Retrieval** | 100 | **3.613** | **4.023** | **4.275** | 3.262 | 4.480 |
| **3-Hop Exposure Traversal** | 100 | **5.058** | **5.518** | **5.733** | 4.456 | 6.615 |
| **5-Hop Bounded Traversal** | 100 | **7.172** | **7.764** | **8.054** | 6.403 | 8.111 |
| **Agent 2 Context Retrieval** | 100 | **2.432** | **2.683** | **2.913** | 2.068 | 2.916 |
| **ThesisDelta Computation** | 100 | **0.405** | **0.544** | **0.605** | 0.356 | 0.736 |

---

## 5. FORMAL EQUATIONS & INVARIANTS

1. **Provenance Verification Rate:**
   $$\text{PVR} = \frac{\sum_{i=1}^N \mathbf{1}(\text{provenance\_status}_i = \text{VERIFIED} \land \text{source\_id}_i \ne \text{UNKNOWN})}{N}$$

2. **Source Authority Rate:**
   $$\text{SAR} = \frac{\sum_{i=1}^N \mathbf{1}(\text{source\_class}_i \in \{\text{PRIMARY\_ISSUER}, \text{PRIMARY\_REGULATOR}, \text{GOVERNMENT\_POLICY}\})}{N}$$

3. **Market Point-In-Time Violation Rate:**
   $$\text{PVR}_{\text{market}} = \frac{\sum_{i=1}^N \mathbf{1}(\text{retrieved\_in\_query}(i, T_{\text{decision}}) \land \text{available\_at}_i > T_{\text{decision}})}{N}$$

4. **System Point-In-Time Violation Rate:**
   $$\text{PVR}_{\text{system}} = \frac{\sum_{i=1}^N \mathbf{1}(\text{retrieved\_in\_query}(i, T_{\text{decision}}) \land \text{observed\_at}_i > T_{\text{decision}})}{N}$$

5. **Syndication Inflation Rate:**
   $$\text{SIR} = \frac{\sum_{i=1}^N \mathbf{1}(\text{is\_syndication}_i = \text{TRUE} \land \text{counted\_as\_independent}_i = \text{TRUE})}{N}$$

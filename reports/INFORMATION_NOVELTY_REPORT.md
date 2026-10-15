# SWINGDECK — INFORMATION NOVELTY & DELTA ENGINE REPORT (GATE 2)

## EXECUTIVE SUMMARY

This report documents the implementation and verification of the **Information Novelty Engine, Event Clustering, and Information Delta Framework** under Gate 2 of the Intelligence Upgrade V1.1+.

In market intelligence, `NEW_DOCUMENT` $\neq$ `NEW_INFORMATION`. A flurry of 20 media portals republishing an identical press release or wire feed must never be mistaken for 20 independent confirmations. Gate 2 equips SwingDeck with semantic novelty categorization, state-transition information delta materialization, and syndication-aware event clustering to ensure capital is allocated only on genuine real-world changes.

---

## 1. SEMANTIC NOVELTY TAXONOMY

SwingDeck categorizes every ingested information item and claim into one of nine distinct novelty classes (`NoveltyClass`):

| Novelty Class | Definition | Trading & Agent Decision Implication |
| :--- | :--- | :--- |
| **`NEW_CATALYST`** | First disclosure of an unexpected, material corporate/policy/macro catalyst. | Prime trigger for new trading setup evaluation. |
| **`STATUS_UPDATE`** | Incremental progress on a known roadmap (e.g. mining permit renewal step). | Contextual update; maintains active monitoring. |
| **`MATERIAL_CHANGE`** | Substantive revision to terms, value, or timeline of a known project or transaction. | Requires thesis re-evaluation and risk re-sizing. |
| **`NEW_IMPLICATION`** | Analytical discovery of indirect secondary exposure from known events. | Propagates multi-hop exposure to supply chain/peers. |
| **`CONFIRMATION`** | Independent third-party verification of an unconfirmed report. | Strengthens thesis confidence without moving price target. |
| **`REPETITION`** | Duplicate or near-duplicate coverage of an already known fact by the same or similar source. | Ignored in novelty scoring; suppresses noise. |
| **`SYNDICATION`** | Exact or syndicated reprint of a primary newswire/disclosure by secondary portals. | Linked to parent event; **does not inflate independent confirmation count**. |
| **`REVISION`** | Formal correction or restatement of a previously published disclosure. | Updates previous record; flags potential data revision. |
| **`CONTRADICTION`** | Direct factual or directional conflict with an existing active claim or thesis. | Triggers Red Team review and immediate thesis invalidation check. |
| **`UNKNOWN`** | Insufficient contextual history to evaluate novelty state. | Handled with epistemic humility; prevents false confidence. |

---

## 2. STATE-TRANSITION INFORMATION DELTAS

Rather than computing deltas only on-the-fly during ad-hoc queries, SwingDeck materializes explicit state-transition records (`InformationDeltaRecord` in table `information_deltas`):

```sql
CREATE TABLE IF NOT EXISTS information_deltas (
    delta_id VARCHAR PRIMARY KEY,
    entity_id VARCHAR NOT NULL,
    attribute_name VARCHAR NOT NULL,
    previous_state VARCHAR,
    new_state VARCHAR NOT NULL,
    change_time VARCHAR NOT NULL,
    available_at VARCHAR NOT NULL,
    supporting_evidence_id VARCHAR NOT NULL,
    source_refs VARCHAR DEFAULT '[]',
    created_at VARCHAR NOT NULL
);
```

### Concrete Example: Smelter Project Milestone Transition

```
  STATE BEFORE:
  attribute: smelter_commercial_status
  previous_state: "UNDER_CONSTRUCTION"
  
  REAL-WORLD DISCLOSURE:
  "Ministry grants commercial operation approval for copper smelter unit."
  
  STATE AFTER:
  attribute: smelter_commercial_status
  new_state: "APPROVED" / "COMMERCIAL_OPERATION"
  change_time: "2026-03-15T09:00:00Z"
  available_at: "2026-03-15T09:05:00Z"
  supporting_evidence_id: "EV_MEMR_SMELTER_001"
```

---

## 3. EVENT CLUSTERING & SYNDICATION NON-INFLATION

Multiple heterogeneous sources reporting on the same underlying real-world event are grouped into canonical clusters (`EventClusterRecord` in table `event_clusters`).

```
                              ┌──────────────────────────────────┐
                              │     CANONICAL EVENT CLUSTER      │
                              │    CLUST_2026_ADRO_AADI_SPIN     │
                              └─────────────────┬────────────────┘
                                                │
         ┌────────────────────────┬─────────────┴────────────┬────────────────────────┐
         ▼                        ▼                          ▼                        ▼
  ISSUER FILING             EXCHANGE NOTICE            MEDIA REPORT             PORTAL SYNDICATION
  (Primary Source)          (Regulatory Notice)        (Secondary Report)       (Syndicated Copy)
  • Source: IDX             • Source: BEI              • Source: Bisnis.com     • Source: Portal XYZ
  • Corrob: INDEPENDENT     • Corrob: INDEPENDENT      • Corrob: DERIVED_REPORT • Corrob: SYNDICATION
  • Novelty: NEW_CATALYST   • Novelty: CONFIRMATION    • Novelty: STATUS_UPDATE • Novelty: SYNDICATION
```

### Mathematical Invariant: Syndication Non-Inflation
$$\text{Independent Confirmations} = \sum_{e \in \text{Cluster}} \mathbb{I}(\text{CorroborationType}(e) = \text{INDEPENDENT\_CORROBORATION})$$

Syndicated reprints ($\text{CorroborationType} = \text{SYNDICATED\_REPETITION}$) have weight $0$ toward independent corroboration counts.

---

## 4. EPISTEMIC SOURCE TRUTH DIFFERENTIATION

SwingDeck strictly separates distinct epistemic dimensions rather than collapsing them into a single opaque "confidence score":

1. **`SOURCE_AUTHENTICITY`**: Is the publisher legitimate, official, or verified?
2. **`PROVENANCE_INTEGRITY`**: Can the content hash and retrieval chain be traced without tampering?
3. **`CLAIM_SUPPORT`**: Does the raw text excerpt directly entail the structured claim?
4. **`CLAIM_TRUTH`**: Has the real-world occurrence been independently verified?
5. **`RELEVANCE`**: Does this claim impact the target security or sector?
6. **`NOVELTY`**: Is this fact genuinely new to the market at the decision timestamp?

---

## 5. TEST VERIFICATION EVIDENCE

Verified in `tests/test_intelligence_upgrade_v11.py` and `tests/test_natural_information_ingestion.py`:
- `test_gate2_semantic_novelty_and_delta_materialization`: Verified 9 novelty classes and state-transition delta materialization.
- `test_gate2_event_clustering_and_syndication_non_inflation`: Proved that syndicated articles do not inflate independent confirmation counts.
- `test_adversarial_semantic_deduplication`: Verified robustness against cosmetic text mutations.

**Status: CERTIFIED & COMPLIANT**

# ADAPTIVE HISTORICAL DATA & RESEARCH FOUNDATION (BATCH ZZZ.13)

**Document ID:** `DOC-ADAPTIVE-FOUNDATION-ZZZ13`  
**Architecture Version:** `ADAPTIVE_FOUNDATION_V2_20260915`  
**Governance Hierarchy:** 4-Layer Controlled Evolution  
**Baseline Immutability State:** `METHODOLOGY_V1` / `DATASET_V1` / `RESULT_V1` FROZEN  
**Effective Date:** September 15, 2026  
**Governance Authority:** 3-Agent Architecture (Agent 1: Quant, Agent 2: Market Intelligence & Red Team, Agent 3: Investment Committee & Risk — Audit Only). Zero Agent 4.

---

## 1. Executive Philosophy: Freeze the Baseline — Allow Controlled Evolution

Batch ZZZ.12 successfully codified the **Research Methodology Lock** for the baseline dataset. However, locking the baseline **does not mean locking the project against new knowledge, data, or scientific progress**.

> **The Core Invariant:**  
> **FREEZE THE BASELINE — ALLOW CONTROLLED EVOLUTION.**  
> SwingDeck must continuously absorb new historical data, disclosures, corporate relationships, commodity exposures, macro variables, and statistical methods without mutating historical research baselines or violating Point-in-Time (PIT) integrity, scientific discipline, and historical comparability.

---

## 2. Four-Layer Governance Architecture

To ensure clean separation between frozen baselines, data extensions, sandboxed experiments, and promoted methodologies, SwingDeck enforces a strict **4-Layer Governance Architecture**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: FROZEN BASELINE (Immutable)                                   │
│ • METHODOLOGY_V1_FROZEN_20260915                                       │
│ • DATASET_V1_CANONICAL_FROZEN (N=73, 12 Tickers)                       │
│ • Canonical Results (C0 = +3.10 pp, C5 = +2.98 pp, Level 2)            │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│ LAYER 2: EXTENSION (Additive Knowledge & Historical Data)              │
│ • Multi-Year Data Ingestion (2016–2026)                                │
│ • Expanded Ticker Universes (IDX80 / LQ45)                             │
│ • New Entity Mappings & Temporal Relationships                         │
│ • New Commodity Exposures & Corporate Actions                          │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼─────────────────────────────────────┐
│ LAYER 3: EXPERIMENT (Sandboxed Research Branches)                      │
│ • New Research Hypotheses & Counterfactual Models                      │
│ • Novel Statistical Variance Estimators & Controls                     │
│ • Sub-Sector Stratification & Regime Models                            │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ (10-Point Promotion Gate)
┌──────────────────────────────────▼─────────────────────────────────────┐
│ LAYER 4: PROMOTION (Formal Version Evolution)                          │
│ • CANDIDATE ──► UNDER_TESTING ──► VALIDATED ──► PROMOTED               │
│ • Generates METHODOLOGY_V2 (Preserves V1 in Lineage Ledger)            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. New Criteria Intake & Six-Type Classification

Any newly discovered data stream, qualitative event category, or analytical tool is submitted via a formal `CriterionProposal`. The engine evaluates and classifies it into exactly one of **Six Types**:

### Type A: Data Extension
* *Examples:* Adding historical years (e.g. 2016–2023), new liquid tickers, additional exchange disclosure categories.
* *Governance:* Methodology remains unchanged; evaluated via the Replication-First protocol on Dataset V2.

### Type B: Data Quality Improvement
* *Examples:* Timestamp corrections, entity mapping refinements, duplicate elimination, source provenance verification.
* *Governance:* Never overwrites Dataset V1; generates a corrected dataset version (e.g. `DATASET_V1.1`).

### Type C: Information Extension
* *Examples:* Political linkages, supply chain dependencies, detailed segment revenue exposure, controller ownership changes.
* *Governance:* Ingested into the DuckDB relational graph with temporal validity bounds (`valid_from`, `valid_to`).

### Type D: Analytical Extension
* *Examples:* Novel control variables, alternative counterfactual estimators, high-dimensional fixed effects, machine learning propensity models.
* *Governance:* Quarantined within Layer 3 sandboxed research branches.

### Type E: Methodology Change
* *Examples:* Changing the primary endpoint, redefining contextual peer networks, altering evidence taxonomies, modifying causality levels.
* *Governance:* Requires generating a distinct `METHODOLOGY_V2` specification; historical V1 remains immutable.

### Type F: Strategy Change
* *Examples:* Modifying Layer E quantitative thresholds, adjusting breakout entry/exit rules, altering risk limits or position sizing.
* *Governance:* Strictly quarantined to downstream strategy research; prohibited from historical data expansion.

---

## 4. Five-Tier Backward Compatibility Assessment

Every intake proposal receives a formal **Backward Compatibility Status**:

| Status | Meaning | Action & Isolation Rule |
| :--- | :--- | :--- |
| **`COMPATIBLE`** | 100% compatible with Methodology V1 | Ingest directly into Dataset V2 extension layer |
| **`EXTENSION_ONLY`** | Additive information leaving V1 untouched | Add to DuckDB relational intelligence graph |
| **`EXPERIMENTAL`** | Novel analytical or econometric method | Sandbox in dedicated research experiment branch |
| **`METHODOLOGY_CHANGING`** | Modifies core research definitions | Mandates new methodology version (`METHODOLOGY_V2`) |
| **`STRATEGY_CHANGING`** | Changes trading/execution rules | Isolate in downstream execution strategy module |

> **No "Methodology Prison":** The system never rejects a promising criterion simply because it was not in `METHODOLOGY_V1`. It registers, classifies, tests, and promotes it when justified.

---

## 5. Schema & Taxonomy Evolution Protocols

### 5.1 Additive Schema Evolution
Schema evolution is strictly additive:
* New fields are registered in `FieldLineage` with `schema_version`, `introduced_at_batch`, and `fallback_value`.
* Historical fields are **never silently deleted**; if retired, they are marked `is_deprecated = True` with `deprecated_at_batch`.

### 5.2 Taxonomy Domain Expansion
Taxonomies can expand into new operational domains (e.g. `SUPPLY_CHAIN`, `TECHNOLOGY`, `REGULATORY_EXPOSURE`) without retroactively rewriting historical V1 records. Historical observations retain their original classification.

---

## 6. Temporal Knowledge Graph & Relationship Architecture

All relational entities, ownership links, and exposure chains must enforce Point-in-Time (PIT) validity:
$$\text{Relationship} = \{\text{Entity}_A, \text{Entity}_B, \text{Type}, \text{valid\_from}, \text{valid\_to}, \text{observed\_at}, \text{source}, \text{confidence}, \text{PIT\_status}, \text{provenance\_hash}\}$$

* Invariant: `valid_from <= valid_to`.
* Invariant: Queries at time $T$ must enforce `valid_from <= T` and `publication_time <= T`.
* Knowledge accumulation preserves past states: $\text{Current Knowledge} + \text{New Evidence} = \text{Updated Knowledge}$, but past records are never overwritten.

---

## 7. Epistemological Integrity: Preservation of UNKNOWN

Data expansion must never artificially eliminate genuine uncertainty:
$$\text{NO\_EVIDENCE\_IN\_DATASET} \neq \text{VERIFIED\_NO\_EVENT} \neq \text{QUIET\_TRADING\_DAY}$$
* If a new ticker or historical window lacks verified primary filings, it must remain `NO_EVIDENCE_IN_DATASET`.
* Coercing `UNKNOWN` $\rightarrow$ `EVIDENCE_PRESENT` to create an illusion of high coverage is strictly prohibited.

---

## 8. Research Branching & Lineage Tree

SwingDeck manages multi-track research via an immutable branching tree:

```text
METHODOLOGY_V1_FROZEN (Root)
       │
       ├── DATASET_V1 (Canonical N=73 Baseline)
       │
       ├── DATASET_V2 (Multi-Year Ingestion Branch — Replication-First Verified)
       │
       ├── EXPERIMENT_BRANCH_A (Alternative Econometric Counterfactuals)
       │
       └── METHODOLOGY_V2 (Formal Promoted Version across Multi-Year Universes)
```

---

## 9. Ten-Point Promotion Gate Protocol

A criterion or method is promoted from Extension/Experiment to a formal new Methodology Version only when meeting **all 10 institutional criteria**:

1. **Clear Definition:** Mathematical and conceptual specifications unambiguously defined.
2. **Verifiable Source:** Backed by authentic primary exchange, regulatory, or corporate IR sources.
3. **PIT Compliance:** Strict `publication_time <= AS_OF` enforcement without lookahead leakage.
4. **Complete Provenance:** Cryptographic SHA-256 raw file hashing and source tier tagging.
5. **Adequate Entity Resolution:** Mapped unambiguously to canonical ticker/entity identifiers.
6. **Zero Lookahead Leakage:** Passes $T+1, T+2, T+5$ multi-horizon injection tests ($0$ leaks).
7. **Non-Trivial & Non-Redundant:** Adds incremental orthogonal information beyond existing features.
8. **Clear Use Case:** Explicitly mapped to an economic hypothesis or governance risk control.
9. **Appropriately Tested:** Validated across out-of-sample or multi-cycle historical periods.
10. **Red Team Certification:** Passes exhaustive 20-dimension Red Team anti-drift audit.

---

## 10. Scientific Failure as a Valid Research Output

If Dataset V2 reveals that an empirical association from V1 attenuates, disappears, or reverses:
* The result is recorded as **`HYPOTHESIS_REVISED`** or **`ASSOCIATION_ATTENUATED`**.
* The dataset is **never rejected or filtered** to rescue the old hypothesis.
* SwingDeck values scientific truth and process discipline over artificial narrative preservation.

---

## 11. Final Certification

```text
================================================================================
ADAPTIVE FOUNDATION STATUS:    CERTIFIED ACTIVE
GOVERNANCE MODEL:              4-LAYER CONTROLLED EVOLUTION
INTAKE CLASSIFICATION:         6-TYPE SYSTEM (A through F)
COMPATIBILITY HIERARCHY:       5-TIER BACKWARD COMPATIBILITY
PROMOTION GATE:                10-POINT INSTITUTIONAL PROTOCOL
BASELINE IMMUTABILITY:         METHODOLOGY_V1 & DATASET_V1 FULLY PROTECTED
================================================================================
```

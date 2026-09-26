# RESEARCH METHODOLOGY LOCK & GOVERNANCE SPECIFICATION (ZZZ.12)

**Document ID:** `DOC-METHODOLOGY-LOCK-ZZZ12`  
**Methodology Version:** `METHODOLOGY_V1_FROZEN_20260915`  
**Baseline Dataset Version:** `DATASET_V1_CANONICAL_FROZEN`  
**Baseline Snapshot ID:** `SNAPSHOT_ZZZ117_687970d0e904`  
**Canonical Sample Hash:** `SAMPLE_ZZZ117_HASH_f03310068fd3`  
**Effective Date:** September 15, 2026  
**Governance Authority:** 3-Agent Architecture (Agent 1: Quant, Agent 2: Market Intelligence & Red Team, Agent 3: Investment Committee & Risk — Audit Only). Zero Agent 4.

---

## 1. Executive Purpose & Governance Mandate

This document serves as the **Single Canonical Source of Truth** for SwingDeck research methodology prior to material historical data expansion (Dataset V2). 

> **Core Mandate:**  
> To guarantee that any observed change in empirical findings following historical data expansion is strictly attributable to **data addition**, and never to silent changes in research questions, endpoint definitions, peer construction, counterfactual hierarchies, evidence taxonomies, causality levels, missingness treatment, or governance boundaries.

Once locked under Batch ZZZ.12, **zero silent modifications** are permitted.

---

## 2. Primary Research Question

The research question of the SwingDeck information intelligence framework is frozen as:

> **"Does company-specific historical information provide incremental discriminatory information about subsequent relative performance after accounting for market, peer, exposure, time, and known confounding structures?"**

**Prohibited Drift:**
* MUST NOT be converted to: *"Is this strategy profitable?"*
* MUST NOT be converted to: *"How can we maximize Sharpe ratio or win rate?"*
* Directional alpha discovery and strategy optimization remain strictly isolated downstream stages.

---

## 3. Unit of Analysis

The atomic unit of observation is frozen as:
$$\text{Observation} = \text{Company } (i) \times \text{Decision Date } (t)$$

Each observation record MUST contain:
1. `entity`: Canonical ticker symbol.
2. `decision_date`: Trading calendar date $T$.
3. `decision_time`: Exchange market close timestamp (16:00:00 WIB).
4. `evidence_state`: Verified Point-in-Time disclosure state at $T$.
5. `peer_state`: Contextual peer exposure group membership at $T$.
6. `exposure_state`: Deterministic economic/commodity exposure profile at $T$.
7. `target_return`: Realized forward holding return ($H_1, H_3, H_5, H_{10}, H_{20}$).
8. `counterfactual`: Leave-one-out and purified peer benchmark returns.
9. `provenance`: Cryptographic raw artifact hash (SHA-256) and source tier.
10. `dataset_version`: Explicit dataset snapshot identifier.

> **Invariant:** $\text{Observation} \neq \text{Event}$. A single corporate event spanning multiple rolling decision dates retains its distinct `event_id` and must be evaluated with cluster-robust variance estimators.

---

## 4. Endpoints Specification

### 4.1 Primary Endpoint
The **Primary Endpoint** is strictly locked as:
$$\mathbf{H_5 \text{ PEER-EXCESS DIFFERENTIAL}} = \mathbb{E}[\text{Excess}_{i,t}(H_5) \mid \text{Evidence Present}] - \mathbb{E}[\text{Excess}_{i,t}(H_5) \mid \text{Unobserved}]$$
where:
$$\text{Excess}_{i,t}(H_5) = R_{i, [t, t+5]} - \frac{1}{|P_{i,t}|} \sum_{j \in P_{i,t}, j \neq i} R_{j, [t, t+5]}$$

*Target company $i$ is NEVER included in its own benchmark calculation.*

### 4.2 Secondary Endpoints
Secondary endpoints are strictly exploratory and must not replace the primary endpoint:
* Returns: $H_1, H_3, H_{10}, H_{20}$.
* Path-dependent metrics: Maximum Favorable Excursion (MFE), Maximum Adverse Excursion (MAE).

---

## 5. Counterfactual Hierarchy (C0 to C5)

To maintain rigorous comparability without obscuring sensitivity, research runs must report across the 6-tier hierarchy:

| Tier | Name | Description | Role |
| :--- | :--- | :--- | :--- |
| **C0** | **Canonical LOO** | Original Leave-One-Out peer mean benchmark | Historical Baseline |
| **C1** | **LOO Validation** | Exact algebraic replication of LOO benchmark | Algorithmic Check |
| **C2** | **Evidence-Excluded** | Excludes peers with co-occurring Evidence on date $t$ | Diagnostic Sensitivity |
| **C3** | **Event-Purified** | Excludes peers exposed to identical corporate event ID | Diagnostic Sensitivity |
| **C4** | **Date-Purified** | Excludes peers active on date $t$ | Diagnostic Sensitivity |
| **C5** | **Fully Purified** | Joint exclusion of same-date, same-event, and Evidence peers | Purified Benchmark |

*Rule of Non-Fabrication: If clean peer count $|P_{i,t}^{\text{clean}}| = 0$, the observation is marked `NOT_ESTIMABLE`. No single-stock artificial benchmarks are permitted.*

---

## 6. Peer Group Construction Rules

1. **Outcome-Blind:** Peer membership must be established strictly using information available at or before decision time $T$.
2. **Zero Hindsight:** Forward price movements, future disclosures, or post-hoc sector classifications are strictly forbidden.
3. **Contextual Exposure Groups (Pilot Universe):**
   * `COAL_PRODUCER`: `ADRO`, `PTBA`, `ITMG`
   * `NICKEL_MINING`: `ANTM`, `INCO`
   * `HEAVY_EQUIPMENT`: `UNTR`, `ASII`
   * `BANKING_TIER1`: `BBCA`, `BBRI`, `BMRI`, `BBNI`
   * `TELECOMMUNICATION`: `TLKM`

---

## 7. Evidence & Information-State Taxonomy

All historical information records must map into exactly one canonical state:

| State | Definition | Governance Rule |
| :--- | :--- | :--- |
| `EVIDENCE_PRESENT` | Verified primary/secondary disclosure published at $\le T$ | Valid treatment stratum |
| `EVIDENCE_CONTRADICTORY` | Material contradictions detected across news/filings | Flagged for Red Team review |
| `EVIDENCE_PIT_UNCERTAIN` | Ambiguous publication or retrieval timestamp | Quarantined from treatment |
| `ENTITY_UNRESOLVED` | Ambiguous company/entity resolution | Quarantined from treatment |
| `NO_EVIDENCE_IN_DATASET` | Unobserved disclosure record in current database | **Unobserved stratum (NOT negative control)** |
| `VERIFIED_NO_EVENT` | Certified exhaustive absence across all official registries | Requires certified negative proof |

> **Critical Epistemological Invariant:**  
> $$\text{NO\_EVIDENCE\_IN\_DATASET} \neq \text{VERIFIED\_NO\_EVENT} \neq \text{QUIET\_TRADING\_DAY}$$

---

## 8. Causality & Attribution Hierarchies

### 8.1 Causality Levels
1. `OBSERVED`: Statistical pattern observed in historical sample.
2. `CORRELATED`: Association survives bivariate linear controls.
3. `ECONOMICALLY_PLAUSIBLE`: Supported by verified business/commodity transmission.
4. `HYPOTHESIZED`: Formal testable hypothesis registered in `fact_hypothesis`.
5. `EXPERIMENTALLY_TESTED`: Out-of-sample or falsification tests executed.
6. `VALIDATED`: Certified across multi-cycle out-of-sample data.

$$\text{OBSERVED} \neq \text{CORRELATED} \neq \text{CAUSAL} \neq \text{ALPHA}$$

### 8.2 Attribution Taxonomy
Attribution must decompose returns into:
* `MARKET_COMPONENT`
* `SECTOR_COMPONENT`
* `FACTOR_COMPONENT`
* `MACRO_COMPONENT`
* `COMMODITY_COMPONENT`
* `FLOW_COMPONENT`
* `NEWS_COMPONENT`
* `OWNERSHIP_COMPONENT`
* `RELATIONSHIP_COMPONENT`
* `COMPANY_SPECIFIC_COMPONENT`
* `UNKNOWN_COMPONENT` (Mandatory default when evidence is insufficient)

---

## 9. Exposure & Relationship Standards

### 9.1 Exposure Standard
Every exposure record must specify:
* `exposure_level`: `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`.
* `exposure_basis`: `revenue`, `cost`, `asset`, `debt`, `subsidiary`, `project`, `permit`, `contract`, `region`, `business_model`, `other`.
* `temporal_bounds`: `valid_from`, `valid_to`, `observed_at`, `PIT_status`.

### 9.2 Relationship Standard
Every relationship record must specify:
* `relationship_type`: `shareholder`, `controller`, `beneficial_owner`, `affiliate`, `subsidiary`, `parent`, `related_party`, `ownership_change`.
* `provenance`: `source`, `confidence`, `PIT_status`, raw SHA-256 hash.
* *Relationship $\neq$ Causality.*

---

## 10. Temporal Safety & Historical Immutability Principle

$$\text{CURRENT KNOWLEDGE} + \text{NEW EVIDENCE} = \text{UPDATED KNOWLEDGE}$$
$$\text{UPDATED KNOWLEDGE} \neq \text{OVERWRITE HISTORICAL STATE}$$

1. **Strict PIT Boundary:** All queries must enforce `valid_from <= AS_OF` and `publication_time <= AS_OF`.
2. **Hindsight Prevention:** Future corporate actions, earnings surprises, or price paths must never backfill into decision time $T$.
3. **Historical Immutability:** Research results for Batch ZZZ.11.7 under Dataset V1 remain immutable. Future Dataset V2 produces distinct research versions (`V1 \rightarrow V2`), never silent overwrites.

---

## 11. Data Versioning & Cryptographic Manifest Standards

Every research run MUST record:
* `dataset_version`: e.g. `DATASET_V1_CANONICAL_FROZEN`
* `snapshot_id`: Cryptographic identifier (e.g. `SNAPSHOT_ZZZ117_687970d0e904`)
* `dataset_manifest_hash`: SHA-256 hash of data files manifest
* `sample_hash`: SHA-256 hash of observation array (`SAMPLE_ZZZ117_HASH_f03310068fd3`)
* `code_version` & `code_hash`
* `config_version` & `config_hash`
* `schema_version` & `schema_hash`
* `execution_timestamp` (UTC ISO-8601)
* `random_seed`: Deterministic integer seed.

---

## 12. Change Control Governance & Change Classification

Any post-lock modification must be classified under the 4-Class System:

### Class A: Data Addition
* *Scope:* Ingestion of additional years, disclosures, news, or tickers without changing definitions.
* *Governance:* Permitted after Replication-First certification.

### Class B: Data Correction
* *Scope:* Fixing entity linkage errors, correcting faulty timestamps, removing corrupted duplicates.
* *Governance:* Requires corrected dataset version (e.g. `DATASET_V1.1`) and lineage changelog.

### Class C: Methodology Change
* *Scope:* Modifying endpoints, peer definitions, exposure groupings, or taxonomies.
* *Governance:* Requires new methodology version (`METHODOLOGY_V2`) and separate research run.

### Class D: Strategy / Execution Change
* *Scope:* Modifying Layer E thresholds, entry/exit rules, risk gates, position sizing.
* *Governance:* **STRICTLY PROHIBITED** during historical data expansion.

---

## 13. Historical Expansion Gate & Replication-First Protocol

### 13.1 Gate Criteria
Dataset V2 is authorized for ingestion only when:
1. `METHODOLOGY_LOCK = TRUE`.
2. All 15+ deterministic lock tests pass.
3. 20-dimension Red Team audit certifies zero governance violations.

### 13.2 Replication-First Protocol
Before any expanded research is executed on Dataset V2:
1. Extract the exact V1 subset ($N=73$, 12 tickers, 2024–2026).
2. Execute canonical baseline replication.
3. Verify: $\Delta_{C0} = +3.10\text{ pp} \pm 0.0001\text{ pp}$.
4. If replication fails $\implies$ **STOP. Reject Dataset V2.**

---

## 14. Multiple Testing & Exploratory vs Confirmatory Policy

* **Confirmatory Tests:** Pre-specified primary endpoint ($H_5$ Peer-Excess Differential) and C0/C5 benchmarks.
* **Exploratory Tests:** Sub-group analyses, horizon scans ($H_1, H_{20}$), machine learning features, textual sentiment.
* All exploratory findings must be explicitly labeled `EXPLORATORY` and cannot be upgraded to `CONFIRMATORY` post-hoc.

---

## 15. Clustering, Pre-Trend, and Placebo Policies

1. **Clustered Inference:** Variance estimation must report cluster-robust sandwich errors across Date, Exposure, and Ticker clusters.
2. **Pre-Trend Reporting:** Information research must report pre-event trajectories ($H[-10,-5], H[-5,-1]$). Strong pre-trends mandate classification as `CONFIRMATION_MARKER`, not exogenous shock.
3. **Outcome-Blind Placebos:** Placebo dates must be drawn blind to future returns. If placebo excess approaches treatment excess, identification is marked `WEAKENED`.

---

## 16. Source Authenticity vs File Integrity

$$\text{SHA-256 FILE INTEGRITY} \neq \text{SOURCE AUTHENTICITY} \neq \text{ARCHIVE COMPLETENESS}$$
* A valid cryptographic hash proves uncorrupted byte transmission.
* Verifying source authenticity requires proving document origin, official issuer domain, issuance timestamps, and cross-source corroboration.

---

## 17. Final Methodology Lock Certification

```text
================================================================================
METHODOLOGY LOCK STATUS:       LOCKED (TRUE)
METHODOLOGY VERSION:           METHODOLOGY_V1_FROZEN_20260915
HISTORICAL EXPANSION GATE:     OPEN
ACTIVE CHANGE CONTROL:         4-CLASS SYSTEM (A, B, C, D)
BASELINE DATASET:              DATASET_V1_CANONICAL_FROZEN (N=73)
PRIMARY ENDPOINT:              H5 PEER-EXCESS DIFFERENTIAL (+3.10 pp / +2.98 pp)
IDENTIFICATION LEVEL:          LEVEL 2 (Confirmation Marker)
CAUSAL ALPHA STATUS:           NOT_ESTABLISHED
================================================================================
```

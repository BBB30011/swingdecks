# BATCH ZZZ.12 — RESEARCH METHODOLOGY LOCK & HISTORICAL EXPANSION GATE

**Batch ID:** `BATCH-ZZZ.12`  
**Date:** September 15, 2026  
**Evaluator:** Agent 1 (Quant & Market Scanner), Agent 2 (Market Intelligence & Red Team), Agent 3 (Investment Committee & Risk — Audit Only)  
**Governance State:** 3-AGENT GOVERNANCE LOCKED (Zero Agent 4)  
**Methodology Version:** `METHODOLOGY_V1_FROZEN_20260915`  
**Baseline Dataset Version:** `DATASET_V1_CANONICAL_FROZEN`  
**Baseline Snapshot ID:** `SNAPSHOT_ZZZ117_687970d0e904`  
**Methodology Lock Status:** `METHODOLOGY_LOCKED` (METHODOLOGY_LOCK = TRUE)  
**Historical Expansion Gate:** `OPEN`  

---

## 1. Executive Summary & Gate Decision

Batch ZZZ.12 formally establishes the **Research Methodology Lock** for the SwingDeck research platform. This batch freezes all research definitions, units of analysis, primary endpoints, counterfactual hierarchies, evidence taxonomies, causality levels, and governance change controls prior to material historical data expansion (Dataset V2).

### Gate Decision Summary:
* **`METHODOLOGY_LOCK = TRUE`**: All 25 methodological dimensions codified, verified, and locked.
* **`HISTORICAL_EXPANSION_GATE = OPEN`**: Historical data expansion to Dataset V2 is formally authorized under the **Replication-First Protocol**.
* **Zero Strategy Modifications**: No Layer E parameter changes, no threshold tuning, no alpha claims.

---

## 2. Frozen Methodology Contract & Taxonomies

### 2.1 Research Objective & Primary Question
> **"Does company-specific historical information provide incremental discriminatory information about subsequent relative performance after accounting for market, peer, exposure, time, and known confounding structures?"**

### 2.2 Core Invariants Locked
* **Unit of Analysis:** $\text{Company } (i) \times \text{Decision Date } (t)$ ($N=73$ Layer-E setups across 12 canonical tickers).
* **Primary Endpoint:** $\mathbf{H_5 \text{ PEER-EXCESS DIFFERENTIAL}}$ ($C0 = +3.10\text{ pp}, C5 = +2.98\text{ pp}$).
* **Secondary Endpoints:** $H_1, H_3, H_10, H_20, MFE, MAE$ (Strictly exploratory).
* **Counterfactual Hierarchy:** $C0$ (Canonical LOO), $C1$ (LOO Validation), $C2$ (Evidence-Excluded), $C3$ (Event-Purified), $C4$ (Date-Purified), $C5$ (Fully Purified).
* **Evidence Taxonomy:** `EVIDENCE_PRESENT`, `EVIDENCE_CONTRADICTORY`, `EVIDENCE_PIT_UNCERTAIN`, `ENTITY_UNRESOLVED`, `NO_EVIDENCE_IN_DATASET`, `VERIFIED_NO_EVENT`.
* **Causality Hierarchy:** `OBSERVED` $\rightarrow$ `CORRELATED` $\rightarrow$ `ECONOMICALLY_PLAUSIBLE` $\rightarrow$ `HYPOTHESIZED` $\rightarrow$ `EXPERIMENTALLY_TESTED` $\rightarrow$ `VALIDATED`.
* **Attribution Taxonomy:** 11 mutually exclusive components (`MARKET`, `SECTOR`, `FACTOR`, `MACRO`, `COMMODITY`, `FLOW`, `NEWS`, `OWNERSHIP`, `RELATIONSHIP`, `COMPANY_SPECIFIC`, `UNKNOWN`).

---

## 3. Four-Class Change Control System

| Change Class | Type | Permitted in Data Expansion? | Governance Requirement |
| :--- | :--- | :---: | :--- |
| **Class A** | Data Addition | **YES** | Must pass Replication-First test on V1 subset |
| **Class B** | Data Correction | **YES** | Must generate corrected dataset version with lineage entry |
| **Class C** | Methodology Change | **CONDITIONAL** | Requires new research version; cannot overwrite V1 |
| **Class D** | Strategy Change | **NO (PROHIBITED)** | Forbidden during historical data expansion |

---

## 4. Replication-First Protocol for Dataset V2

Before any expanded multi-year dataset (Dataset V2) is analyzed for new research:
1. The ingestion engine must extract the exact V1 sample subset ($N=73, 12$ tickers).
2. The replication harness must execute the baseline pipeline on the extracted subset.
3. The calculated $H_5$ peer excess differential must match $C0 = +3.10\text{ pp} \pm 0.0001\text{ pp}$.
4. If replication fails, the expansion run is immediately aborted (`REPLICATION_FAILURE`).

---

## 5. Agent 2 Red Team 20-Dimension Anti-Drift Audit

| # | Audit Dimension | Evaluated Anti-Drift Rule | Status |
| :-: | :--- | :--- | :---: |
| 1 | **Methodology Drift** | Primary question and unit of analysis frozen | **PASS** |
| 2 | **Endpoint Drift** | $H_5$ Peer-Excess Differential locked as primary endpoint | **PASS** |
| 3 | **Peer Definition Drift** | Outcome-blind PIT peer construction strictly enforced | **PASS** |
| 4 | **Evidence State Drift** | 6-state taxonomy locked (`NO_EVIDENCE != NO_EVENT`) | **PASS** |
| 5 | **PIT Drift** | Strict `publication_time <= AS_OF` enforced | **PASS** |
| 6 | **Taxonomy Drift** | Causality (6 levels) & Attribution (11 components) locked | **PASS** |
| 7 | **Hidden Threshold Change** | Layer E signal parameters strictly immutable | **PASS** |
| 8 | **Hidden Sample Change** | Sample $N=73$ locked via cryptographic hash | **PASS** |
| 9 | **Dataset Mutation** | V1 Parquet / DuckDB frozen and read-only | **PASS** |
| 10 | **Snapshot Mutation** | `SNAPSHOT_ZZZ117_687970d0e904` verified immutable | **PASS** |
| 11 | **Code/Config Mismatch** | Code and config hashes cryptographically locked | **PASS** |
| 12 | **Historical Overwrite** | `UPDATED KNOWLEDGE != OVERWRITE HISTORICAL STATE` | **PASS** |
| 13 | **Outcome Leakage** | 0 forward return variables used in peer/event definitions | **PASS** |
| 14 | **Hindsight Prevention** | Point-in-Time uncertainty strictly preserved | **PASS** |
| 15 | **Source Authenticity** | SHA-256 integrity separated from source authenticity | **PASS** |
| 16 | **Missingness Conflation** | Unobserved stratum classified as `NO_EVIDENCE_IN_DATASET` | **PASS** |
| 17 | **Exploratory to Confirmatory** | Mandatory labelling of exploratory vs confirmatory tests | **PASS** |
| 18 | **V1 Replication Protocol** | Replication-first rule codified for all V2 expansions | **PASS** |
| 19 | **Silent Methodology Change** | Class A-D change control protocol enforced | **PASS** |
| 20 | **Causal Overclaim** | Causal Alpha ruled `NOT_ESTABLISHED`; Level 2 Identification | **PASS** |

**Red Team Audit Verdict:** **20 / 20 PASS (METHODOLOGY_LOCK_CERTIFIED_DEFENSIBLE)**

---

## 6. Final Required Governance Certification

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

---

## 7. Absolute Stop Condition

In accordance with Section 40 of Batch ZZZ.12:
* No historical data added in this batch.
* No strategy parameters modified.
* No ticker universe expansion executed.
* Gate is open for future authorized expansion batches.

# BATCH ZZZ.13 — HISTORICAL DATA EXPANSION V2 (ADAPTIVE HISTORICAL DATA & RESEARCH FOUNDATION)

**Batch ID:** `BATCH-ZZZ.13`  
**Date:** September 15, 2026  
**Evaluator:** Agent 1 (Quant & Market Scanner), Agent 2 (Market Intelligence & Red Team), Agent 3 (Investment Committee & Risk — Audit Only)  
**Governance Architecture:** 4-Layer Controlled Evolution Architecture  
**Baseline Immutability:** `METHODOLOGY_V1` & `DATASET_V1` FULLY FROZEN & PROTECTED  
**Foundation Status:** `ADAPTIVE_FOUNDATION_ACTIVE`  

---

## 1. Executive Summary & Core Mandate Resolution

Batch ZZZ.13 establishes the **Adaptive Historical Data & Research Foundation** for SwingDeck. Following the Methodology Lock codified in Batch ZZZ.12, ZZZ.13 implements the architectural framework that enables continuous historical data expansion, new entity discovery, qualitative event intake, schema evolution, and research experimentation **without compromising historical reproducibility, Point-in-Time (PIT) integrity, scientific discipline, or historical comparability**.

### Core Foundation Principle:
> **FREEZE THE BASELINE — ALLOW CONTROLLED EVOLUTION.**  
> SwingDeck is not locked in a "methodology prison". It welcomes new data, sources, relationships, and hypotheses, provided they are formally classified, versioned, sandboxed in research branches, and promoted strictly through the 10-Point Promotion Gate.

---

## 2. Four-Layer Governance Architecture

| Governance Layer | Name | Scope & Authority | Immutability Rule |
| :--- | :--- | :--- | :--- |
| **Layer 1** | **Frozen Baseline** | `METHODOLOGY_V1`, `DATASET_V1` ($N=73$), Canonical Results | **Strictly Immutable** |
| **Layer 2** | **Extension** | Multi-year market data, expanded tickers, qualitative filings, DuckDB relationships | Additive; never overwrites V1 |
| **Layer 3** | **Experiment** | Sandboxed branches for novel controls, counterfactuals, and hypotheses | Isolated in research branches |
| **Layer 4** | **Promotion** | Candidate $\rightarrow$ Tested $\rightarrow$ Validated $\rightarrow$ Promoted | Promoted via 10-Point Gate |

---

## 3. Six-Type Criteria Intake Pipeline

The intake engine has been operationalized and validated across sample proposals representing all 6 canonical types:

| Criterion ID | Discovered Domain | Classification | Compatibility Status | Governance Layer |
| :--- | :--- | :--- | :--- | :--- |
| `CRIT-001-MULTI-YEAR` | Multi-Year Data (2016–2026) | **TYPE A (Data Extension)** | `COMPATIBLE` | Layer 2 Extension |
| `CRIT-002-TIMESTAMP-FIX` | UTC Close Timestamp Precision | **TYPE B (Data Quality)** | `EXTENSION_ONLY` | Layer 2 Extension |
| `CRIT-003-SUPPLY-CHAIN` | Mining Equipment Supplier Links | **TYPE C (Information Extension)** | `EXTENSION_ONLY` | Layer 2 Extension |
| `CRIT-004-HIGH-DIM-FE` | High-Dimensional Fixed Effects | **TYPE D (Analytical Extension)** | `EXPERIMENTAL` | Layer 3 Experiment |
| `CRIT-005-MULTI-ENDPOINT` | Horizon Cumulative Abnormal Return | **TYPE E (Methodology Change)** | `METHODOLOGY_CHANGING` | Layer 3 Experiment $\rightarrow$ V2 |
| `CRIT-006-DYNAMIC-THRESHOLD` | Volatility-Adjusted Scanner Gate | **TYPE F (Strategy Change)** | `STRATEGY_CHANGING` | Strategy Module (Quarantined) |

---

## 4. Schema & Taxonomy Evolution Protocols

### 4.1 Additive Field Lineage
* Schema fields are versioned with metadata: `field_name`, `schema_version`, `introduced_at_batch`, `is_deprecated`, `fallback_value`.
* Historical fields are never deleted; backward compatibility is permanently maintained for Dataset V1 and legacy replays.

### 4.2 Non-Retroactive Taxonomy Expansion
* New taxonomy domains (e.g. `SUPPLY_CHAIN_DEPENDENCY`, `TECHNOLOGY_EXPOSURE`) are added to the taxonomy ledger for Dataset V2+ without retroactively reclassifying historical V1 observations.

---

## 5. Temporal Knowledge Graph & Relationship Tracking

* All newly ingested corporate relationships, ownership structures, and supply-chain linkages enforce strict temporal boundaries:
  $$\text{Relationship} = \{\text{entity}, \text{related\_entity}, \text{type}, \text{valid\_from}, \text{valid\_to}, \text{observed\_at}, \text{source}, \text{confidence}, \text{PIT\_status}\}
* **Preservation of Genuine Uncertainty:** Data expansion strictly enforces $\text{NO\_EVIDENCE\_IN\_DATASET} \neq \text{VERIFIED\_NO\_EVENT}$. Unobserved periods remain unobserved; no artificial backfilling or hallucinated coverage is permitted.

---

## 6. Ten-Point Promotion Gate Protocol

Any criterion, relationship stream, or analytical tool seeking promotion to a formal new methodology version must pass all 10 institutional gates:
1. Clear mathematical/conceptual definition.
2. Verifiable source origin.
3. Strict Point-in-Time (PIT) compliance ($t_\text{pub} \le T$).
4. Cryptographic SHA-256 file provenance.
5. Unambiguous entity resolution.
6. Zero lookahead leakage ($T+1, T+2, T+5$ future injection tests).
7. Non-trivial, non-redundant incremental information.
8. Clear economic/governance use case.
9. Appropriate out-of-sample/multi-cycle validation.
10. Unanimous Red Team anti-drift certification.

---

## 7. Agent 2 Red Team 20-Dimension Adaptive Audit

| # | Red Team Audit Dimension | Evaluated Governance Rule | Status |
| :-: | :--- | :--- | :---: |
| 1 | **Baseline Immutability** | Methodology V1 and Dataset V1 strictly frozen | **PASS** |
| 2 | **Controlled Evolution** | 4-Layer Governance separates baseline from extensions | **PASS** |
| 3 | **No Methodology Prison** | Intake pipeline registers and classifies all new criteria | **PASS** |
| 4 | **Intake Classification** | 6-Type categorization (Types A-F) strictly enforced | **PASS** |
| 5 | **Backward Compatibility** | Compatibility status (Compatible, Experimental, etc.) assigned | **PASS** |
| 6 | **Schema Version Lineage** | Additive field versioning preserves historical schemas | **PASS** |
| 7 | **Taxonomy Evolution** | New domains added without retroactively modifying V1 | **PASS** |
| 8 | **Temporal State Invariance** | valid_from/valid_to enforced on all new relationships | **PASS** |
| 9 | **Preservation of UNKNOWN** | UNKNOWN / NO_EVIDENCE stratum strictly preserved | **PASS** |
| 10 | **Hypothesis Invalidation** | Scientific failure recorded as valid output (not data rejection) | **PASS** |
| 11 | **Conclusion Mutability** | V2 allowed to find stronger, weaker, or zero effects | **PASS** |
| 12 | **Research Branching** | Sandboxed branches prevent mutating parent baselines | **PASS** |
| 13 | **10-Point Promotion Gate** | Promotion requires meeting all 10 institutional criteria | **PASS** |
| 14 | **Point-In-Time Integrity** | publication_time <= AS_OF enforced on all new sources | **PASS** |
| 15 | **Source Provenance** | Cryptographic SHA-256 hashes recorded for all new files | **PASS** |
| 16 | **Strategy Isolation** | Type F strategy changes quarantined from historical foundation | **PASS** |
| 17 | **Methodology Versioning** | Type E changes mandate distinct METHODOLOGY_V2 version | **PASS** |
| 18 | **Entity Resolution Bounds** | Ambiguous entities mapped to ENTITY_UNRESOLVED | **PASS** |
| 19 | **Replication-First Mandate** | Dataset V2 must replicate V1 subset before expansion | **PASS** |
| 20 | **Causal Overclaim Prevention** | New evidence classified under strict 6-level causality hierarchy | **PASS** |

**Red Team Audit Verdict:** **20 / 20 PASS (ADAPTIVE_FOUNDATION_GOVERNANCE_CERTIFIED)**

---

## 8. Final Required Governance Certification

```text
================================================================================
ADAPTIVE FOUNDATION STATUS:    ACTIVE & CERTIFIED
GOVERNANCE ARCHITECTURE:       4-LAYER CONTROLLED EVOLUTION
CRITERIA INTAKE ENGINE:        6-TYPE CLASSIFICATION (A through F)
COMPATIBILITY ASSESSMENT:      5-TIER BACKWARD COMPATIBILITY
PROMOTION GATE:                10-POINT INSTITUTIONAL PROTOCOL
BASELINE IMMUTABILITY:         METHODOLOGY_V1 & DATASET_V1 FULLY PRESERVED
================================================================================
```

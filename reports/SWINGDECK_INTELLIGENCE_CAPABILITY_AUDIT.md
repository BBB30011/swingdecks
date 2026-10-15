# SWINGDECK — MASTER INTELLIGENCE & ENGINEERING CAPABILITY AUDIT V1.0

**Audit Date:** 2026-09-30  
**Repository:** `D:\Project\SwingDeck`  
**Role:** Principal Architect + Senior Quant Research Engineer + Market Intelligence Engineer + Data Engineer + AI Systems Engineer + Adversarial Reviewer  
**Audit Scope:** Full codebase, database schemas, retrieval contracts, agent boundaries, temporal/PIT invariants, and market intelligence reasoning pathways.

---

## 1. Executive Summary & Forensic Baseline

SwingDeck is an autonomous, three-agent swing trading intelligence desk for the Indonesian Equity Market (IDX). The platform's foundational mandate is:

> **STORE ONCE → NORMALIZE CORRECTLY → RELATE CORRECTLY → PROVENANCE EVERYTHING → PRESERVE TIME → RETRIEVE FAST → NEVER INVENT**

The recent Natural Information Ingestion Gate V1 successfully certified the 16-stage pipeline, establishing raw byte immutability, 26-vector source authenticity, 5-tier entity resolution, cryptographic evidence anchoring, and derived graph rebuildability. 

However, forensic analysis reveals critical capability bottlenecks where the system must evolve from a **document-evidence repository** into a **dynamic Temporal Market Intelligence System**.

```text
CURRENT FOUNDATION STATUS:
├── Operational Test Suite: 262 Passed, 3 Skipped, 0 Failed
├── Natural Ingestion Acceptance Suite: 21 Passed (100%)
├── Semantic & Evidence Truth Gate: PASS (0 Findings)
├── Runtime Decision Agents: EXACTLY 3 (AGENT_4 = FORBIDDEN)
├── Live Execution Boundary: BLOCKED (PAPER_ONLY = TRUE)
└── Scientific Research Branch: CLOSED & IMMUTABLE (COBA_001–COBA_018)
```

---

## 2. Current Architecture & Component Topology

```text
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                SWINGDECK RUNTIME DESK                                    │
├─────────────────────────┬───────────────────────────────┬───────────────────────────────┤
│   AGENT 1: QUANT        │   AGENT 2: INTELLIGENCE       │   AGENT 3: COMMITTEE          │
│   "WHAT IS MOVING?"     │   "WHY IS IT MOVING?"         │   "SHOULD WE ACT?"            │
├─────────────────────────┼───────────────────────────────┼───────────────────────────────┤
│ • OHLCV & Price Action  │ • Natural Ingestion Pipeline  │ • Investment Committee Syn.   │
│ • Liquidity Analyzer    │ • 5-Tier Entity Resolver      │ • Opportunity Ranker (0-100)  │
│ • Momentum / Breakout   │ • Red Team / Contradictions   │ • Timing Engine (Proximity/Win│
│ • Benchmark (IHSG) Rel. │ • Economic Transmission       │ • Risk Engine & Sizing        │
│ • Market / Stock Regime │ • LLM Reasoner (PIT-blind)    │ • Exit Engine (Paper Broker)  │
└────────────┬────────────┴───────────────┬───────────────┴───────────────┬───────────────┘
             │                            │                               │
             ▼                            ▼                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    KNOWLEDGE DATA PLATFORM (DuckDB + File System)                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│ [Canonical Tables]: raw_documents, sources, entities, entity_aliases,                  │
│                     entity_identifiers, information_items, claims, evidence,            │
│                     entity_relationships, relationship_evidence, exposures,             │
│                     mechanisms, contradictions, corporate_actions, policies             │
│ [Derived Index]  : derived_entity_neighborhood, derived_entity_exposure_index          │
│ [Retrieval Engine]: FAST PATH (<10ms single hop) / DEEP PATH (multi-hop graph)          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Detailed Forensic Subsystem Audit

### 3.1 Temporal & Source Truth Hardening (Phase 1)
- **Status:** Partially Hardened, Gaps in Timestamp Derivation Metadata.
- **Current Model:** Distinguishes `event_time`, `published_at`, `available_at`, `observed_at`/`retrieval_time`.
- **Findings & Flaws:**
  1. *Timestamp Source Provenance Missing*: When a document is ingested, timestamps are parsed as ISO-8601 strings without recording the `derivation_method` (e.g. `HTTP_HEADER_LAST_MODIFIED`, `ARTICLE_BYLINE_PARSED`, `EXCHANGE_METADATA`, `RETRIEVAL_CLOCK_FALLBACK`).
  2. *Timezone Ambiguity in Unofficial News*: Some Indonesian news feeds output local Western Indonesia Time (WIB / UTC+7) without timezone offsets, which risks timestamp misalignments if parsed as naive UTC.
  3. *PIT Filter Fragility*: If `available_at` is missing, defaulting to `pub_time` or `retrieval_time` lacks an explicit confidence tag (`EXACT_TIMESTAMP` vs `ESTIMATED_AVAILABILITY`).

### 3.2 Information Database V2 — Temporal Market Memory (Phase 2)
- **Status:** Functional Relational DB, Needs State-Transition Memory.
- **Current Tables:** 12 canonical DuckDB tables + 2 derived index tables.
- **Findings & Flaws:**
  1. *Lack of Explicit `information_deltas` Table*: When an event updates an existing entity's project or regulatory status, the delta is inferred at query time rather than recorded as a materialized state transition.
  2. *Missing Market Snapshot at Availability*: The system does not capture the concurrent market state (e.g. IHSG index, sector ETF, stock price at $T_{\text{avail}}$) inside the information record.

### 3.3 Information Novelty & Cross-Source Corroboration (Phase 3 & 5)
- **Status:** Deduplication & Syndication Active; Semantic Novelty Missing.
- **Current Model:** Distinguishes `IDEMPOTENT_RETRIEVAL`, `NEW_REVISION`, `SYNDICATION_LINK`, and `NEW_DOCUMENT`.
- **Findings & Flaws:**
  1. *Repetition vs Novelty*: Ingesting an article with a slightly different wording of old news is classified as `NEW_DOCUMENT`, even if the underlying claim contains zero information novelty.
  2. *Corroboration Lineage*: Lineage tracking exists for syndicated copies via `syndication_original_url`, but lacks a multi-source corroboration cluster that groups independent issuer filings + regulatory notices + media reports into an `EventCluster`.

### 3.4 Exposure & Economic Mechanism Engine (Phase 4)
- **Status:** Ontology Defined; Automated Propagation Missing.
- **Current Model:** `core/semantic_ontology.py` defines 21 `EconomicChannel` enums, 4 `ExposureType` enums, and comprehensive subject-object compatibility matrices.
- **Findings & Flaws:**
  1. *Manual / Rule-Bound Exposure Mapping*: Exposures and mechanisms are currently mapped on a per-entity basis or extracted from explicit case rules (e.g. ADRO $\rightarrow$ AADI spinoff).
  2. *Lack of Upstream Macro Transmission Propagation*: When a policy changes (e.g. Coal Royalty Regulation issued by Ministry of Energy), the graph does not automatically broadcast transmission candidates across the sector's exposed constituent nodes.

### 3.5 Agent 2 Intelligence Reasoning & Red Team (Phase 8)
- **Status:** Structured Output Enforced; Depth Needs Expansion.
- **Current Model:** `Agent2LLMReasoner` generates `Agent2IntelligenceReport` with `FACT`, `OBSERVATION`, `INTERPRETATION`, `HYPOTHESIS` separation, Red Team challenge, and MNPI blocking.
- **Findings & Flaws:**
  1. *Reasoning Depth*: When run in offline/deterministic mode, Agent 2 relies on rule templates rather than deeply querying the multi-hop transmission graph to uncover second-order exposures.
  2. *Missing "Why Now" Verification*: Agent 2 notes catalysts, but does not calculate whether the catalyst has already been priced into current price momentum.

### 3.6 Agent 1 $\leftrightarrow$ Information Database Interlock (Phase 9)
- **Status:** Unidirectional Flow (Agent 1 $\rightarrow$ Agent 2 $\rightarrow$ Agent 3).
- **Findings & Flaws:**
  1. *No Reverse Investigation Trigger*: When Agent 1 detects an anomalous volume surge or momentum breakout on a stock, it does not trigger an on-demand reverse intelligence query ("Has any information delta occurred for this symbol in the last 48 hours?").

### 3.7 Opportunity Ranker & Timing Engine (Phase 10)
- **Status:** Functional Multi-Factor Decomposition; Context-Aware.
- **Current Model:** `core/opportunity_ranker.py` and `core/timing_engine.py` decompose scores into 9 factors (technical, flow, relative strength, sector, regime, catalyst, evidence quality, risk, timing).
- **Findings & Flaws:**
  1. *Heuristic Weights*: Factor weights are properly flagged as `PRELIMINARY / NOT EMPIRICALLY VALIDATED`. They must remain contextual descriptors without claiming false predictive alpha.

### 3.8 Exit Intelligence & Dynamic Thesis Monitoring (Phase 11)
- **Status:** Basic Priority-Based Exit Engine.
- **Current Model:** `core/exit_engine.py` checks 11 exit priorities (DATA_INVALID, THESIS_INVALIDATED, STOP_LOSS, RISK_RED, TARGET_REACHED, MOMENTUM_FADE, FLOW_REVERSAL, CATALYST_EXPIRED, SECTOR_REVERSAL, TIME_EXIT, TIME_DECAY).
- **Findings & Flaws:**
  1. *Reactive vs Proactive Exit*: The exit engine evaluates current position technicals, but does not receive an active stream of `ThesisDelta` from Agent 2 when new contradictory evidence arrives post-entry.

---

## 4. Strengths, Weaknesses, and Hidden Risks

### 4.1 Current Strengths
1. **Zero Hallucination / Never Invent Enforcement**: The system strictly uses `UNKNOWN` rather than guessing missing facts.
2. **True Raw Byte Immutability**: Captured natural documents are preserved verbatim with SHA-256 digests.
3. **Strict 3-Agent Boundary**: Exactly 3 runtime agents with clear operational separation (`Agent 1` Quant, `Agent 2` Intelligence, `Agent 3` Committee).
4. **Sub-10ms PIT Retrieval**: DuckDB-powered `KnowledgeRetrievalEngine` delivers Point-in-Time verified records in under 10ms.
5. **Deterministic Rebuildability**: Derived intelligence graph indexes are 100% rebuildable from canonical DuckDB tables.

### 4.2 Critical Weaknesses
1. **Lack of Information Novelty Classification**: Articles reporting already-known facts are stored as new documents without marking claim novelty as `REPETITION` vs `NEW_CATALYST`.
2. **Absence of Macro/Policy Exposure Propagation**: Policy announcements from government/ministry nodes do not systematically propagate structural exposure flags down to sector companies.
3. **Passive Exit Monitoring**: Agent 2 is not automatically polled to re-verify active open positions against incoming information items.

### 4.3 Hidden Risks
1. **Timezone Offset Truncation**: Public RSS/scraped feeds with ambiguous GMT/WIB timezones could introduce minor temporal drift if not explicitly normalized to UTC.
2. **Duplicate Wire News Inflation**: News portals publishing identical syndicated articles without canonical attribution could falsely inflate corroboration scores if syndication lineage is omitted.

---

## 5. Prioritized Capability Upgrade Matrix

| Priority | Component | Objective | Impact | Complexity | Risk | Trading Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **P0** | **Timestamp Metadata Hardening** | Add derivation method, timezone source, and confidence to all timestamps | High | Low | Low | Critical (PIT Integrity) |
| **P0** | **MNPI & Restricted Decision Firewall** | Formalize automated policy-check gate on all retrieval paths | High | Low | Low | Critical (Compliance) |
| **P1** | **Information Novelty Engine** | Classify incoming claims: `NEW`, `UPDATE`, `CONFIRMATION`, `REPETITION` | Very High | Medium | Low | High (Signal Clarity) |
| **P1** | **Multi-Hop Exposure Propagation** | Propagate policy/commodity shocks to sector & peer companies | Very High | Medium | Medium | High (Catalyst Discovery) |
| **P1** | **Proactive Exit Intelligence (Thesis Monitor)**| Re-evaluate open positions against incoming contradictory evidence | High | Medium | Low | High (Capital Protection) |
| **P2** | **Reverse Quant $\leftrightarrow$ Intel Query** | Trigger intelligence lookups when Agent 1 detects anomalous volume | Medium | Medium | Low | Medium (Anomaly Context) |
| **P2** | **Market State Snapshot at Availability** | Capture IHSG/sector state at the exact moment information became available | Medium | Low | Low | Medium (Market Reaction Context)|
| **P3** | **Continuous Real-Time Stream Worker** | Daemonized async polling for official disclosures and exchange feeds | Medium | High | Medium | Operational Scale |

---

## 6. Recommended Target Architecture & Implementation Roadmap

```text
                                  TARGET CAPABILITY ARCHITECTURE
                                  
  [REAL-WORLD DATA STREAM] ──▶ [SOURCE AUTHENTICITY & TIMESTAMP HARDENING]
                                          │
                                          ▼
                             [16-STAGE INGESTION PIPELINE]
                                          │
                                          ▼
                         [INFORMATION NOVELTY & CLUSTERING]
                          ├── NEW CATALYST
                          ├── STATUS UPDATE / TRANSITION
                          ├── REPETITION / SYNDICATION
                          └── CONTRADICTION
                                          │
                                          ▼
                      [MULTI-HOP ECONOMIC TRANSMISSION GRAPH]
                          Policy / Macro ──▶ Channel ──▶ Sector ──▶ Company (ADRO/BBCA)
                                          │
                                          ▼
                        [CANONICAL DUCKDB INTELLIGENCE STORE]
                                          │
                                          ▼
                        [FAST / DEEP PIT RETRIEVAL CONTRACT]
                                   │              │
                                   ▼              ▼
                     [AGENT 1 QUANT] ◀──────────▶ [AGENT 2 INTELLIGENCE + RED TEAM]
                            │                               │
                            └──────────────┬────────────────┘
                                           │
                                           ▼
                             [AGENT 3 INVESTMENT COMMITTEE]
                                           │
                        ┌──────────────────┴──────────────────┐
                        ▼                                     ▼
             [ENTRY SIZING & TIMING]                [DYNAMIC EXIT THESIS MONITOR]
```

### Proposed Sequential Implementation Gates:
1. **Gate 1: Timestamp & Source Provenance Hardening** (P0) — Explicit timezone, derivation method, and timestamp confidence tagging.
2. **Gate 2: Information Novelty & State-Transition Engine** (P1) — Semantic claim clustering, repetition filtering, and `information_deltas` tracking.
3. **Gate 3: Multi-Hop Transmission & Exposure Propagation** (P1) — Economic channel propagation across macro $\rightarrow$ commodity $\rightarrow$ sector $\rightarrow$ equity.
4. **Gate 4: Dynamic Thesis & Exit Intelligence Monitor** (P1) — Automated post-entry thesis re-verification against new information items.

---

## 7. Deferred & Non-Goals

1. **Autonomous Live Broker Execution**: Remains strictly `BLOCKED` (Paper-Only governance).
2. **Creation of Agent 4**: Remains strictly `FORBIDDEN` (System retains exactly 3 decision agents).
3. **Alpha / Causality Claims**: Scientific research branch remains `CLOSED`. No empirical alpha or causality is claimed.

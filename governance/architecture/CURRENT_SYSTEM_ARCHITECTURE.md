# SWINGDECK — CURRENT SYSTEM ARCHITECTURE

## 1. Executive Summary

SwingDeck is an evidence-based quantitative and intelligence-driven swing trading desk platform built specifically for the Indonesian equity market (IDX). The platform operates under a strict, governed **3-Agent Architecture** backed by deterministic relational intelligence (DuckDB), chronological time-series storage (Parquet/CSV), queue orchestration with idempotency, and rigorous Point-In-Time (PIT) firewalls.

Following the scientific closure of the historical research branch (**COBA_001 through COBA_018**), the platform is formally divided into two distinct, decoupled operating layers:
1. **Layer A: Frozen Scientific Research Layer** (Immutable historical empirical evidence).
2. **Layer B: Post-Research Engineering Layer** (Active architecture, reliability, data engineering, observability, operational safety, and testing).

### System Readiness Classification
* **Engineering Status**: `ENGINEERING_READY_WITH_LIMITATIONS`
  * *Limitations*: Daily-bar discretization (intraday auction microstructure and order book queues unmodeled); semi-manual news ingestion in Agent 2; unmodeled market impact / slippage queues; external API synchronization dependencies.
* **Operational Status**: `OPERATIONALLY_READY_WITH_LIMITATIONS`
  * *Authorized Scope*: Strictly bounded to (1) research, (2) deterministic historical replay, (3) backtesting/evaluation, and (4) semi-manual paper trading.
  * *Autonomous Live Trading*: Strictly **`NOT_READY`** (`AUTONOMOUS_LIVE_TRADING = BLOCKED`).
* **Scientific Strategy Status**: Permanently **`NOT_READY`** (`STRATEGY_OPTIMIZATION = BLOCKED`).


---

## 2. End-to-End System Data Flow

```text
       [ IDX Market Data / Corporate Actions / Disclosures / News RSS ]
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │   Data Ingestion Engine      │
                       │   (Idempotent, Raw Capture)  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │   Validation & PIT Gate      │
                       │   (Schema, Timestamp, Hash)  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │   Normalization Substrate    │
                       │ (DuckDB Ledger / Parquet Lake│
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │           AGENT 1            │
                       │   (Quant & Market Scanner)   │
                       │   "WHAT IS MOVING TODAY?"    │
                       └──────────────┬───────────────┘
                                      │ Candidate Setup Stream
                                      ▼
                       ┌──────────────────────────────┐
                       │           AGENT 2            │
                       │ (Market Intelligence/RedTeam)│
                       │ "WHY DID IT MOVE? SURVIVE?"  │
                       └──────────────┬───────────────┘
                                      │ Synthesized Evidence & Red Team Packet
                                      ▼
                       ┌──────────────────────────────┐
                       │           AGENT 3            │
                       │ (Investment Committee/Risk)  │
                       │ "SHOULD WE ACT? SIZING/R:R?" │
                       └──────────────┬───────────────┘
                                      │ Operational Action (BUY, WAIT, HOLD, SELL, AVOID)
                                      ▼
                       ┌──────────────────────────────┐
                       │      Decision & Alerts       │
                       │ (Deep Alert Engine / Queue)  │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
                       ┌──────────────────────────────┐
                       │    Position & Risk Monitor   │
                       │ (MTM Snapshot / Invalidation)│
                       └──────────────────────────────┘
```

---

## 3. Strict 3-Agent Boundary Enforcement

The system mandates **EXACTLY 3 RUNTIME AGENTS**. A fourth agent is strictly forbidden (`AGENT_4 = FORBIDDEN`). Supporting modules (orchestrator, data sources, databases, monitors) are research and platform infrastructure, never agents.

### Agent 1: Quant & Market Scanner
* **Primary Mandate**: "WHAT IS MOVING?"
* **Authorized Scope**:
  * Technical price action, trend filters (EMA, SMA), momentum indicators, volume profile.
  * Relative strength versus benchmark (IHSG).
  * Market regime detection (BULL, BEAR, SIDEWAYS, HIGH_VOLATILITY).
  * Liquidity and turnover threshold validation (turnover $\ge 1\text{B IDR}$, price $\ge 100\text{ IDR}$).
  * Candidate setup ranking and initial stop-loss/target boundary calculation.
* **Prohibited Scope**:
  * Final trade commitment.
  * Semantic reasoning or fundamental valuation.
  * Portfolio allocation optimization.

### Agent 2: Market Intelligence & Red Team
* **Primary Mandate**: "WHY DID IT MOVE? CAN THE THESIS SURVIVE ADVERSARIAL CHALLENGE?"
* **Authorized Scope**:
  * Relational evidence retrieval from DuckDB (`dim_entity`, `fact_event`, `fact_exposure`, `fact_relationship`).
  * Asymmetric beneficiary detection and peer differential analysis (Leave-One-Out peer exclusion).
  * News, corporate disclosures, dividends, splits, and macro policy context.
  * Multi-dimensional Red Team adversarial challenge (completeness, contradictions, speculation flags).
  * Dual Research Mode: `API` (automated offline) and `WEB` (IDE-assisted human-in-the-loop).
* **Prohibited Scope**:
  * Mutating canonical market data or databases.
  * Generating trade execution sizing or timing triggers.
  * Accessing forward return outcomes ($H_1, H_3, H_5, H_{10}, H_{20}$).

### Agent 3: Investment Committee & Risk Engine
* **Primary Mandate**: "SHOULD WE ACT NOW, AND HOW SHOULD RISK BE MANAGED?"
* **Authorized Scope**:
  * Multi-dimensional synthesis of Agent 1 quantitative score and Agent 2 Red Team verdict.
  * **Decision State Taxonomy Reconciliation**:
    * **Layer A (Historical Frozen Taxonomy)**: `ACT`, `WATCH`, `WAIT`, `REJECT`, `INSUFFICIENT` (permanently immutable across COBA_001–COBA_018).
    * **Layer B (Operational Runtime Action Taxonomy)**: `BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID` (governed by `core/schemas.py` and `core/decision.py`).
    * **Semantic Mapping**:
      * `BUY` $\leftrightarrow$ Operational implementation of historical `ACT`.
      * `WAIT` $\leftrightarrow$ Operational implementation of historical `WAIT` / `INSUFFICIENT` / `WATCH`.
      * `AVOID` $\leftrightarrow$ Operational implementation of historical `REJECT` (downside risk, fatal contradictions, or failed red-team challenge).
      * `HOLD` / `SELL` $\leftrightarrow$ Operational position management lifecycle states for active open positions.
    * *Defensive Governance Note*: Operational `AVOID` is strictly runtime execution vocabulary and DOES NOT modify or reopen the historical frozen taxonomy (`ACT`/`WATCH`/`WAIT`/`REJECT`/`INSUFFICIENT`).
  * Sizing and risk management math: 0.5% capital-at-risk ceiling at fixed 3% stop distance.
  * Indonesian statutory integer lot sizing (100 shares/lot) with zero fractional shares.
  * Invalidation trigger monitoring and R/R ratio gating ($\ge 2.0$).
* **Prohibited Scope**:
  * Acting as a fourth runtime agent.
  * Bypassing Red Team blocks or overriding critical contradictions without documented justification.

---

## 4. Point-In-Time (PIT) Architecture

To prevent lookahead bias and future data leakage, every operational information object conforms to a 5-timestamp model:

| Timestamp Attribute | Definition | Enforcement Rule |
| :--- | :--- | :--- |
| `event_time` | The physical moment an economic or market event occurred. | Informational only. |
| `publication_time` | The exact UTC timestamp when the information was published publicly. | Must be $\le$ Decision Timestamp ($T_0$). |
| `ingestion_time` | The timestamp when the system received and recorded the data. | Audited for system lineage. |
| `effective_time` | The moment from which the event officially applies (e.g. ex-dividend date). | Applied according to exchange rules. |
| `availability_time` | The earliest moment downstream agents are permitted to query the object. | $\max(\text{publication\_time}, \text{ingestion\_time})$. |

### ReplayFirewall Mechanics
The `ReplayFirewall` (`core/replay_firewall.py`) enforces strict runtime boundaries:
1. **Outcome Blindness**: Hard-blocks any record containing forward return fields (`H1`, `H3`, `H5`, `H10`, `H20`, `mae`, `mfe`).
2. **Future Timestamp Rejection**: Rejects any record with `published_at > decision_datetime`.
3. **Current-State Rejection**: Rejects records tagged as live current state during historical simulation.
4. **Peer Self-Exclusion**: Strictly excludes the target asset from its own contextual peer basket.

---

## 5. Live vs. Historical Data Isolation

| Dimension | Historical Research Substrate | Live Operational Substrate |
| :--- | :--- | :--- |
| **Data Source** | Canonical 80-ticker Lake & 2,826 Session Calendar | Real-time exchange feed / Daily close ingest |
| **Storage Location** | `data/parquet/market/`, `data/raw/historical/` | `data/raw/market/`, `queue/`, `state/` |
| **Database** | Read-only historical DuckDB snapshot | `data/duckdb/intelligence.duckdb` |
| **Execution Price** | Exact Next-Day Open (observed quote) | Order execution fill quote |
| **Horizon Exit** | Exact Observed Close on session $T+H$ | Real-time stop-loss / take-profit order |
| **Isolation Barrier** | Historical replay cannot access live cache | Live runner cannot read forward simulation results |

---

## 6. Queue, Orchestration & Event Architecture

The operational execution pipeline is managed by `Orchestrator` (`core/orchestrator.py`) and `PipelineRunner` (`core/pipeline_runner.py`):

1. **Queue Hierarchy**:
   * `queue/`: Pending incoming candidate jobs.
   * `queue/processing/`: Active jobs currently undergoing Agent 1/2/3 evaluation.
   * `queue/completed/`: Successfully synthesized decisions.
   * `queue/failed/`: Recoverable failures eligible for retry.
   * `queue/dead_letter/`: Unrecoverable errors, corrupted JSON, or idempotency conflicts.
2. **Idempotency Engine**: Cryptographically hashes inputs (`input_hash`). Duplicates are skipped without side effects; hash conflicts trigger dead-letter isolation.
3. **Retry Policy**: Exponential backoff with maximum 3 retry attempts for transient errors; deterministic classification of retryable vs non-retryable exceptions.
4. **Atomic Helper**: All state persistence operations utilize atomic file writing (`.tmp` write followed by atomic rename) to eliminate partial-write corruptions during sudden shutdown.
5. **Health Monitor**: Continuously verifies database accessibility, disk space, and queue health. Transitions system to `PAUSED` if anomalies are detected.

---

## 7. Operational Safety & Failure Modes

The platform enforces fail-safe defaults across every decision pathway:

| Scenario / Condition | Unsafe Behavior (FORBIDDEN) | Safe Behavior (ENFORCED) |
| :--- | :--- | :--- |
| **Missing Market Data** | Assume positive momentum / Buy | Transition to `NO_DATA` / Action: `AVOID` |
| **Insufficient Intelligence** | Default to approval | Transition to `INSUFFICIENT` / Red Team: `BLOCK` / Action: `WAIT` |
| **Unresolved Contradiction** | Ignore contradiction | Red Team: `BLOCK` / Action: `AVOID` |
| **High Volatility / Gap Down** | Assume stop filled at stop price | Enforce observed Open gap-fill accounting |
| **Cash Exhaustion / Contention** | Allow fractional lots or margin debt | Strict integer lots; block new entries when cash exhausted |
| **System Error in Pipeline** | Emit default buy decision | Move job to `dead_letter`; Action: `AVOID` |

---

## 8. Governance & Permanent Research Firewalls

All operations within SwingDeck remain bound by the permanent scientific firewalls established at the closure of COBA_018:
* `CAUSALITY = NOT_PROVEN`
* `STANDALONE_ALPHA = NOT_PROVEN`
* `STRATEGY_OPTIMIZATION = BLOCKED`
* `STRATEGY_READINESS = NOT_READY`
* `EXACTLY_3_AGENTS = TRUE`
* `AGENT_4 = FORBIDDEN`
* `RESEARCH_BRANCH = CLOSED`

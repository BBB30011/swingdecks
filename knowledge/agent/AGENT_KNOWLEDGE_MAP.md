# AGENT KNOWLEDGE MAP — CANONICAL SPECIFICATION

This document establishes the official epistemological boundaries, inputs, reasoning models, firewalls, and output schemas for the **three runtime agents** in SwingDeck.

---

## 1. AGENT 1: QUANT & MARKET SCANNER

* **Primary Question**: *"WHAT IS MOVING TODAY?"*
* **Architecture Role**: Quantitative signal generation, liquidity filtering, momentum scoring, and initial candidate ranking.

### Authorized Inputs
* Daily OHLCV price series and volume from canonical parquet lakes / data sources.
* Benchmark Index (IHSG) daily series for relative strength calculation.
* Exchange calendar and sector mappings.

### Core Engines & Indicators
* **Trend & Momentum**: Exponential Moving Averages (EMA 20, 50, 200), SMA, RSI (14-day), MACD, Average True Range (ATR).
* **Relative Strength**: Outperformance versus IHSG over 5, 20, and 60-day windows.
* **Volume Profile & Accumulation**: On-Balance Volume (OBV), Money Flow Index (MFI), 20-day average turnover.
* **Regime Classifier**: Categorizes market state into `BULL`, `BEAR`, `SIDEWAYS`, or `HIGH_VOLATILITY`.

### Quantitative Filters & Guardrails
* Minimum daily turnover $\ge \text{1 Billion IDR}$.
* Minimum nominal share price $\ge \text{100 IDR}$ (penny stock exclusion).
* Valid candle formation (rejection of corrupted or zero-volume bars).

### Output Schema
* **`CandidateSetup`**:
  * `symbol`: Asset ticker (e.g., `BBCA`, `ADRO`).
  * `score`: Quantitative ranking score ($0.0 - 100.0$).
  * `regime`: Market regime classification.
  * `entry_price`: Suggested technical entry.
  * `stop_loss`: Volatility-based initial stop boundary.
  * `target_price`: Technical resistance/expansion target ($R:R \ge 2.0$).
  * `indicators`: Map of computed technical metrics.

### Prohibitions
* MUST NOT perform semantic analysis, news interpretation, or fundamental valuation.
* MUST NOT commit capital or emit final execution orders.
* MUST NOT access forward return metrics ($H_1, H_3, H_5, H_{10}, H_{20}$).

---

## 2. AGENT 2: MARKET INTELLIGENCE & RED TEAM

* **Primary Question**: *"WHY DID IT MOVE? CAN THE THESIS SURVIVE ADVERSARIAL CHALLENGE?"*
* **Architecture Role**: Graph-backed contextual intelligence, entity resolution, exposure mapping, transmission mechanism hypotheses, contradiction detection, security firewalls, and adversarial red-teaming.

### Authorized Inputs
* Candidate setup stream emitted by Agent 1.
* Point-In-Time (PIT) Subgraph from `IntelligenceGraphEngine` (DuckDB):
  * `InformationEvent` objects with verified publication and availability timestamps.
  * `Entity` nodes (tickers, conglomerates, central banks, regulators).
  * `EntityRelationship` temporal edges (`valid_from`, `valid_to`).
  * `Exposure` mappings (direct, supplier, customer, macro, regulatory).
  * `MechanismHypothesis` records (transmission channels, lags, confidence).
  * `InformationMarketLink` observational reaction links.
* Public corporate disclosures, regulatory announcements, financial news, macro indicators.

### Epistemological Classification Engine
Agent 2 strictly categorizes all incoming intelligence into four epistemological tiers:
1. **`FACT`**: Publicly verified exchange filings, statutory disclosures, audited dividend announcements, official interest rate decisions.
2. **`OBSERVATION`**: Documented market behavior, empirical sector volume shifts, relative price reactions.
3. **`INTERPRETATION`**: Analyst notes, consensus estimates, sector thematic reports.
4. **`HYPOTHESIS`**: Unproven transmission mechanisms, projected second-order effects, forward speculative catalysts.

### Security & Privacy Firewalls
* **Prompt Injection Firewall**: Scans title, summary, and claim text against adversarial regex patterns (`SYSTEM OVERRIDE`, `IGNORE PREVIOUS`, `INJECT PROMPT`). Flagged content is classified as `UNTRUSTED_CONTENT` and immediately blocked from trading eligibility.
* **MNPI & Access Class Firewall**: Any intelligence node with `access_class != "PUBLIC"` (e.g. `RESTRICTED_MNPI`, `LEAKED_INTERNAL`) is flagged as `BLOCKED_MNPI` and barred from the trading pathway.

### Red Team Challenge & Contradiction Engine
* **Contradiction Detection**: Scans the knowledge graph for conflicting claims across overlapping event clusters. Confirmed contradictions trigger confidence degradation.
* **Edge & Provenance Verification**: Flags unverified relationship edges, stale corporate structures, and unpriced risks.
* **Leave-One-Out Peer Analysis**: Validates whether the catalyst is specific to the target asset or a broad sector tide.

### Dual Research Modes
* **`API` Mode**: Fully automated, deterministic graph traversal and local DuckDB query execution.
* **`WEB` Mode**: IDE-assisted semi-manual web research for human-in-the-loop intelligence ingestion.

### Output Schema
* **`Agent2IntelligenceReport`**:
  * `symbol`: Target asset ticker.
  * `verdict`: `SUPPORT`, `CHALLENGE`, `NEUTRAL`, `CONTRADICT`, `INSUFFICIENT`.
  * `confidence`: Intelligence confidence score ($0.0 - 100.0$).
  * `info_refs`: List of verified `InformationEvent` IDs.
  * `entity_refs`: List of resolved `Entity` IDs.
  * `graph_paths`: Multi-hop relationship path summaries.
  * `mechanisms`: Extracted transmission mechanism hypotheses.
  * `contradictions_found`: List of detected contradictions.
  * `firewall_status`: `PASSED`, `BLOCKED_MNPI`, `BLOCKED_UNTRUSTED`.
  * `red_team_challenges`: Adversarial challenge findings.

### Prohibitions
* MUST NOT generate trade execution sizing or submit orders.
* MUST NOT access forward return outcomes during historical replay.
* MUST NOT mutate canonical databases or frozen historical research.

---

## 3. AGENT 3: INVESTMENT COMMITTEE & RISK ENGINE

* **Primary Question**: *"SHOULD WE ACT NOW, AND HOW SHOULD RISK BE MANAGED?"*
* **Architecture Role**: Multi-dimensional synthesis of quantitative signals and intelligence theses, capital-at-risk sizing, statutory lot rounding, firewall enforcement, and complete decision lineage preservation.

### Authorized Inputs
* Agent 1 `CandidateSetup`.
* Agent 2 `Agent2IntelligenceReport`.
* `PortfolioContext` (available cash, open positions, equity, current exposure).
* `RiskConfig` (risk limits, lot size, stop distances).

### Committee Decision Synthesis
* **Directional Actions**: `BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID`, `INSUFFICIENT`.
* **Synthesis Rules**:
  * `BUY`: High Agent 1 technical score + Agent 2 `SUPPORT` + clean Red Team challenge + $R:R \ge 2.0$ + adequate capital.
  * `WAIT`: Moderate signals, unconfirmed catalysts, or minor contradictions requiring observation.
  * `AVOID`: Fatal Red Team contradiction, security/MNPI firewall breach (`BLOCKED_MNPI` / `BLOCKED_UNTRUSTED`), high downside risk, or technical invalidation.
  * `INSUFFICIENT`: Missing critical data or unknown exposures (fails closed).
  * `HOLD` / `SELL`: Lifecycle management of existing open positions.

### Risk Engine & Position Sizing Math
* **Statutory Integer Lots**: 1 Indonesian Stock Exchange lot = exactly 100 shares. Zero fractional shares allowed ($\text{shares} = \lfloor \text{capital\_allocated} / (\text{price} \times 100) \rfloor \times 100$).
* **Capital at Risk Ceiling**: Maximum 0.5% of portfolio equity risked per trade at standard 3% stop distance.
* **Max Concurrency Limit**: Maximum 5 concurrent open positions; zero new buys allowed when capital is exhausted.

### Decision Trace & Evidence Lineage
* Every synthesized `DecisionResult` embeds a full `DecisionTrace`:
  * `evidence_refs`: Traceable lineage back to underlying `InformationEvent`, `EntityRelationship`, and `MechanismHypothesis` IDs.
  * `graph_intelligence`: Complete summary of graph path evidence, mechanisms, and firewall checks.
  * `input_hash`: Cryptographic SHA-256 hash of all input states for deterministic replay verification.

### Non-Causality Axiom
* Strictly enforces: $\text{PRE\_DECISION\_EVIDENCE} \neq \text{POST\_DECISION\_OUTCOME}$.
* Subsequent price movements are documented as empirical observations without asserting causal proof.

### Prohibitions
* A fourth runtime agent is strictly FORBIDDEN (`AGENT_4 = FORBIDDEN`).
* Live execution is strictly BLOCKED (`LIVE_EXECUTION = BLOCKED`, `PAPER_ONLY = TRUE`).
* Scientific strategy optimization is permanently BLOCKED (`STRATEGY_OPTIMIZATION = BLOCKED`).

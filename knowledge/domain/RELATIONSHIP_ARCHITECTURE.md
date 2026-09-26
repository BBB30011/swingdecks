# SwingDeck Relationship Data Architecture

This document defines the strategy for integrating relationship and causal data into the SwingDeck decision engine. It outlines the conceptual model and establishes the phasing strategy for implementing Graph-based Intelligence (Neo4j) vs. Relational Data (JSON/Parquet/SQL).

## 1. The Decision: Neo4j Applicability
After evaluating the requirements and drawing inspiration from external repositories (like `idx-bei`), the verdict on adopting Neo4j is:
**DO NOT ADOPT (FOR CORE TRADING/BACKTEST ENGINE)**

**Reasoning:**
- Core trading logic relies on Point-In-Time (PIT) OHLCV vectors, indicators, and flat macro/catalyst records. These are processed fastest via JSON, Parquet, or SQLite.
- Neo4j introduces significant overhead for linear time-series processing.
- Graph databases excel in **multi-hop relationship exploration** (e.g., finding hidden Ultimate Beneficial Owners or overlapping director boards across conglomerates).
- We will only adopt Neo4j as a downstream *Relationship Intelligence Engine* (Phase 3) if testing proves that complex multi-hop relationship features yield significant out-of-sample predictive edge over simple SQL relational joins.

---

## 2. Phased Architecture Strategy

### Phase 1: Flat Relational Baselines (Current State)
- **Tech Stack**: JSON, Parquet, SQLite (if needed).
- **Entities**: `Company`, `Sector`, `Signal`, `Trade`, `Catalyst`, `MacroEvent`.
- **Relationships**: Simple 1:1 or 1:N linkages evaluated sequentially.
  - `Company` BELONGS_TO `Sector`
  - `Catalyst` AFFECTS `Company`
  - `Trade` RESULTED_IN `Outcome`

### Phase 2: Advanced Relational Datasets
- **Goal**: Ingest critical relationship datasets without adopting graph DB overhead.
- **Datasets**: 
  - `Corporate Actions` (Stock Splits, Dividends, Rights Issues)
  - `Broker Flow` & `Bandarmology` (Broker accumulation patterns)
  - `KSEI / Shareholder Drift` (Changes in institutional ownership > 5%)
- **Implementation**: Mapped via structured JSON records or SQL joins. Tested as new features inside the `Quant` and `Intelligence` agents.

### Phase 3: Graph Intelligence Layer (Neo4j)
- **Goal**: Discover hidden correlations and multi-hop exposures.
- **Trigger**: When simple Phase 2 features show plateauing returns, and we need to map complex exposures like:
  - `Company A` CORRELATED_WITH `Company B` due to shared `UBO` (Ultimate Beneficial Owner).
  - `MacroEvent` IMPACTS `Sector` which CASCADES_TO `Company`.
- **Implementation**: Deploy Neo4j strictly as a sidecar intelligence service. The core engine queries the graph for a "Relationship Risk Score" rather than running the trading loop inside Neo4j.

---

## 3. Conceptual Entity-Relationship Model

Before writing any database schemas, the domain is conceptually modeled as follows. Every temporal edge must include `valid_from` and `valid_to` properties to prevent hindsight leakage.

### Core Entities
- `Company`, `Sector`, `Industry`
- `Person` (Director/Commissioner), `Shareholder` (Institution/UBO), `Broker`
- `Catalyst`, `News`, `MacroEvent`, `PolicyEvent`, `Commodity`, `Index`
- `CorporateAction`, `Trade`, `Decision`, `Knowledge`, `Signal`

### Edges (Relationships)
- `Company` ──BELONGS_TO──> `Sector`
- `Company` ──RELATED_TO──> `Company`
- `Company` ──OWNED_BY──> `Shareholder`
- `Person` ──DIRECTOR_OF──> `Company`
- `Broker` ──TRADES──> `Company`
- `Institution` ──FLOWS_INTO──> `Company`
- `Catalyst` ──AFFECTS──> `Company`
- `MacroEvent` ──AFFECTS──> `Sector`
- `Commodity` ──IMPACTS──> `Company`
- `Knowledge` ──DERIVED_FROM──> `Trade`

> [!IMPORTANT]  
> All relationships extracted from news or corporate filings must carry a `knowledge_available_at` timestamp. Graph queries during historical simulations must strictly filter out edges created after the simulation tick.

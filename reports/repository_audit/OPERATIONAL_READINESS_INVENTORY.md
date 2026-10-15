# OPERATIONAL READINESS INVENTORY
## SWINGDECK PAPER-TRADING RUNTIME SUBSYSTEM

**Run ID**: `OPERATIONAL_RUN_20260928_1245`  
**Date**: September 28, 2026  
**Auditor**: Antigravity Autonomous Operational Agent  
**Repository**: `D:\Project\SwingDeck`  
**Execution Mode**: Autonomous Long-Run Paper-Trading Validation  

---

## 1. System Inventory Matrix

| Subsystem Component | Canonical Implementation Path | Operational Responsibility | Mutability | Primary Schema / Contract |
| :--- | :--- | :--- | :--- | :--- |
| **CLI Ingress** | [`main.py`](file:///D:/Project/SwingDeck/main.py), [`core/command_parser.py`](file:///D:/Project/SwingDeck/core/command_parser.py) | Interactive shell & human command parsing (Semi-Manual Mode) | Controlled | Command strings (`AGENT2 UPDATE NEWS`, `AGENT2 INGEST NEWS`) |
| **Orchestrator** | [`core/orchestrator.py`](file:///D:/Project/SwingDeck/core/orchestrator.py) | Pipeline coordination, health check, idempotency, retry, DLQ | Mutable State | `JobContext`, `JobState`, `FailureType` |
| **Pipeline Runner** | [`core/pipeline_runner.py`](file:///D:/Project/SwingDeck/core/pipeline_runner.py) | Stage-by-stage multi-agent pipeline execution with atomic persistence | Mutable State | Stage JSONs (`stages/{job_id}_{stage}.json`) |
| **Daily Cycle** | [`core/daily_cycle.py`](file:///D:/Project/SwingDeck/core/daily_cycle.py) | Scheduled 5-phase operating day (`08:30`, `11:00`, `14:00`, `15:30`, `16:00`) | Stateless | Market day phase envelopes |
| **Data Source Factory**| [`core/data_source_factory.py`](file:///D:/Project/SwingDeck/core/data_source_factory.py) | Decoupled factory instantiating market data providers | Stateless | Config dict $\to$ `MarketDataSource` |
| **Market Data Providers**| [`core/data_source.py`](file:///D:/Project/SwingDeck/core/data_source.py), [`core/csv_data_source.py`](file:///D:/Project/SwingDeck/core/csv_data_source.py), [`core/providers/yfinance_provider.py`](file:///D:/Project/SwingDeck/core/providers/yfinance_provider.py) | Market OHLCV snapshot retrieval (MOCK, CSV, YFINANCE) | Read-Only | `MarketSnapshot`, `MarketBar` |
| **Agent 1 (Quant)** | [`agents/agent1_quant/pipeline.py`](file:///D:/Project/SwingDeck/agents/agent1_quant/pipeline.py) | Quantitative screening, liquidity filter, ATR, RSI, regime detection | Controlled | `Agent1Output`, `QuantResult` |
| **Agent 2 (Intelligence)**| [`agents/agent2_intelligence/pipeline.py`](file:///D:/Project/SwingDeck/agents/agent2_intelligence/pipeline.py) | Contextual / Mechanism Reasoning, news disclosures, Red Team | Controlled | `Agent2IntelligenceOutput`, `RedTeamResult` |
| **Agent 3 (Committee)** | [`agents/agent3_committee/pipeline.py`](file:///D:/Project/SwingDeck/agents/agent3_committee/pipeline.py) | Multi-factor evidence synthesis, sizing, operational decision | Controlled | `DecisionResult` (`BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID`) |
| **Queue Lifecycle** | [`core/queue.py`](file:///D:/Project/SwingDeck/core/queue.py) | Transactional atomic file queue (`pending`, `processing`, `completed`, `dead_letter`) | Ephemeral Mutable | `JobEnvelope` |
| **Intelligence Lake** | [`data/duckdb/intelligence.duckdb`](file:///D:/Project/SwingDeck/data/duckdb/intelligence.duckdb) | Relational store for entities, news events, disclosures, price reactions | Versioned DB | 10 Relational tables (`dim_entity`, `fact_event`, etc.) |
| **Position Lifecycle** | [`core/position.py`](file:///D:/Project/SwingDeck/core/position.py), [`core/paper_portfolio.py`](file:///D:/Project/SwingDeck/core/paper_portfolio.py) | Paper trade tracking, lot sizing, MTM, MAE/MFE, reconciliation | Mutable State | `PaperPosition`, `PositionMonitorEvent` |
| **Exit Engine** | [`core/exit_engine.py`](file:///D:/Project/SwingDeck/core/exit_engine.py) | Deterministic exit evaluation priority (DATA_INVALID $\to$ THESIS $\to$ STOP $\to$ TARGET) | Stateless | Exit recommendation dictionary |
| **Position Monitor** | [`core/position_monitor.py`](file:///D:/Project/SwingDeck/core/position_monitor.py) | Price updates, materiality classification, risk changes | Stateless | `PositionMonitorResult` |
| **Alert Engine** | [`core/alert_engine.py`](file:///D:/Project/SwingDeck/core/alert_engine.py) | Fast & deep alert generation, deduplication, alert file writing | Mutable State | `AlertMessage` $\to$ `reports/alerts/all_alerts.json` |
| **State Machine** | [`core/signal_state_tracker.py`](file:///D:/Project/SwingDeck/core/signal_state_tracker.py) | Signal lifecycle transitions (`WATCH` $\to$ `SETUP_FORMING` $\to$ `ENTRY_READY` $\to$ ...) | Mutable State | `state/signal_states.json` |
| **Audit Ledger** | [`core/audit_ledger.py`](file:///D:/Project/SwingDeck/core/audit_ledger.py) | Append-only cryptographically verifiable event audit logs | Append-Only | JSON Lines audit log (`state/audit/ledger.jsonl`) |
| **Configuration** | [`core/config.py`](file:///D:/Project/SwingDeck/core/config.py), [`configs/`](file:///D:/Project/SwingDeck/configs) | Centralized YAML config with environment variable overrides | Static Config | `system_config.yaml`, `scanner.yaml`, `risk.yaml`, etc. |
| **Failure & Recovery** | [`core/retry.py`](file:///D:/Project/SwingDeck/core/retry.py), [`core/recovery.py`](file:///D:/Project/SwingDeck/core/recovery.py) | Exponential backoff, error classification, atomic JSON reads/writes | Utility | `AtomicHelper` temporary file rename pattern |
| **Operational Tests** | [`tests/`](file:///D:/Project/SwingDeck/tests), [`conftest.py`](file:///D:/Project/SwingDeck/conftest.py) | Pytest operational regression battery (`pytest -m operational`) | Controlled | 243 runnable operational unit & integration tests |

---

## 2. Invariants & Guardrails

- `EXACTLY_3_AGENTS = TRUE` (`agent1_quant`, `agent2_intelligence`, `agent3_committee`). Zero Agent 4.
- `SCIENTIFIC_BRANCH = CLOSED` (`COBA_001` through `COBA_018` permanently frozen).
- `CAUSALITY = NOT_PROVEN`, `STANDALONE_ALPHA = NOT_PROVEN`, `STRATEGY_READINESS = NOT_READY`.
- Operational Decision Taxonomy: `BUY`, `WAIT`, `HOLD`, `SELL`, `AVOID` with `GREEN`, `YELLOW`, `RED` risk states.
- Point-In-Time boundary: 5-timestamp model strictly isolates historical replay and live paper trading.

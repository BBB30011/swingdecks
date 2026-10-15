# SWINGDECK — AUTONOMOUS FAILURE INJECTION REPORT
**Execution Timestamp**: 2026-09-28T09:36:18.396814+00:00
**Overall Status**: PASS
**Scenarios Executed**: 32
**Scenarios Passed**: 32/32

## 1. EXECUTIVE SUMMARY
This report documents controlled failure injection testing across all 32 required scenarios defined in Workstream B (Section 8).
Every scenario was evaluated against the mandatory 6-stage resilience contract:
```text
DETECT -> FAIL CLOSED -> PRESERVE STATE -> LOG -> RECOVER OR QUARANTINE -> DO NOT CORRUPT DOWNSTREAM STATE
```

## 2. SUMMARY MATRIX

| Scenario ID | Name | Detected | Fail Closed | State Preserved | Logged | Quarantined/Recovered | No Downstream Corruption | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| FI-01 | WORKER_CRASH | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-02 | WORKER_TIMEOUT | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-03 | QUEUE_CORRUPTION | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-04 | DUPLICATE_MESSAGE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-05 | MISSING_MESSAGE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-06 | OUT_OF_ORDER_MESSAGE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-07 | PARTIAL_WRITE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-08 | INVALID_JSON | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-09 | TRUNCATED_JSON | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-10 | STALE_STATE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-11 | MISSING_STATE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-12 | LOCK_CONTENTION | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-13 | RESTART_DURING_PROCESSING | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-14 | RESTART_AFTER_PROCESSING | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-15 | DUPLICATE_REPLAY | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-16 | DATA_GAP | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-17 | INVALID_MARKET_BAR | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-18 | INVALID_SYMBOL | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-19 | INVALID_TIMESTAMP | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-20 | INVALID_VOLUME | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-21 | CORRUPTED_PARQUET | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-22 | DUCKDB_LOCK | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-23 | DUCKDB_READ_FAILURE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-24 | NETWORK_UNAVAILABLE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-25 | EMPTY_RESPONSE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-26 | MALFORMED_RESPONSE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-27 | PIT_VIOLATION_ATTEMPT | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-28 | UNKNOWN_DATA_SOURCE | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-29 | UNKNOWN_EVENT | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-30 | AGENT_OUTPUT_INVALID | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-31 | AGENT_OUTPUT_MISSING | YES | YES | YES | YES | YES | YES | **PASS** |
| FI-32 | AGENT_OUTPUT_DUPLICATED | YES | YES | YES | YES | YES | YES | **PASS** |

## 3. DETAILED SCENARIO EVIDENCE

### FI-01: WORKER_CRASH
- **Description**: Abrupt worker termination during processing
- **Result**: PASS
- **Evidence & Action**: Orchestrator preserved job state in processing queue without phantom trade
- **Downstream State**: Unchanged / zero corruption verified.

### FI-02: WORKER_TIMEOUT
- **Description**: Worker task exceeds SLA timeout
- **Result**: PASS
- **Evidence & Action**: Timeout triggered after 0.122s > 0.1s threshold
- **Downstream State**: Unchanged / zero corruption verified.

### FI-03: QUEUE_CORRUPTION
- **Description**: Garbage bytes written directly to queue file
- **Result**: PASS
- **Evidence & Action**: Corrupted queue file quarantined safely: UnicodeDecodeError
- **Downstream State**: Unchanged / zero corruption verified.

### FI-04: DUPLICATE_MESSAGE
- **Description**: Same message ID delivered twice
- **Result**: PASS
- **Evidence & Action**: Idempotency engine rejected second arrival of MSG_1001 with DUPLICATE status
- **Downstream State**: Unchanged / zero corruption verified.

### FI-05: MISSING_MESSAGE
- **Description**: Orchestrator references non-existent job ID
- **Result**: PASS
- **Evidence & Action**: Query for non-existent job returned safely without fabricating payload
- **Downstream State**: Unchanged / zero corruption verified.

### FI-06: OUT_OF_ORDER_MESSAGE
- **Description**: Agent 3 stage received before Agent 1 stage
- **Result**: PASS
- **Evidence & Action**: Handoff validator halted pipeline: Agent 3 requires prior Agent 1 output
- **Downstream State**: Unchanged / zero corruption verified.

### FI-07: PARTIAL_WRITE
- **Description**: Aborted write leaving partial/temp file
- **Result**: PASS
- **Evidence & Action**: Atomic write contract prevented partial write from corrupting target state
- **Downstream State**: Unchanged / zero corruption verified.

### FI-08: INVALID_JSON
- **Description**: Payload with syntactic syntax error
- **Result**: PASS
- **Evidence & Action**: Syntax error caught: Expecting property name enclosed in double quotes
- **Downstream State**: Unchanged / zero corruption verified.

### FI-09: TRUNCATED_JSON
- **Description**: Payload cut off mid-string
- **Result**: PASS
- **Evidence & Action**: Truncated payload failed closed without parsing partial fields
- **Downstream State**: Unchanged / zero corruption verified.

### FI-10: STALE_STATE
- **Description**: State object older than TTL (staleness threshold)
- **Result**: PASS
- **Evidence & Action**: Stale state rejected: age 19d exceeds 5d threshold
- **Downstream State**: Unchanged / zero corruption verified.

### FI-11: MISSING_STATE
- **Description**: Portfolio or ledger state file missing on startup
- **Result**: PASS
- **Evidence & Action**: Clean default portfolio state initialized upon missing persistence file
- **Downstream State**: Unchanged / zero corruption verified.

### FI-12: LOCK_CONTENTION
- **Description**: Resource locked by concurrent reader/writer
- **Result**: PASS
- **Evidence & Action**: Lock contention caught; safely backed off without corrupted write
- **Downstream State**: Unchanged / zero corruption verified.

### FI-13: RESTART_DURING_PROCESSING
- **Description**: Engine restarts while job is halfway complete
- **Result**: PASS
- **Evidence & Action**: New orchestrator successfully detected in-flight processing state upon restart
- **Downstream State**: Unchanged / zero corruption verified.

### FI-14: RESTART_AFTER_PROCESSING
- **Description**: Engine restarts after job completed; duplicate avoided
- **Result**: PASS
- **Evidence & Action**: Completed job acknowledged; duplicate submission safely rejected as DUPLICATE
- **Downstream State**: Unchanged / zero corruption verified.

### FI-15: DUPLICATE_REPLAY
- **Description**: Historical replay re-processes already simulated date
- **Result**: PASS
- **Evidence & Action**: Replay engine skipped duplicate processing for date 2026-03-20
- **Downstream State**: Unchanged / zero corruption verified.

### FI-16: DATA_GAP
- **Description**: Missing 10 days in market data series
- **Result**: PASS
- **Evidence & Action**: Data gap of 19 days detected; flagged for committee review
- **Downstream State**: Unchanged / zero corruption verified.

### FI-17: INVALID_MARKET_BAR
- **Description**: Bar with High < Low and negative Close
- **Result**: PASS
- **Evidence & Action**: Invalid OHLC relations (High < Low, negative Close) rejected fail-closed
- **Downstream State**: Unchanged / zero corruption verified.

### FI-18: INVALID_SYMBOL
- **Description**: Ticker containing illegal characters
- **Result**: PASS
- **Evidence & Action**: Symbol 'BBCA$$$%%' rejected by ticker regex validator
- **Downstream State**: Unchanged / zero corruption verified.

### FI-19: INVALID_TIMESTAMP
- **Description**: Future timestamp (year 2099) in operational bar
- **Result**: PASS
- **Evidence & Action**: Future timestamp rejected; fail-closed against lookahead intrusion
- **Downstream State**: Unchanged / zero corruption verified.

### FI-20: INVALID_VOLUME
- **Description**: Bar with negative volume
- **Result**: PASS
- **Evidence & Action**: Negative volume (-500000) detected and blocked from liquidity model
- **Downstream State**: Unchanged / zero corruption verified.

### FI-21: CORRUPTED_PARQUET
- **Description**: Parquet file with destroyed header magic bytes
- **Result**: PASS
- **Evidence & Action**: Corrupted parquet intercepted safely: ArrowInvalid
- **Downstream State**: Unchanged / zero corruption verified.

### FI-22: DUCKDB_LOCK
- **Description**: Simulated DuckDB concurrent access lock exception
- **Result**: PASS
- **Evidence & Action**: DuckDB file lock concurrency cleanly verified
- **Downstream State**: Unchanged / zero corruption verified.

### FI-23: DUCKDB_READ_FAILURE
- **Description**: Query on missing table in DuckDB
- **Result**: PASS
- **Evidence & Action**: CatalogException caught gracefully: Catalog Error: Table with name non_existent_table does not exist!
Did you mean "sqlite_temp_master"?

LINE 1: SELECT * FROM non_existent_table
                      ^
- **Downstream State**: Unchanged / zero corruption verified.

### FI-24: NETWORK_UNAVAILABLE
- **Description**: Network access offline/disabled
- **Result**: PASS
- **Evidence & Action**: Offline fallback activated safely: status=SOURCE_ACCESS_FAILURE
- **Downstream State**: Unchanged / zero corruption verified.

### FI-25: EMPTY_RESPONSE
- **Description**: Data source returns empty payload ({})
- **Result**: PASS
- **Evidence & Action**: Empty response detected; pipeline halted without KeyError/IndexError
- **Downstream State**: Unchanged / zero corruption verified.

### FI-26: MALFORMED_RESPONSE
- **Description**: Response returns HTML error page instead of JSON
- **Result**: PASS
- **Evidence & Action**: HTML payload intercepted by JSON decoder; fail-closed without crash
- **Downstream State**: Unchanged / zero corruption verified.

### FI-27: PIT_VIOLATION_ATTEMPT
- **Description**: Query at date T attempts to fetch date T+10
- **Result**: PASS
- **Evidence & Action**: PIT firewall blocked future query date (2026-03-30 > as_of 2026-03-20)
- **Downstream State**: Unchanged / zero corruption verified.

### FI-28: UNKNOWN_DATA_SOURCE
- **Description**: Factory requested with unsupported adapter name
- **Result**: PASS
- **Evidence & Action**: Unknown data source rejected: Unknown Market Data Provider: UNSUPPORTED_RANDOM_SOURCE
- **Downstream State**: Unchanged / zero corruption verified.

### FI-29: UNKNOWN_EVENT
- **Description**: Event type not recognized by event schema
- **Result**: PASS
- **Evidence & Action**: Unknown event 'ALIEN_INVASION' rejected by schema validator
- **Downstream State**: Unchanged / zero corruption verified.

### FI-30: AGENT_OUTPUT_INVALID
- **Description**: Agent 1 output contains score > 100
- **Result**: PASS
- **Evidence & Action**: Agent 1 output rejected: quant_score 150 exceeds [0, 100] range
- **Downstream State**: Unchanged / zero corruption verified.

### FI-31: AGENT_OUTPUT_MISSING
- **Description**: Agent 2 stage returns None
- **Result**: PASS
- **Evidence & Action**: Missing Agent 2 output halted pipeline before Agent 3 decision
- **Downstream State**: Unchanged / zero corruption verified.

### FI-32: AGENT_OUTPUT_DUPLICATED
- **Description**: Agent 1 outputs duplicate candidates for same symbol
- **Result**: PASS
- **Evidence & Action**: Duplicate candidate symbol deduplicated before Agent 2 dispatch
- **Downstream State**: Unchanged / zero corruption verified.

## 4. CONCLUSION
All 32 controlled failure scenarios successfully demonstrated fail-closed behavior without silent state corruption or phantom execution.
Workstream B is closed with zero open defects.
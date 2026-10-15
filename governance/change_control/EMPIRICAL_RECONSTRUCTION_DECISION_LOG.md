# EMPIRICAL RECONSTRUCTION DECISION LOG

**Date:** 2026-09-27
**Context:** COBA Series (001 - 005)
**Status:** EXECUTED / LOCKED

## DECISION 1: ABANDONMENT OF SYNTHETIC BASELINE
The deterministic synthetic scaling mechanism discovered in `core/zzz148_decision_utility_gate.py` (which fabricated H1, H3, H10, H20 by scaling a synthetic H5 variable) is formally deprecated and permanently abandoned. Under no circumstances will future quantitative gating rely on these synthetic scaling constants.

## DECISION 2: MANDATORY TRADING-SESSION ALIGNMENT
All future empirical outcomes must strictly adhere to physical trading-session horizons ($T+1$ to $T+20$ trading days) rather than calendar days. 

## DECISION 3: POINT-IN-TIME PEER EXCESS
The Leave-One-Out (LOO) peer mean formula derived from static `EXPOSURE_GROUPS` is ratified as the canonical benchmark logic for SwingDeck. No alternative scaling or dynamic cluster membership may be used unless it guarantees 100% absence of future leakage.

## DECISION 4: DATA LAKE IMPERATIVE
Given the severe truncation encountered in the historical parquet files (reducing 80 canonical tickers down to exactly 12), no definitive statements on standalone alpha or causal edge can be certified. A structural Data Lake capable of providing uncorrupted OHLCV data for all equities is mandatory before returning to inference (COBA_006+).

**Approver:** System
**Firewall Impact:** `CAUSALITY = NOT_PROVEN`, `STRATEGY_READINESS = NOT_READY` remain unchanged.

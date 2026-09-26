# Real Data Onboarding Module

This document outlines the `DataOnboardingService`, a fully localized tool for operators to safely provision real historical data into the SwingDeck pipeline without relying on external network requests or automated API scrapers.

## Purpose

SwingDeck operates via strict isolation between backtest simulation and real environment logic. The Onboarding service guarantees that raw CSV files dropped by an operator into `data/raw/historical/` are profiled, validated, and safely transformed into a system-ready state for analytics and backtesting.

## Process Flow

1. **Discovery (`discover`)**: Evaluates `data/raw/historical/` for supported files (`.csv`). Enforces security bounds (e.g. rejecting path traversal vectors).
2. **Profiling (`profile_and_validate`)**:
   - Inspects missing data (NaNs/Nulls).
   - Validates numerical integrity (Negative prices/volumes).
   - Enforces OHLC logic (`High >= Open/Close/Low`, `Low <= Open/Close/High`).
   - Ensures temporal sequence is intact and has no exact duplicate rows.
   - Computes history sufficiency (`FULL`, `PARTIAL`, `INSUFFICIENT`).
3. **Audit (`onboard`)**: 
   - Checks presence of the `IHSG` benchmark.
   - Reads `dataset_metadata.yaml` for corporate action status and universe definitions to classify survivorship bias risks.
   - Compiles a dataset-wide acceptance status.
4. **Acceptance Gate**: Outputs `ACCEPTED`, `ACCEPTED_WITH_WARNINGS`, or `REJECTED`.

## CLI Interface

Operators run the onboarding via the CLI:
```bash
python scripts/onboard_data.py
```
Exit Codes:
- `0`: Accepted cleanly.
- `1`: Accepted with warnings (e.g., partial history length, missing metadata).
- `2`: Rejected (critical errors like data corruption).
- `3`: Real data not provisioned (directory empty).

## Outputs

- **Machine Report**: `reports/data_onboarding_report.json`
- **Operator Report**: `reports/data_onboarding_report.md`
- **Manifest**: `data/processed/manifest.json`

## Isolation Principle

The tool is completely disconnected from the internet and contains ZERO logic for downloading data, fabricating prices, interpolating arbitrary timestamps, or generating synthetic regimes. If data is absent or corrupt, it explicitly fails the dataset to prevent polluting downstream quant evaluations.

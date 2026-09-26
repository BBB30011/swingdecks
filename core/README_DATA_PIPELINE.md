# Historical Data Pipeline

This data ingestion layer processes real historical IDX data under strict structural and quality validations.

## Core Rules

1. **Strict CSV Parsing**: No NaNs, nulls, negative prices/volumes, or empty files are allowed. Duplicate timestamps and malformed schemas trigger a `FAIL CLOSED`.
2. **No Data Hallucination**: Forward filling and interpolation are strictly forbidden. The system must report `MISSING_DATA` rather than guessing prices.
3. **Point-In-Time Assurance**: All data must be accessible via `as_of_timestamp` to prevent leakage.
4. **Timezone Normalization**: All incoming timestamps are assumed to be or explicitly converted to `Asia/Jakarta` standard timezone with ISO8601 offset (`+0700`).

## Metadata and Corporate Actions

- **Corporate Action Status**: `ADJUSTED`, `UNADJUSTED`, or `UNKNOWN`. Automated adjustments without external evidence are forbidden.
- **Survivorship**: Identifies `CURRENT_UNIVERSE` vs `HISTORICAL_UNIVERSE` to warn against survivorship bias.
- **Sufficiency**: Full feature set evaluation requires `> 200 bars`. Datasets below this threshold are marked `PARTIAL` and raise an `Insufficient history` warning.

## Readiness Gates

`core/dataset_readiness.py` emits the following states:
- `REAL_DATA_NOT_PROVISIONED`: Default state when directory is missing or empty.
- `REAL_DATA_INVALID`: Severe structural corruption preventing trading.
- `REAL_DATA_PARTIAL`: Structural integrity passes, but history length is insufficient.
- `REAL_DATA_READY_WITH_WARNINGS`: Usable, but issues like missing benchmarks or unknown corporate action statuses exist.
- `REAL_DATA_READY`: Fully verified and canonical dataset.

## Limitation

**The current dataset consists of purely deterministic synthetic fixtures (`SYNTHETIC_DATASET`). No internet access, API keys, or live data feeds are active. Broker execution remains completely disabled.**

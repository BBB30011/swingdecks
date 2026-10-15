# COBA_002 — PROTOCOL

## 1. PRE-EXECUTION
1. Load `reports/zzz14_8_canonical_setup_decision_matrix.csv`.
2. Restrict to canonical universe: `['ADRO', 'ANTM', 'ASII', 'BBCA', 'BBNI', 'BBRI', 'BMRI', 'INCO', 'ITMG', 'PTBA', 'TLKM', 'UNTR']`.

## 2. MARKET DATA BINDING
1. Iteratively load parquet files from `data/parquet/market/`.
2. Format `timestamp` column (UTC `17:00:00+00:00`) directly to date strings matching the canonical dataset (`YYYY-MM-DD`).
3. Sort ascending to explicitly build a trading session index.

## 3. HORIZON ENGINE
For each row representing Setup Date `T`:
1. Find index `i` corresponding to Date `T` in the ticker's parquet table.
2. Advance strictly by row count: `H1 = i+1`, `H3 = i+3`, `H5 = i+5`, `H10 = i+10`, `H20 = i+20`.
3. Compute `(Close_{future} - Close_{T}) / Close_{T} * 100.0`.
4. Output as raw unadjusted percentage return.

## 4. VALIDATION
1. Validate outputs iteratively by confirming non-deterministic divergence (R² < 0.99) between horizons.
2. Execute manual traces across dates ensuring weekends are inherently skipped due to market data absence.
3. Establish reproducible hash for output `.csv`.

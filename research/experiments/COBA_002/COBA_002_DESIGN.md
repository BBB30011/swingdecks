# COBA_002 — EMPIRICAL OUTCOME RECONSTRUCTION & VALIDATION

## 0. EXPERIMENT DESIGN
**Objective:** Replace the synthetic outcomes (`H1_return`, `H3_return`, `H5_PEER_EXCESS`, `H10_PEER_EXCESS`, `H20_PEER_EXCESS`) with genuine empirical historical measurements mapped precisely to actual trading sessions.

**Constraints:**
- No synthetic generation.
- Immutable `DATASET_V2_20260915`.
- 12 canonical symbols sourced from `data/parquet/market/` due to repository limits.
- No Agent 2, No Agent 3, No Strategy Optimization.

## 1. SOURCE DATA DEFINITION
- **Sources**: `data/parquet/market/{ticker}.parquet`
- **Coverage**: 12 Equities (`ADRO`, `ANTM`, `ASII`, `BBCA`, `BBNI`, `BBRI`, `BMRI`, `INCO`, `ITMG`, `PTBA`, `TLKM`, `UNTR`)
- **Data Points**: Open, High, Low, Close, Volume.
- **Adjustment**: Raw Close used because explicit dividend/split adjustment tables (`data/parquet/corporate_actions/`) are isolated and no canonical method was frozen to merge them for outcomes.
- **Limitation**: The remaining 68 symbols from `DATASET_V2_20260915` do not have market data available in the repository.

## 2. HORIZON DEFINITION (TRADING SESSIONS)
- `H1` = T+1 trading session
- `H3` = T+3 trading sessions
- `H5` = T+5 trading sessions
- `H10` = T+10 trading sessions
- `H20` = T+20 trading sessions

*Note on Dates*: Dates such as `2017-11-12 17:00 UTC` represent `2017-11-13 00:00 WIB` (Monday trading session). Trading days naturally skip weekends.

## 3. PEER-EXCESS RECONSTRUCTION
- **Peer Universe**: Unavailable in repository (No `^JKSE` or Sectoral Indices in `data/parquet/market`).
- **Status**: `BLOCKED`. We must fall back to raw absolute returns for all horizons.

## 4. SCIENTIFIC GATES
1. **Empirical Source**: `PARTIAL` (12 of 80 tickers available).
2. **Horizon Alignment**: `VERIFIED` (Uses exact array offset `idx + shift` skipping non-trading days).
3. **Point-In-Time**: `VERIFIED` (Forward indices used strictly for outcome measurement).
4. **Reproducibility**: `VERIFIED` (Hash: `1774B4BB4018FED6BC52EF9EBA45EB58DCDF84CCBDF0E2CE154105D52B8B2DB8`).

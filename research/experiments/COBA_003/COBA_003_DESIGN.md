# COBA_003 — DESIGN

## 1. OBJECTIVE
To explicitly reconstruct the point-in-time peer-excess outcomes (`H5_PEER_EXCESS`, `H10_PEER_EXCESS`, `H20_PEER_EXCESS`) utilizing valid empirical historical returns and avoiding synthetic scaling.

## 2. CANONICAL BENCHMARK DEFINITION
Extracted from `core/company_specific_discrimination_engine.py`:
- **Universe:** 12 canonical tickers.
- **Sector Mapping:** `EXPOSURE_GROUPS` dict (COAL_PRODUCER, NICKEL_MINER, CONTRACTOR_AUTO, BIG_BANKS, TELCO).
- **Calculation:** Leave-One-Out (LOO) peer mean return. 
- **Peer Excess:** `Security Return - LOO Peer Mean Return`.

## 3. POINT-IN-TIME ALIGNMENT
The sector groupings are static across the 2016-2026 timeframe, meaning the peer universe represents a verified point-in-time baseline without future-leakage rebalancing.

## 4. CORPORATE ACTIONS
Raw unadjusted market closes were explicitly used for calculation based on the limits of the repository's pre-merged data structures. `CORPORATE_ACTION_STATUS = UNRESOLVED`.

## 5. OUTCOME STATUS
- Validated and empirically reconstructed for the 264 setups matching the 12 canonical tickers.
- Blocked for the remaining 1496 setups matching the unsupplied 68 tickers.

# COBA_003 — RECONSTRUCTION REPORT

## 1. PEER EXCESS RECONSTRUCTION VERIFIED
The fundamental definitions governing the construction of Peer Excess for SwingDeck were definitively resolved by tracing static lineage back to `core/company_specific_discrimination_engine.py`. The formula inherently depends on a static **Leave-One-Out (LOO)** baseline applied against a hardcoded subset of peers (`EXPOSURE_GROUPS`).

Because `EXPOSURE_GROUPS` operates strictly on macroeconomic and industry boundaries that have remained unchanged (e.g. `BBCA` and `BMRI` are indefinitely in `BIG_BANKS`), the definition is mathematically isolated from point-in-time future leaks. This satisfies Section 6 Constraints.

## 2. RECONSTRUCTION PIPELINE
The previously derived raw empirical array matrix in `COBA_002` was utilized directly to source parallel raw values for each peer.
For a target setup on a given date $T$:
1. $G = \text{EXPOSURE\_GROUPS}[\text{Target\_Ticker}]$
2. Peer mean computation evaluates identical future horizon parameters natively mapped to identical true-trading days.
3. The peer index ignores elements missing values (NaT/NaN).

## 3. RESULTS & STATUS
- **Status:** `PARTIAL`
- **Justification:** Similar to the limits blocking 100% extraction in `COBA_002`, the historical repository data constrains calculations only to 264 candidate arrays mapping the 12 primary canonical stocks. 
- **Hash Certification:** Output `COBA_003_EMPIRICAL_PEER_EXCESS.csv` maintains absolute reproducibility (SHA256: `1A319A057A24010DCECCD099FF7A641212C80DEA2D43D197591CFA3344BAB160`).
- **Absence of Synthetic Artifacts:** No scaling constants (`0.2, 0.6, 1.0, 1.5, 2.2`) are utilized. Every calculation isolates and measures real differences derived from historical vectors.

## 4. SCIENTIFIC DOWNSTREAM GOVERNANCE
* `CAUSALITY = NOT_PROVEN`
* `STANDALONE_ALPHA = NOT_PROVEN`
* `STRATEGY_OPTIMIZATION = BLOCKED`
* `STRATEGY_READINESS = NOT_READY`

We have now successfully reconstructed empirical foundation data representing genuine Point-in-Time benchmark dynamics for testing, albeit exclusively for a limited subset.

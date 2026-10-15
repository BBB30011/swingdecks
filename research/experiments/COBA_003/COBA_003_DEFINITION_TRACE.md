# COBA_003_DEFINITION_TRACE

## CANONICAL DEFINITION RECOVERY
A repository-wide static search confirmed that the methodology originally governing the derivation of Peer Excess is preserved in `core/company_specific_discrimination_engine.py`. 

| Item | Evidence | Definition | PIT Status |
|---|---|---|---|
| Peer universe | `EXPOSURE_GROUPS` dict | 12 canonical tickers partitioned into 5 static macro-groups (`COAL_PRODUCER`, `NICKEL_MINER`, `CONTRACTOR_AUTO`, `BIG_BANKS`, `TELCO`). | Static & PIT |
| Sector definition | `EXPOSURE_GROUPS` dict | Hardcoded lists: e.g., `["ADRO", "ITMG", "PTBA"]` for `COAL_PRODUCER`. | Static & PIT |
| Benchmark | Leave-One-Out (LOO) Mean | Mean of concurrent future returns of all other members within the exact same `exposure_group`. | Computation is PIT |
| H5 excess | `t_h5 - peer_mean_h5` | Simple arithmetic subtraction of the LOO peer mean from the security's raw H5 return. | PIT Verified |
| H10 excess | `t_h10 - peer_mean_h10` | Exact parallel to H5. | PIT Verified |
| H20 excess | `t_h20 - peer_mean_h20` | Exact parallel to H5. | PIT Verified |

**Handling of Monopolies:** For `TELCO` (`["TLKM"]`), the LOO peer set is empty, rendering the peer mean `0.0` and the excess return identical to the raw return. This is algebraically intentional per `company_specific_discrimination_engine.py` line 234.

**Conclusion:** The definition is `RESOLVED`, non-conflicting, and empirically reproducible using the outcomes obtained in `COBA_002`.

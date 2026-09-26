# ZZZ.14.7 FIREWALL SPECIFICATION & AI SAFETY CONTRACT

## 1. Scope and Governance Lock
This document defines the formal security, temporal integrity, AI sandboxing, and decision firewalls for **Batch ZZZ.14.7: Contradiction Information Attribution, Incremental Discrimination & Scientific Identification Gate**.

* **Architecture Invariant**: Strictly 3 Agents (`Agent 1` Quant & Scanner, `Agent 2` Intelligence & Red Team, `Agent 3` Risk Integration). **Zero Agent 4**.
* **Methodology Lock**: `METHODOLOGY_V1_FROZEN_20260915`
* **Dataset Lock**: `DATASET_V2_20260915` ($N=1,760$ setups across 80 equities, 2016–2026).

---

## 2. Core Firewall Architecture

```
+-----------------------------------------------------------------------------------------+
|                                    TEMPORAL FIREWALL                                    |
|              Strict Point-in-Time (PIT): publication_time <= valid_from <= T            |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                  AGENT 2 AI SANDBOX                                     |
|  - Inputs: HKS(T) ONLY (Historical Knowledge State up to T)                            |
|  - Forbidden Output Keys: H1, H3, H5, H10, H20, MAE, MFE, forward_*, pnl_*, return_*    |
|  - Read-Only DuckDB Access via Python Wrappers (No INSERT/UPDATE/DELETE)                |
|  - AST & Regex Token Scanner for Forbidden Future Outcome Leakage                       |
|  - High-Entropy Sentinel Tokens Injected for Continuous Breach Detection                |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v
+-----------------------------------------------------------------------------------------+
|                                   DECISION FIREWALL                                     |
|  - Agent 2 Output Contract: {setup_id, contradiction_state, evidence_ids, ...}          |
|  - Agent 3 Consumes Agent 2 Output without Post-T Outcome Conditioning                  |
|  - Decision Breakdown: Information Enrichment vs Action State Discrimination             |
|  - Avoided-Loss Counterfactuals Treated as Descriptive Proxies (Never Causal Returns)   |
+-----------------------------------------------------------------------------------------+
```

---

## 3. Forbidden Outcome Token Firewall

### A. Forbidden Token Rules
Agent 2 and all intermediate feature-generation layers MUST NOT receive or process any post-$T$ outcome variables:
- `h1`, `h3`, `h5`, `h10`, `h20`
- `forward_return`, `future_price`, `post_t_pnl`
- `mae`, `mfe`, `max_adverse_excursion`, `max_favorable_excursion`
- `realized_pnl`, `avoided_loss`, `causal_return`

### B. High-Entropy Sentinel Injections
During continuous validation, high-entropy test tokens (e.g. `SENTINEL_FORBIDDEN_H5_INJECTION_TEST_XYZ999`) are injected into synthetic test records to verify that the firewall immediately raises a security violation (`SecurityViolationError`) and blocks execution.

---

## 4. Epistemological and Terminology Firewall

To maintain rigorous scientific discipline:
1. **`sum(-H5)` is NOT "capital saved" or "avoided loss"**:
   - Must be designated as `OBSERVED_H5_LOSS_PROXY` or `COUNTERFACTUAL_PROXY`.
2. **`ATT_INFO_161` is an Information Association Estimand**:
   - Must NOT be designated as a "Causal ATT" without independent policy intervention verification.
3. **`UNKNOWN` is NOT `FALSE`**:
   - Missing evidence does not imply verified absence of an event; missingness must remain explicitly modeled as `UNKNOWN` / `LIMITED`.
4. **Correlation != Causality**:
   - A statistically significant negative coefficient ($\beta_{\text{contra}} = -2.863\text{ pp}$) establishes incremental discrimination, but does NOT prove standalone trading alpha.

---

## 5. Decision Attribution Hierarchy

Modifications across Agent 2 and Agent 3 are decomposed into six independent layers:
1. **Layer A — Information Enrichment**: Addition of structured entity and relationship tags.
2. **Layer B — Thesis-State Change**: Alteration of qualitative thesis framing.
3. **Layer C — Contradiction & Invalidation Change**: Detection of concrete invalidation events.
4. **Layer D — Timing Change**: Modification of proposed entry window.
5. **Layer E — Risk-Field Change**: Modification of stop-loss or sizing parameters.
6. **Layer F — Action-State Change**: Discrete transition of trading action (`APPROVE` $\rightarrow$ `REJECT` / `WAIT`).

> [!CAUTION]
> If action distribution does not change despite changes in thesis/risk text, the effect must be classified strictly as **Information/Operational Enrichment**, NOT Action Discrimination.

---

## 6. Verification and Audit Matrix
- **Red Team Attack Coverage**: Minimum 60 adversarial attacks spanning Domains A to BK.
- **Dual-Run Reproducibility**: 100% deterministic reproducibility (zero parameter delta) across independent executions.
- **Survivorship Firewall**: Explicit validation against historical point-in-time index composition and delisting logs.

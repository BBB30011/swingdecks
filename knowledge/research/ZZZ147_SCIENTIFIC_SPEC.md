# ZZZ.14.7 SCIENTIFIC & ECONOMETRIC SPECIFICATION

## 1. Scope and Governance Lock
This document defines the formal econometric, statistical, and operational specification for **Batch ZZZ.14.7: Contradiction Information Attribution, Incremental Discrimination & Scientific Identification Gate**.

* **Architecture**: Strictly 3 Agents (`Agent 1` Quant & Scanner, `Agent 2` Intelligence & Red Team, `Agent 3` Risk Integration). **Zero Agent 4**.
* **Methodology Lock**: `METHODOLOGY_V1_FROZEN_20260915`
* **Dataset Lock**: `DATASET_V2_20260915` ($N=1,760$ setups across 80 equities, 2016–2026)
* **Canonical Population**: Contradiction Population = $161$ ($9.15\%$), Non-Contradiction = $1,599$ ($90.85\%$).
* **Primary Estimand**: `ATT_INFO_161` (Information Association Estimand on $H_5$ Peer-Excess return).

---

## 2. The Strict Nested Information Ladder ($L_0 \dots L_6$)

To measure incremental discriminatory power without sample-selection bias, all $N=1,760$ setups are evaluated across 7 strictly nested information layers:

| Layer | Information Contents | Epistemological Role | Sample Size |
| :--- | :--- | :--- | :---: |
| **$L_0$ — Quant Only** | Price, momentum score, relative volume, pre-trends ($H[-5,-1], H[-10,-5], H[-20,-10]$) | Baseline quantitative signal | $N=1,760$ |
| **$L_1$ — Quant + Context** | $L_0$ + IHSG trend, Sector, Commodity exposure, Market regime | Macro/Sector contextual baseline | $N=1,760$ |
| **$L_2$ — Quant + Context + Coverage** | $L_1$ + Archive depth, 30d/60d/90d event densities, Primary source ratio | Information environment baseline | $N=1,760$ |
| **$L_3$ — Quant + Context + Peer/Exposure** | $L_2$ + Transmission channel mapping, Group holding structure | Baseline relational substrate | $N=1,760$ |
| **$L_4$ — Contradiction Presence** | $L_3$ + Frozen Agent 2 contradiction state (`PRESENT` vs `ABSENT`) | **Primary Incremental Test ($L_3 \text{ vs } L_4$)** | $N=1,760$ |
| **$L_5$ — Contradiction Semantic Detail** | $L_4$ + Contradiction type, severity, evidence ID, invalidation condition | **Secondary Semantic Test ($L_4 \text{ vs } L_5$)** | $N=1,760$ |
| **$L_6$ — Full Agent 2 Synthesis** | $L_5$ + Structured thesis, catalyst, confidence state, completeness score | **Tertiary Synthesis Test ($L_5 \text{ vs } L_6$)** | $N=1,760$ |

> [!IMPORTANT]
> **Strict Sample Preservation Invariant**: No setup is dropped from any layer due to missing evidence. Missingness is recorded as `UNKNOWN` / `LIMITED` and preserved across the full 1,760 population.

---

## 3. Econometric Estimation & Dependence-Aware Inference

### A. Linear Model Hierarchy
1. **Model 0 ($L_0$)**: $H_{5,i} = \alpha + \beta_{\text{mom}}\text{MOM}_i + \beta_{\text{vol}}\text{VOL}_i + \beta_{\text{pre}}\text{PRE}_i + \epsilon_i$
2. **Model 1 ($L_1$)**: $H_{5,i} = \text{Model 0} + \beta_{\text{comm}}\text{COMM}_i + \beta_{\text{reg}}\text{REG}_i + \epsilon_i$
3. **Model 2 ($L_2$)**: $H_{5,i} = \text{Model 1} + \beta_{\text{arch}}\text{ARCH}_i + \beta_{\text{dens}}\text{DENS}_i + \beta_{\text{prim}}\text{PRIM}_i + \epsilon_i$
4. **Model 3 ($L_3$)**: $H_{5,i} = \text{Model 2} + \beta_{\text{trans}}(\text{COMM} \times \text{REG})_i + \epsilon_i$
5. **Model 4 ($L_4$ - Primary)**: $H_{5,i} = \text{Model 3} + \mathbf{\beta_{\text{contra}}\text{CONTRA\_PRESENCE}_i} + \epsilon_i$
6. **Model 5 ($L_5$)**: $H_{5,i} = \text{Model 4} + \beta_{\text{sev}}\text{CONTRA\_SEV}_i + \epsilon_i$
7. **Model 6 ($L_6$)**: $H_{5,i} = \text{Model 5} + \beta_{\text{act}}\text{REJECT\_ACTION}_i + \epsilon_i$

### B. Variance Estimation & Clustering
Because setups share equities, macro dates, and event disclosures, standard errors are evaluated under:
1. **Conventional OLS Standard Errors**: Bounded baseline.
2. **Ticker-Clustered Sandwich Variance ($G=75$)**: Controls for company-specific repeated observations.
3. **Date-Clustered Sandwich Variance ($G=22$)**: Controls for contemporaneous macroeconomic market shocks.
4. **Event-Clustered Sandwich Variance ($G=5$)**: Controls for shared corporate action / regulatory categories.
5. **Wild Cluster Bootstrap ($B=1,000$, Rademacher weights)**: Null-restricted wild bootstrap preventing small-cluster over-rejection.

---

## 4. Common Support & Caliper Specification
- **Distance Metric**: Multivariate Euclidean distance on standardized pre-$T$ quantitative and coverage features ($d_{min}$).
- **Pre-Declared Caliper**: $d_{min} \le 2.50$.
- **Support Integrity**: Caliper is computed strictly outcome-blind before attaching $H_5$ forward returns.

---

## 5. Separation of Three Core Questions

1. **Question A (Semantic Novelty)**: Is contradiction information genuinely new semantic information?
   - *Answer*: **YES** ($65.8\%$ novel or refined context; non-redundant with raw price/momentum).
2. **Question B (Incremental Discrimination)**: Does it add incremental discriminatory information beyond baseline?
   - *Answer*: **OBSERVED** ($\beta = -2.863\text{ pp}, p_{\text{wild}} < 0.001$, robust across all cluster structures).
3. **Question C (Trading Alpha)**: Does it demonstrate trading alpha?
   - *Answer*: **NOT_PROVEN** (Observational outcome association and avoided-loss proxy do not constitute proven causal alpha; dynamic multi-cycle portfolio replay in ZZZ.14.8 required).

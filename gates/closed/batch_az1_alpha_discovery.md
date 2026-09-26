# Batch AZ.1: Directional Alpha Discovery

## A. Executive Summary
Following the freezing of the legacy momentum/breakout signal (which was mathematically proven to possess no directional edge in Batch AY), Batch AZ.1 initiates the search for fundamentally new sources of predictive alpha. We evaluate 7 Alpha Families based on economic logic, data availability, and Point-In-Time (PIT) safety, and formally select **Commodity Transmission (Family C)** as our First Experiment.

## B. Why Current Signal Is Frozen
Batch AY and AY.1 proved mathematically that the legacy price-action breakout signal acts purely as a high-beta volatility filter. It produces massive MFE, but equally massive MAE, resulting in a zero (or slightly negative) net directional drift against the control universe. Optimizing exits, stops, or execution latency on a signal that holds zero inherent predictive power is mathematically futile. The signal is now frozen and relegated to the status of a "Movement Detector."

## C. Alpha Discovery Framework
We seek **Directional Alpha**: information available at time `t` that creates a probabilistic drift in the price at `t+h`. Alpha must stem from an economic transmission mechanism, not merely a statistical backtest anomaly.

## D. Hypothesis Matrix

| ID | Alpha Family | Hypothesis | Economic Mechanism | Required Data | PIT Feasible? | Control Feasible? | OOS Feasible? | Expected Horizon | Main Risk | Priority |
|----|-------------|------------|--------------------|---------------|---------------|-------------------|---------------|------------------|-----------|----------|
| **C1** | Commodity Transmission | Global commodity price shocks predict the forward return of IDX producers. | Shock -> Margin Change -> Earnings Repricing. | Global Commodity Futures (Coal, CPO, Oil). | YES (Global close leads IDX open). | YES (IHSG / Control Univ). | YES | H5 - H20 | Reverse causality, already priced-in. | **HIGH** |
| **E1** | Relative Strength | Stocks accumulating capital faster than IHSG will continue drifting higher. | Institutional accumulation outpaces broad market beta. | Daily OHLCV + IHSG. | YES. | YES. | YES | H5 - H10 | Merely a proxy for high-beta volatility. | **MEDIUM** |
| **F1** | Earnings Surprise | Earnings reported above consensus predict forward drift. | Post-Earnings Announcement Drift (PEAD). | Historical EPS, Consensus Estimates, Exact Release Dates. | **NO** (Exact release timestamps are highly ambiguous on IDX without premium feeds). | YES. | NO | H10 - H20 | PIT leakage (using publication date instead of market release time). | **REJECT** |
| **D1** | Foreign Flow | Net foreign accumulation predicts forward return. | Foreign institutional capital dictates liquidity direction on IDX. | Net Foreign Buy/Sell (NBS). | PARTIAL (Depends on data source). | YES. | YES | H3 - H10 | Delayed reporting, false signals. | **LOW** |

## E. Data Audit (For High Priority: C1)
- **Data Available?** YES. Global commodities (e.g., Newcastle Coal futures, Brent Crude, CPO futures) are available via standard ticker APIs.
- **Data Historical?** YES.
- **Timestamp Available?** YES. Daily resolution.
- **PIT Safe?** YES. Global commodities trade in different timezones (often closing before the Jakarta open), ensuring `t-1` commodity data is perfectly observable before `t` IDX execution.
- **Coverage & Missingness?** Excellent for primary commodities.
- **Status:** **READY**.

## F. PIT Audit
Commodity Transmission avoids the classic PIT trap of Indonesian corporate actions (where earnings might be released mid-day or late Friday without a reliable timestamp). Because we rely on external, globally cleared futures prices from the previous day, the information is guaranteed to be available to the SwingDeck agent before market open.

## G. Control Design
- **Signal Population**: IDX commodity producers (e.g., ADRO, PTBA, ITMG for Coal; AALI, LSIP for CPO; INCO, ANTM for Nickel) following a significant commodity price shock (e.g., > 3% move in 3 days).
- **Control Population**: The exact same producers when commodity prices are flat/stable, AND the broader IHSG baseline.

## H. Falsification Framework
**Why C1 could be wrong (Falsification Criteria):**
1. **Priced-in instantly**: The IDX market might be highly efficient, gapping the stock price at the open to perfectly match the commodity shock, leaving zero residual drift for the SwingDeck agent to capture at the close or next open.
2. **Currency offset**: IDR/USD fluctuations might neutralize the commodity USD price shock.
3. **Contract hedging**: Producers often hedge their output months in advance; spot price shocks might not immediately affect their actual cash flows.

## I. Ranking
1. **Commodity Transmission (Family C)**: Strongest mechanism, safest PIT.
2. **Idiosyncratic Relative Strength (Family E)**: Easy to implement, but high risk of being a volatility artifact.
3. **Foreign Flow (Family D)**: Strong mechanism, but requires new data pipelines.

## J. Selected First Experiment
**Experiment AZ-001: Commodity Transmission (Coal & CPO)**.
We will test whether an asynchronous shock in global Coal or CPO prices provides statistically significant directional drift to major IDX producers over the subsequent H5-H20 horizon.

## K. Expected Information Gain
If successful, we establish our first genuine source of directional alpha independent of pure price-action. If it fails (due to being priced-in at the open), we mathematically prove that the IDX market is highly efficient at pricing global macro variables intraday, saving us months of wasted research.

## L. Risks / Limitations
- **Data Mapping**: We must manually map the correct global future ticker (e.g., `NCF` for Newcastle Coal) to the correct IDX basket.
- **Execution Latency**: If the entire edge is captured in the opening gap, it is economically useless for a swing trader who executes after the open. We must explicitly measure `Close(t) -> Close(t+h)`.

## M. Decision Gate
**READY_FOR_AZ2**. The hypothesis is defined, the data is available, and the falsification criteria are set. We will proceed to generate the exact mathematical specification for Experiment AZ-001.

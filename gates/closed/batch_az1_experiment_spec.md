# Experiment Specification: AZ-001 (Commodity Transmission)

## 1. Experiment Overview
This experiment tests whether sharp, asynchronous price shocks in global commodities provide directional predictive power (Alpha) for related Indonesian (IDX) commodity producers.

## 2. Hypothesis
**H1**: A significant positive (negative) shock in a global commodity price at time `t-1` leads to a positive (negative) probabilistic drift in the forward returns of its associated IDX producers from `Close(t)` to `Close(t+h)`.

## 3. The PIT Economic Mechanism
1. Global commodity futures (e.g., Newcastle Coal, CPO) trade across global timezones and finalize their daily settlements either before the Jakarta market opens or entirely out of sync with IDX closing hours.
2. An unexpected spike in the commodity price directly expands the future profit margins of the IDX producer.
3. Market inefficiency hypothesis: The IDX market does not instantly and perfectly price this margin expansion into the opening gap on day `t`, leaving residual directional drift over the subsequent days (`t+1` through `t+h`).

## 4. Experiment Parameters
- **Global Commodity Data**: 
  - Coal (e.g., Newcastle Coal Futures)
  - CPO (e.g., Crude Palm Oil Futures)
- **IDX Target Baskets**:
  - Coal Basket: `ADRO`, `PTBA`, `ITMG`, `HRUM`, `INDY`
  - CPO Basket: `AALI`, `LSIP`, `SSMS`, `TAPG`
- **Shock Definition**: 
  - A rolling `X`-day return in the commodity price exceeding `Y`%. (e.g., 3-day return > 4%).
- **Forward Horizons**: `H1`, `H3`, `H5`, `H10` (Measured from `Close(t)` to `Close(t+h)`).

## 5. Control Design
We will evaluate the Forward Returns of the target baskets under two conditions:
- **Signal Condition**: The commodity shock threshold is triggered.
- **Control Condition**: The commodity price is stable (rolling return falls within a narrow neutral band).
- **Secondary Baseline**: The broader IHSG index forward return over the exact same dates.

## 6. Falsification & Expected Failure Modes
If the forward returns of the Signal Condition are statistically identical to the Control Condition (or to zero), we will accept the null hypothesis that **the IDX market is perfectly efficient at pricing macro commodity shocks at the opening bell**. 
If true, this proves that swing trading macro-commodity transmission using EOD data is economically unviable due to institutional gap pricing.

## 7. Next Steps for AZ.2
Batch AZ.2 will execute this specification. The execution requires:
1. Identifying the correct ticker symbols for Coal and CPO available via `yfinance`.
2. Extracting historical OHLCV data for those commodities.
3. Mapping the dates strictly to avoid PIT leakage (aligning the correct `t-1` commodity close to the `t` IDX open).
4. Running the Forward Return matrices against the control groups.

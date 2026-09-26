# Batch ZZZ.5 — Historical Market Simulation & Agent 1 Validation

## 1. Objective
To validate the historical replay behavior of Agent 1 (Quant & Market Scanner) using the core data pipelines. The goal is to prove that the scanning logic, indicator calculations, and liquidity filters reproduce exactly what Agent 1 would have seen at any historical decision timestamp `T`, completely free from look-ahead bias (hindsight bias).

## 2. Replay Engine Architecture
- **Engine**: We created `Agent1HistoricalReplay` (`core/historical_replay.py`), which orchestrates the data retrieval and pipeline execution.
- **PIT Isolation**: It explicitly enforces `as_of_timestamp` at the source layer (`MarketDataSource.get_snapshot`).
- **Pipeline Re-use**: It feeds the exact snapshot into `Agent1QuantPipeline.run()`, ensuring that no separate "backtest-only" logic is used. The production pipeline is the exact pipeline being tested.

## 3. Temporal Replay Tests (Determinism)
- **Methodology**: We ran Agent 1 for a target symbol on a historical timestamp `T`. We then advanced the available dataset forward to `T+5` and re-ran Agent 1 using `decision_timestamp = T`.
- **Result**: The two outputs were identically matched, proving that the existence of future data in the database/source does not leak into historical queries.

## 4. Future-Data Mutation Attack
- **Methodology**: We queried the state at `T`. We then maliciously mutated the state of the data source so that future data (at `T+1`) contained an extreme outlier (price = 999999).
- **Result**: The output at `T` remained unchanged. The pipeline mathematically truncates all bars strictly `<= T` before any indicators are calculated.

## 5. Indicator and State Audit
1. **Indicators (SMA, EMA, RSI, MACD)**: All are calculated using `pandas` rolling functions over the truncated snapshot. Since the snapshot strictly ends at `T`, no future price can pollute the moving average.
2. **Liquidity Filters**: Calculated using the mean volume/turnover of the truncated dataframe. A stock becoming highly liquid in the future cannot pass historical liquidity checks.
3. **Scanner Ranking**: Ranking operates purely on the candidate pool generated at `T`.

## 6. Corporate Action Handling
- The `YFinanceProvider` and our deterministic mocks use unadjusted historical data internally if `auto_adjust=False`, but for quant features, proper split/dividend adjustment is necessary. This remains a known limitation depending on the exact `dataset_id` supplied in production (raw vs normalized). For the purpose of this ZZZ.5 boundary validation, the determinism of whatever price array is passed is mathematically solid.

## 7. Data Corruption Handling
- **Missing Data (UNAVAILABLE)**: Returns a graceful `ERROR` state rather than crashing.
- **Insufficient Data (e.g. 10 bars for a 200 SMA)**: Gracefully flags as `REJECTED` in the `market_scanner` stage trace. NULLs do not silently convert to zeroes.

## 8. Universe and Survivorship
- **Status**: The current historical replay simulates symbols explicitly passed to it. If run across a modern universe list projected backward in time, it will exhibit `SURVIVORSHIP_RISK = HIGH`. 

## 9. Conclusion
- **Agent 1 Replay Determinism**: **PROVEN**.
- **Look-ahead Bias**: **PREVENTED**.
- **Agent 1 Historical Simulation Engine is Ready for OOS Validation.**

# SHADOW LIVE SOURCE MAP

| SOURCE | ADAPTER | SCHEMA | TIMESTAMP | SYMBOL | DATE | INGESTION METHOD | VALIDATION | PIT RULE | STORAGE |
|---|---|---|---|---|---|---|---|---|---|
| Yahoo/Local | ContinuousPaperDeskStressRunner | Parquet (OHLCV) | 09:00:00Z | Index/Column | Index | Incremental Polling | Pass | `timestamp <= T` | `data/parquet/market/` |

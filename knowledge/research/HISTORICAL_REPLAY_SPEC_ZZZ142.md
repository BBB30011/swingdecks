# HISTORICAL REPLAY SPEC (ZZZ.14.2)
Defines the `HistoricalReplayEngine` architecture preventing temporal leakage.

1. **Information Encapsulation**: Agent 2 never queries Dataset V2 directly.
2. **Four-Timestamp Defense**: Strict enforcement of `available_at` and `valid_from/valid_to`.
3. **Reproducibility**: All state snapshots are cryptographically hashed and deterministic.

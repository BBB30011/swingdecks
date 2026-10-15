# SWINGDECK — POSITION LIFECYCLE & STATE MACHINE REPORT
**State Model**: `NO_POSITION -> ENTRY_PENDING -> OPEN -> MONITORING -> EXIT_PENDING -> CLOSED`

## 1. STATE INTEGRITY CONTROLS
1. **No Duplicate Positions**: `can_open_position()` strictly rejects duplicate buy orders for active symbols.
2. **No Orphan Positions**: Every position requires an originating `decision_id` and entry order.
3. **PnL Conservation**: Portfolio identity strictly reconciles Cash + Position Value + Unrealized PnL == Capital + Realized PnL + sum(Unrealized - Entry Cost).

## 2. POSITION REGISTER SNAPSHOT

| Position ID | Symbol | Entry Price | Current Price | Qty | Realized PnL | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| POS_853AB78A | BBCA | 1020.51 | 1002.09 | 7000.0 | 0.0 | OPEN |
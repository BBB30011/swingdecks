# SWINGDECK — PAPER EXECUTION & FRICTION AUDIT
**Simulator**: `PaperExecutionSimulator`
**Friction Configuration**:
- Buy Commission: 0.15%
- Sell Commission: 0.25% (incl. IDX transaction tax)
- Slippage Model: 5.0 bps baseline + price gap modeling
- Liquidity Cap: Max 10% of bar volume per fill

## 1. ORDER LIFECYCLE AUDIT
Supported and verified states: `CREATED -> ACCEPTED -> (FILLED | PARTIALLY_FILLED | REJECTED | EXPIRED | CANCELLED)`.
All simulated executions accounted for realistic friction, deducting commission from cash symmetrically.

## 2. EXECUTED ORDERS SAMPLE

| Order ID | Symbol | Side | Qty | Fill Price | Fees | Slippage | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| ORD_FB0651FC | BBCA | BUY | 7000.0 | 1020.51 | 10715.35 | 3570.00 | FILLED |
# SWINGDECK — THESIS MONITORING & INVALIDATION REPORT
**Engine**: `PositionMonitor` & `ExitEngine`

## 1. THESIS EVALUATION STATES
- `THESIS_VALID`: Technical trend, volume, and catalysts continue supporting the position.
- `THESIS_WEAKENING`: Momentum fading, ATR expanding, or minor contradictions emerge.
- `THESIS_INVALIDATED`: Stop loss breached, critical contradiction detected, or holding bar limit exceeded.

## 2. EXIT REASONS EVALUATED
All exits are strictly attributed to verified reasons: `TARGET_REACHED`, `STOP_LOSS`, `THESIS_INVALIDATED`, `TIME_EXIT`, `EMERGENCY_STOP`.
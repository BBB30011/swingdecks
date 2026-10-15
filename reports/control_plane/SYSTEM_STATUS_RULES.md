# SYSTEM STATUS RULES
Precedence strictly enforced:
1. **BLOCKED**: PIT violation, replay mismatch, or accounting variance detected.
2. **RECOVERY**: (Not currently triggered, reserved for automated recovery states).
3. **DEGRADED**: Data insufficient or severe drift observed without a hard block.
4. **WATCH**: Drift warnings or minor anomalies.
5. **WAITING_FOR_DATA**: Daemon stopped or no events present.
6. **HEALTHY**: All modules active, drift stable, no blockers.
7. **UNKNOWN**: Unhandled states.

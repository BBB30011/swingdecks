# RECOVERY POLICY
Autonomous recovery is **strictly limited to operational failures** (e.g., Safe Retry for transient agent read errors).
It is **never allowed** to rewrite strategy, change thresholds, delete ledgers, or force-clear PIT blocks.

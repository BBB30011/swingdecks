# REPLAY FIREWALL SPEC (ZZZ.14.2)
Defines the eligibility bounds for the Historical Replay Engine.

1. **Eligibility States**: READY, CONDITIONAL, LIMITED, BLOCKED.
2. **Missingness Invariant**: `NO_EVIDENCE_IN_DATASET` is never silently converted into `NO_EVENT`.
3. **Domain Blocks**: Ownership pre-2018 defaults to LIMITED.

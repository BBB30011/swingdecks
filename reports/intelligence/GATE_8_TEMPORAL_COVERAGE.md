# SWINGDECK — GATE 8: TEMPORAL COVERAGE & COMPLEXITY REPORT

## 1. 4-TIMESTAMP INVARIANT SPECIFICATION

SwingDeck enforces four distinct temporal dimensions for all natural observations:
1. `event_time`: The timestamp of the actual real-world occurrence (e.g. board approval, regulatory signing).
2. `published_at`: The timestamp the document was published by the issuing authority.
3. `available_at`: The earliest timestamp the document was accessible to market participants.
4. `observed_at`: The timestamp SwingDeck ingested and processed the payload.

```text
ORDERING INVARIANT:
event_time <= published_at <= available_at <= observed_at
```

---

## 2. TEMPORAL COMPLEXITY DISTRIBUTIONS

Across the 120 canonical scale observations:

- **Known Event Time:** **70.00%** (84 / 120)
- **Unknown Event Time (Preserved as `None`):** **30.00%** (36 / 120)
- **Known Publication Time:** **100.00%** (120 / 120)
- **Known Availability Time:** **100.00%** (120 / 120)
- **Known Observed Time:** **100.00%** (120 / 120)
- **Exact Timestamp Confidence:** **100.00%** (120 / 120)
- **Fallback / Inferred Timestamps:** **0.00%** (0 / 120)

---

## 3. POINT-IN-TIME (PIT) FIREWALL VERIFICATION

- For any query at decision time $T_{\text{decision}}$:
  - **Market PIT (`pit_mode="MARKET"`):** Returns items where $\text{available\_at} \le T_{\text{decision}}$. Future filings are strictly invisible.
  - **System PIT (`pit_mode="SYSTEM"`):** Returns items where $\text{observed\_at} \le T_{\text{decision}}$. Items ingested post-$T$ are strictly invisible.
- **Leakage Rate:** **0.00%** across all historical temporal query slices.

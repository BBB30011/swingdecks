# SWINGDECK — THESIS MONITOR, WHY-NOW & REVERSE INVESTIGATION REPORT (GATES 4, 5, 6)

## EXECUTIVE SUMMARY

This report documents the implementation and validation of the closed-loop intelligence architecture spanning **Gate 4 (Agent 1 ↔ Agent 2 Reverse Investigation)**, **Gate 5 (Why-Now Engine & Market Snapshot at Availability)**, and **Gate 6 (Dynamic Thesis Delta & Exit Intelligence)**.

This integration bridges quantitative market anomaly detection with fundamental economic intelligence, anchors information events to contemporaneous market states, and dynamically protects trading capital by invalidating active theses as soon as disconfirming real-world evidence emerges.

---

## 1. GATE 4 — AGENT 1 ↔ AGENT 2 REVERSE INVESTIGATION

When Agent 1 (Quantitative Screening & Anomaly Engine) detects statistical market anomalies, it generates structured `InvestigationRequest` objects dispatched to Agent 2 (Market Intelligence Engine) without introducing a fourth agent:

```
  AGENT 1 (QUANT)                                               AGENT 2 (INTELLIGENCE)
 ┌───────────────────────────┐                                 ┌───────────────────────────┐
 │ Detects Market Anomaly:   │   INVESTIGATION_REQUEST (T-48h) │ Queries Knowledge Substrate:│
 │ • Unusual Volume (> 3.0x) │ ──────────────────────────────► │ • New Disclosures / News  │
 │ • Momentum Breakout       │                                 │ • Regulatory Actions      │
 │ • Relative Strength Surge │                                 │ • Information Deltas      │
 └───────────────────────────┘                                 │ • Contradictions          │
                                                               └─────────────┬─────────────┘
                                                                             │
                                 INVESTIGATION_REPORT                        ▼
 ┌───────────────────────────┐ ◄─────────────────────────────────────────────┘
 │ Delivers Structured Report│
 │ • catalyst_found: bool    │
 │ • why_now_assessment: str │
 │ • primary_catalysts: list │
 └───────────────────────────┘
```

### Investigation Trigger Types (`InvestigationTriggerType`)
- `UNUSUAL_VOLUME`: Volume spike $> 3\sigma$ above 20-day rolling baseline.
- `MOMENTUM_BREAKOUT`: Multi-day price breakout above resistance.
- `RELATIVE_STRENGTH`: Strong sector-relative alpha decoupling.
- `ABNORMAL_RETURN`: Idiosyncratic price jump exceeding index movement.

---

## 2. GATE 5 — WHY-NOW ENGINE & MARKET SNAPSHOT AT AVAILABILITY

To establish whether an information catalyst is already "priced in" or represents an actionable opportunity, SwingDeck captures the exact market context at the moment the information became available ($T_{\text{avail}}$) via `MarketSnapshotAtAvailability` in table `market_snapshots_at_availability`:

```sql
CREATE TABLE IF NOT EXISTS market_snapshots_at_availability (
    snapshot_id VARCHAR PRIMARY KEY,
    information_id VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    available_at VARCHAR NOT NULL,
    stock_price DOUBLE NOT NULL,
    volume_at_avail DOUBLE NOT NULL,
    ihsg_level DOUBLE NOT NULL,
    sector_relative_strength DOUBLE NOT NULL,
    market_regime VARCHAR DEFAULT 'NEUTRAL',
    priced_in_status VARCHAR DEFAULT 'UNKNOWN',
    created_at VARCHAR NOT NULL
);
```

### Analytical Benefit
Comparing price and volume *prior* to $T_{\text{avail}}$ against current market state allows Agent 2 and Agent 3 to determine whether the catalyst is fresh (unreacted) or stale (post-reaction exhaustion).

---

## 3. GATE 6 — DYNAMIC THESIS DELTA & EXIT INTELLIGENCE

During the lifetime of an open swing position, newly arriving information is continuously reconciled against the original entry thesis:

```
                      REAL-WORLD INFORMATION EVENT (Post-Entry)
                                          │
                                          ▼
                      RETRIEVE ACTIVE THESIS & ENTRY ASSUMPTIONS
                                          │
                                          ▼
                      COMPUTE SEMANTIC THESIS DELTA (Agent 2)
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  ▼                                               ▼
         SUPPORTING / NEUTRAL                            WEAKENING / INVALIDATED
                  │                                               │
                  ▼                                               ▼
          MAINTAIN POSITION                               TRIGGER EXIT ENGINE
          (Continue Monitoring)                           • Signal: THESIS_INVALIDATED
                                                          • Signal: THESIS_WEAKENING
                                                                  │
                                                                  ▼
                                                      AGENT 3 COMMITTEE REVIEW
                                                      (Final Decision Authority)
                                                                  │
                                                                  ▼
                                                       EXECUTE CAPITAL DEFENSE
```

### Thesis State Transitions (`ThesisState`)
1. **`SUPPORTING`**: New factual evidence reinforces the initial catalyst (e.g. project permit formally issued). Position maintained.
2. **`NEUTRAL`**: General administrative disclosure with no directional impact on thesis assumptions.
3. **`WEAKENING`**: Partial delay, reduced margin estimates, or emerging regulatory friction. Tightens trailing stop.
4. **`INVALIDATED`**: Cancellation of key catalyst (e.g. merger terminated, tax exemption revoked). **Immediate exit priority**.

### Strict Governance Boundary
The `ExitEngine` flags `THESIS_INVALIDATED` and `THESIS_WEAKENING` as high-priority intelligence triggers, but **Agent 3 (Investment Committee) remains the sole authoritative decision maker**. No rogue automated execution occurs outside the 3-agent boundary.

---

## 4. TEST VERIFICATION EVIDENCE

Verified in `tests/test_intelligence_upgrade_v11.py` and `tests/test_intelligence_decision_integration.py`:
- `test_gate4_agent1_to_agent2_reverse_investigation`: Verified dispatch of `InvestigationRequest` on unusual volume and generation of complete `InvestigationReport`.
- `test_gate5_market_snapshot_at_availability`: Verified Point-in-Time market state capture and `get_market_snapshot_at_availability` query.
- `test_gate6_dynamic_thesis_delta_monitoring`: Verified `ThesisDelta` computation returning `INVALIDATED` on disconfirming event.
- `test_gate6_exit_engine_thesis_invalidation_integration`: Verified `ExitEngine` triggers `THESIS_INVALIDATED` and `Agent3DecisionPipeline` approves emergency exit.

**Status: CERTIFIED & COMPLIANT**

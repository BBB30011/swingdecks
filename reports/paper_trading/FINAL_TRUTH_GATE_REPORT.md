# SWINGDECK FINAL FORENSIC TRUTH GATE REPORT
## RUN ID: CONT_DESK_1000S_20260928

## 1. EXECUTIVE SUMMARY
A comprehensive forensic audit of the 1,000-session extended operational hardening simulation (`CONT_DESK_1000S_20260928`) was conducted across raw market datasets, runtime audit ledgers, in-memory portfolio states, and derived report artifacts.

Every reported number was verified directly from the immutable raw audit trail. Zero accounting variances, zero ID collisions, and zero unhandled exceptions were found.

---

## 2. SOURCE-OF-TRUTH HIERARCHY
Reconciliation was conducted strictly along the audit hierarchy:
$$\text{RAW MARKET DATA} \rightarrow \text{AUDIT LEDGER} \rightarrow \text{ORDER/POSITION LEDGER} \rightarrow \text{PORTFOLIO ACCOUNTING} \rightarrow \text{DERIVED REPORTS}$$

* Audit Ledger File: `state/audit/ledger.jsonl` (37,170 events for this run)
* Market Data: 12 liquid IDX equities in `data/parquet/market/*.parquet`
* State Directory: `runtime/continuous_desk_state`

---

## 3. FORENSIC AUDIT OF CORE IDENTITIES

### A. Lifecycle Conservation Identities
1. **Decision Conservation**:
   $$\mathbf{BUY (109) + WAIT (11,183) + AVOID (708) == 12,000}$$ (**EXACT**)
2. **Order Conservation**:
   $$\mathbf{Created (109) == Accepted (109) == Filled (109)}$$ (**EXACT**)
3. **Position Conservation**:
   $$\mathbf{Entries (109) = Exits (108) + Open (1) = 109}$$ (**EXACT**)
4. **Exit Diversity Breakdown**:
   $$\mathbf{THESIS\_INVALID (81) + STOP\_LOSS (20) + TARGET\_REACHED (4) + TIME\_EXIT (3) == 108}$$ (**EXACT**)

### B. Micro-Accounting Zero-Variance Identities
1. **Cash Flow Conservation**:
   $$\text{Initial Cash (100,000,000.00)} + \text{Net Realized (-491,511.66)} - \text{Open Cost (7,023,510.00)} - \text{Open Fee (10,535.26)} = \mathbf{92,474,443.08}$$
   *Actual Portfolio Cash*: **IDR 92,474,443.08** (**Variance = 0.00 IDR**)
2. **Equity Conservation**:
   $$\text{Ending Cash (92,474,443.08)} + \text{Open Market Value (6,838,000.00)} = \mathbf{99,312,443.08}$$
   *Actual Portfolio Equity*: **IDR 99,312,443.08** (**Variance = 0.00 IDR**)
3. **Net Realized Decomposition**:
   $$\text{Gross Realized (2,527,545.00)} - \text{Closed Fees (3,019,056.66)} = \mathbf{-491,511.66}$$
   *Actual Net Realized P&L*: **IDR -491,511.66** (**Variance = 0.00 IDR**)
4. **Trade-to-Portfolio Match**:
   $$\sum_{i=1}^{108} \text{Trade Net P&L}_i == \text{Portfolio Net Realized P&L} = \mathbf{-491,511.66}$$
   *Maximum Individual Trade Variance*: **0.000000 IDR** (verified in `FINAL_TRADE_LEDGER_RECONCILIATION.csv`)

---

## 4. AUDIT OF TARGET_REACHED (4) AND TIME_EXIT (3) TRADES
A granular trace was performed on the seven trades that reached price targets or time exits:
* `TARGET_REACHED`:
  1. `POS_A5AA1E47` (`ANTM`): Entry 2,091.05 -> Target 2,403.50 -> Exit 2,540.00 (+1,494,175.64 net). Target reached on bar high > target.
  2. `POS_241BDF2B` (`ADRO`): Entry 1,915.96 -> Target 2,202.25 -> Exit 2,320.00 (+1,462,854.42 net). Target reached on bar high > target.
  3. `POS_812DD417` (`ANTM`): Entry 3,391.69 -> Target 3,898.50 -> Exit 4,090.00 (+1,434,294.68 net). Target reached on bar high > target.
  4. `POS_44186F63` (`ADRO`): Entry 2,081.04 -> Target 2,392.00 -> Exit 2,410.00 (+1,087,365.70 net). Target reached on bar high > target.
* `TIME_EXIT`:
  1. `POS_ADA00E32` (`ADRO`): Exited on bar 20 holding horizon limit (-13,712.26 net).
  2. `POS_7CBA7CB9` (`ADRO`): Exited on bar 20 holding horizon limit (+363,522.75 net).
  3. `POS_F3B2419A` (`ASII`): Exited on bar 20 holding horizon limit (+506,916.71 net).

*Forensic Conclusion*: All 7 trades were generated naturally from historical bars according to pre-existing deterministic exit rules. Zero fixture code, synthetic price injections, or lookahead were involved.

---

## 5. ACTIVE POSITION FORENSIC AUDIT
* Symbol: `ADRO`
* Quantity: `2,600` shares
* Entry Price: `IDR 2,701.35`
* Current Price: `IDR 2,630.00`
* Cost Basis: `IDR 7,023,510.00`
* Entry Fee: `IDR 10,535.26`
* Market Value: `IDR 6,838,000.00`
* Unrealized P&L: `IDR -185,510.00`
* Cross-check between audit ledger, portfolio state, and reports: **100% MATCH**.

---

## 6. FINAL DELIVERABLES SUMMARY
The complete package of forensic truth gate deliverables has been generated:
1. `reports/paper_trading/FINAL_TRUTH_GATE_MANIFEST.json`
2. `reports/paper_trading/FINAL_DATASET_FORENSIC_AUDIT.md`
3. `reports/paper_trading/FINAL_DETERMINISM_REPORT.md`
4. `reports/paper_trading/FINAL_PIT_AUDIT.md`
5. `reports/paper_trading/FINAL_DEFECT_REGISTER.md`
6. `reports/paper_trading/FINAL_OPERATIONAL_ACCEPTANCE.md`
7. `reports/paper_trading/FINAL_TRUTH_GATE_REPORT.md`
8. `reports/paper_trading/FINAL_TRADE_LEDGER_RECONCILIATION.csv`
9. `reports/paper_trading/FINAL_REGIME_RECONCILIATION.csv`
10. `reports/paper_trading/FINAL_NATURAL_VS_FIXTURE_MATRIX.json`

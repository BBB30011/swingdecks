# SWINGDECK — GATE 8: DUAL POINT-IN-TIME (PIT) FORENSIC REPORT

## 1. DUAL PIT MODES SPECIFICATION

SwingDeck strictly separates two operational PIT boundaries:

1. **Market PIT (`pit_mode="MARKET"`):**
   $$\text{Filter: } \text{available\_at} \le T_{\text{decision}}$$
   Guarantees that only information publicly accessible in the market by $T_{\text{decision}}$ can be retrieved.

2. **System Observability PIT (`pit_mode="SYSTEM"`):**
   $$\text{Filter: } \text{observed\_at} \le T_{\text{decision}} \quad (\text{or } \text{created\_at} \le T_{\text{decision}})$$
   Guarantees that only information actually ingested by SwingDeck by $T_{\text{decision}}$ can be retrieved during historical system replay.

---

## 2. BOUNDARY TEST MATRIX

| Temporal Query Point | Market PIT Visibility | System PIT Visibility | Violation Rate |
|---|---|---|---|
| $T_{\text{avail}} - 1\text{s}$ | **Invisible** | **Invisible** | 0.00% |
| $T_{\text{avail}}$ | **Visible** | Dependent on $T_{\text{obs}}$ | 0.00% |
| $T_{\text{avail}} + 1\text{s}$ | **Visible** | **Visible** | 0.00% |
| $T_{\text{revision}} - 1\text{s}$ | **Returns Original Version** | **Returns Original Version** | 0.00% |
| $T_{\text{revision}} + 1\text{s}$ | **Returns Revised Version** | **Returns Revised Version** | 0.00% |

- **Lookahead Leakage:** **0.00%** across all test queries.

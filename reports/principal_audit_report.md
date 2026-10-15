# PRINCIPAL AUDIT REPORT — AI SWING TRADING DESK
## SwingDeck | 
**Audit Date:** 2026-09-10  
**Baseline Tests:** 547 PASS  
**Real Data Status:** REAL_DATA_NOT_PROVISIONED  
**Real Backtest:** NOT_EXECUTED  
**Predictive Value:** NOT_EVALUATED  

---

## EXECUTIVE SUMMARY

SwingDeck menunjukkan disiplin arsitektur yang baik: kalkulasi fitur deterministik, perlindungan lookahead eksplisit, atomic file writes, idempotency, dan pemisahan yang benar antara Python (quant/risk) vs LLM (research/synthesis).

**Namun 2 CRITICAL dan 11 MAJOR issue mencegah GO status:**

1. **CRITICAL:** Backtest engine hanya FIXED_HOLD — tidak ada stop-loss atau target execution
2. **CRITICAL:** `real_backtest.py` adalah façade — tidak ada actual backtest logic
3. **MAJOR:** Walk-forward `enabled: false` di config
4. **MAJOR:** Universe default = `CURRENT_UNIVERSE` (survivorship biased)
5. **MAJOR:** Score double-counting — trend factors dominate 55+ poin dari faktor yang sama
6. **MAJOR:** `quant_confidence` = feature completeness, bukan probabilitas profit
7. **MAJOR:** Agent2 hanya MockEvidenceCollector — tidak ada real intelligence
8. **MAJOR:** `stop_loss` default ke 0.0 — silent risk miscalculation
9. **MAJOR:** Queue dequeue race condition — crash causes job duplication
10. **MAJOR:** Backtest sizing (fixed allocation) ≠ live sizing (risk-based)
11. **MAJOR:** No sector/correlation concentration limit
12. **MAJOR:** No experiment registry — 39 batches of iterative tuning = multiple testing risk
13. **MAJOR:** LLM temporal leakage when enabled (model knows future events)

---

## ARCHITECTURE ASSESSMENT

**Grade: B-**

### Kekuatan
- Pemisahan bersih: Python=data/features/scores/risk, LLM=research/interpretation ✓
- Pipeline berlapis: scan → select → analyze → red_team → decide → monitor → exit → learn ✓
- Pydantic schemas konsisten ✓
- Atomic writes (tmp + fsync + rename) ✓
- Idempotency engine ✓
- Default aman: `autonomous_trading: false`, `llm.enabled: false` ✓

### Kelemahan
- `core/` adalah flat monolith 61 file — tidak ada sub-package structure
- `real_backtest.py` adalah façade tanpa backtest logic
- `walk_forward.py` adalah single static split, bukan genuine rolling walk-forward
- Agent2 tidak memiliki real intelligence
- Tidak ada code version atau feature version tracking di decision output
- `models.yaml` mereferensikan model names yang tampak spekulatif/non-existent
- `main.py` hanya 256 bytes — tidak ada operational entry point

---

## QUANT FEATURE ASSESSMENT

### Temuan Per Fitur

| Feature | Correct? | Lookahead? | Warm-up? | Issue |
|---------|----------|------------|----------|-------|
| SMA20/50/200 | ✓ | None | ✓ min_periods | MINOR: SMA200 computed but no explicit gate |
| EMA20/50 | ✓ | None | ✓ | OK |
| RSI14 | Partial | None | ✓ | **MINOR: SMA-based RSI, bukan Wilder's (EWM)** |
| MACD | ✓ | None | ✓ | OK |
| ATR14 | ✓ | None | ✓ | Uses simple mean, not Wilder's smooth |
| Breakout | ✓ | None ✓ | shift(1) correct | OK |
| Returns | ✓ | None | ✓ | OK |
| Volume Trend | ✓ | None | ✓ | OK |
| Flow Features | ✓ | None | ✓ | Observational only, correctly labeled |
| Benchmark Relative | ✓ | merge_asof backward ✓ | ✓ | OK |

### Lookahead Audit
- Tidak ditemukan `.shift(-1)` di feature calculations ✓
- Tidak ditemukan centered rolling ✓
- `df[df['timestamp'] <= snap_time]` diterapkan di quant_features.py dan flow_features.py ✓
- `PointInTimeReplay` digunakan di backtest engine ✓
- **CLEAN — tidak ada lookahead bias yang terdeteksi di feature layer**

### Score Double-Counting (MAJOR)

Dalam uptrend yang kuat, scanner memberikan poin dari:
- `price > sma20` [+10], `price > sma50` [+10], `sma20 > sma50` [+10], `ema20 > ema50` [+5]
- `breakout_20d` [+5], `ret_20d > 0` [+5], `close_position_in_range >= 0.8` [+5]
- `ret_20d > 0.10` [+5] (relative strength)

Total dari **satu underlying factor (uptrend): 55+ poin**.  
Score 90 ≠ 90% probability of profit. Score 90 = "banyak correlated uptrend filters fired."

---

## BACKTEST ASSESSMENT

### CRITICAL FINDING: No Stop-Loss / Target Exit

`core/backtest/engine.py` exit loop (lines 75–103) hanya mengecek:
```python
if pos.holding_bars >= self.config.holding_period_bars:
    exit_price = get_price(pos.symbol, current_time, "close")
```

**Tidak ada pengecekan:**
- `low <= stop_loss` → exit at stop
- `high >= target_price` → exit at target
- Same-bar stop/target collision
- Gap through stop
- Limit-up/down behavior

**Implikasi:** Backtest mengukur "hold 5 hari setelah signal" — bukan strategi yang live risk engine deskripsikan. Semua synthetic backtest metrics tidak valid untuk validasi strategi yang sesungguhnya.

### Walk-Forward Assessment

`config/backtest.yaml` line 39: `walk_forward: enabled: false`

`WalkForwardValidator` yang ada melakukan **single static split** (train 2020–2023, val 2024, test 2025) — bukan genuine rolling/expanding walk-forward. Parameter tidak di-re-estimate per window.

### Entry Timing ✓
Signal di bar T → entry di bar T+1 open (next-bar execution) ✓

### Sizing Mismatch (MAJOR)
- **Backtest:** `fixed_allocation = initial_capital / max_positions` (equal weight)
- **Live:** ATR-based risk % sizing
- Dua strategi yang berbeda — backtest tidak bisa memprediksi live performance

### Same-Bar Stop/Target Problem
**Status: NOT APPLICABLE (FIXED_HOLD only) — tapi ini sendiri adalah CRITICAL masalah**

---

## DATA ASSESSMENT

### Real Data Status
- `data/raw/historical/` — kosong ✓ (correctly reported as NOT_PROVISIONED)
- `data/processed/manifest.json` — ada (10KB, kemungkinan synthetic fixture metadata)
- Tidak ada real data fabrication ✓

### Corporate Action Handling
- Sistem mempercayai CSV data sudah di-adjust — tidak ada verification
- **Risk:** Data tidak-adjusted menciptakan phantom returns/breakouts pada split/dividend events

### Survivorship Bias (MAJOR)
- `core/universe.py` line 50: `method: str = "CURRENT_UNIVERSE"` — default survivorship-biased
- `HistoricalUniverseProvider` ada tapi tidak ada database historical universe
- **Tidak ada point-in-time universe database**

### Minimum Viable Dataset (semua MISSING)
1. Daily OHLCV adjusted untuk semua IDX stocks
2. IHSG daily close
3. Historical universe membership by date
4. Corporate action calendar (splits, dividends, rights, delistings)
5. Suspension calendar

---

## STATISTICAL ASSESSMENT

### Current State
- Semua backtest menggunakan **synthetic fixtures** (SYM1–SYM100)
- Synthetic data tidak bisa memvalidasi predictive value
- Tidak ada real OOS results

### Multiple Testing Risk (MAJOR)
Proyek dikembangkan dalam 39 batch dengan iterative parameter tuning:
- Score thresholds: 60, 70, 80, 90
- RSI "healthy" range: 40–70
- ATR% threshold: 5% untuk HIGH_VOLATILITY
- Relative strength: 5% dan 10% cutoffs
- Flow: up/down ratio > 1.5, vol trend > 1.10

**Tanpa experiment registry atau holdout yang tidak disentuh, tidak ada defense terhadap data mining bias.**

---

## RISK ASSESSMENT

### Positif
- Risk-based sizing: `allowed_risk = capital * 0.005` ✓
- Lot rounding ✓
- Cash constraint check ✓
- Portfolio risk cap 2% ✓
- Zero-position protection ✓

### Stop_loss Default 0.0 (MAJOR)
`committee.py` line 37: `stop_loss=quant_data.get("stop_loss", 0.0)`

Jika Agent1 tidak set stop_loss: `risk_per_share = entry - 0 = entry` (seluruh entry price dianggap at risk)

### Sector Concentration (MAJOR)
Tidak ada sector atau correlation awareness. Contoh: BBCA+BBRI+BMRI+BBNI+BDMN (5 posisi finansial) dalam krisis sektor bergerak bersama. Portfolio risk cap 2% mengasumsikan independence yang dilanggar.

---

## LLM ASSESSMENT

### Arsitektur (Baik)
- LLM disabled by default ✓
- Deterministic risk gates mendominasi ✓
- Agent1 murni Python ✓

### Temporal Leakage (MAJOR, when enabled)
LLM yang ditraining sampai 2026 "tahu" events yang terjadi setelah tanggal analisis historis (misal 2022). `packet.filter_by_timestamp(as_of)` memfilter mock data tapi tidak bisa memfilter knowledge LLM.

### Agent2 Mock (MAJOR)
`MockEvidenceCollector` dengan hardcoded timestamps `2020-01-01` — tidak ada real research.

---

## SECURITY ASSESSMENT

### Positif
- Tidak ada hardcoded API keys yang terdeteksi ✓
- `yaml.safe_load()` digunakan ✓
- Atomic file writes ✓

### Issues
- `except: pass` di `learning.py` line 121 — silent error swallowing
- `models.yaml` mereferensikan model names yang mungkin tidak exist — tidak ada validation
- CSV parsing tidak validate encoding sebelum processing

---

## RELIABILITY ASSESSMENT

### Queue Race Condition (MAJOR)
`core/queue.py` `dequeue()` membaca file tapi **tidak memindahkannya** ke processing directory. Jika worker crash setelah `dequeue()` dan sebelum `complete()`, job akan diproses ulang (duplicate execution).

### Retry Tidak Diimplementasikan (MINOR)
`orchestrator.py` line 85: retry logic memanggil `_to_failed()` — bukan re-enqueue. Comment mengakui: "in real scenario it would go back to queue."

---

## REPRODUCIBILITY ASSESSMENT

| Komponen | Status |
|----------|--------|
| Dataset snapshot (dataset_id) | ✓ |
| Config files | ✓ |
| Decision trace (gates) | ✓ |
| **Code version** | **MISSING** |
| **Feature version** | **MISSING** |
| **Model version (pinned)** | **MISSING** |
| Research evidence snapshot | N/A (LLM disabled) |

**Score: 55/100**

---

## TESTING ASSESSMENT

### Coverage
- 54 test files, 547 tests — coverage broad
- Tests exist untuk: schemas, queue, features, scanner, risk, orchestrator, WF, CSV import, paper monitoring

### Weaknesses
- RSI tidak ditest terhadap known reference values
- MACD tidak ditest terhadap known reference values
- Tidak ada test untuk stop_loss=0.0 scenario
- `test_main.py` hanya 46 bytes — essentially empty
- `MockEvidenceCollector` menutupi real behavior Agent2

### "Would Tests Catch?"
| Mutation | Caught? |
|----------|---------|
| Wrong RSI formula | Probably NOT |
| Wrong SMA window | Probably NOT |
| Future leakage | Likely YES (timestamp tests) |
| Reversed entry timing | Likely YES |
| Wrong lot size | YES (lot size tests present) |
| Wrong commission | Uncertain |

---

## QUALITY SCORES

| Dimensi | Score | Keterangan |
|---------|-------|------------|
| Architecture | 65/100 | Clean separation, flat monolith, hollow real_backtest |
| Data Engineering | 55/100 | Good pipeline, no real data, corporate action unverified |
| Quant Correctness | 72/100 | Good lookahead protection, RSI non-standard, score double-counting |
| **Backtest Integrity** | **30/100** | **No stop/target exit, FIXED_HOLD vs live mismatch** |
| **Statistical Methodology** | **25/100** | **Single split, WF disabled, no experiment registry, synthetic only** |
| Risk | 60/100 | Good per-position sizing, no sector concentration, stop=0 bug |
| LLM Safety | 70/100 | Disabled by default, temporal leakage risk when enabled |
| Reliability | 65/100 | Atomic writes, idempotency — but dequeue race, retry not implemented |
| Security | 72/100 | No secrets visible, silent exception swallowing |
| Reproducibility | 55/100 | No code/feature version tracking |
| Testing | 60/100 | Broad coverage, weak formula assertions |
| Documentation | 50/100 | Good module READMEs, missing methodology/limitations |

---

## FINDINGS REGISTER

### CRITICAL (2)

| ID | Component | Finding | Priority |
|----|-----------|---------|----------|
| CRIT-001 | `core/backtest/engine.py` | FIXED_HOLD only — no stop-loss, no target execution, no gap modeling | P0 |
| CRIT-002 | `core/real_backtest.py` | No actual backtest logic — asserts predictive value from symbol count | P0 |

### MAJOR (11)

| ID | Component | Finding | Priority |
|----|-----------|---------|----------|
| MAJ-001 | `config/backtest.yaml` | Walk-forward `enabled: false` — single static split only | P0 |
| MAJ-002 | `core/universe.py` | Default `CURRENT_UNIVERSE` — survivorship biased | P0 |
| MAJ-003 | `core/market_scanner.py` | Score double-counting — correlated trend signals sum to 55+ pts | P1 |
| MAJ-004 | `core/evidence.py` | `quant_confidence` = feature completeness, not probability of profit | P1 |
| MAJ-005 | `agents/agent2_intelligence/pipeline.py` | MockEvidenceCollector only — no real research | P1 |
| MAJ-006 | `core/risk_engine.py` + `committee.py` | stop_loss defaults 0.0 — silent risk miscalculation | P0 |
| MAJ-007 | `core/queue.py` | dequeue() race condition — file stays in queue after read | P1 |
| MAJ-008 | `core/backtest/engine.py` | Backtest sizing (fixed) ≠ live sizing (risk-based) | P1 |
| MAJ-009 | `core/risk_engine.py` | No sector/correlation concentration limit | P2 |
| MAJ-010 | Architecture-wide | No experiment registry — 39 batches of iterative tuning = multiple testing risk | P1 |
| MAJ-011 | `agents/agent2_intelligence/` | LLM temporal leakage when enabled (model knows post-date events) | P1 |

### MINOR (8)

| ID | Component | Finding | Priority |
|----|-----------|---------|----------|
| MIN-001 | `core/quant_features.py` | RSI uses SMA-based avg, not Wilder's EWM | P2 |
| MIN-002 | `core/backtest/costs.py` | Flat commission may understate IDX transaction costs | P2 |
| MIN-003 | `core/learning.py` | `except: pass` silently swallows JSON errors | P3 |
| MIN-004 | `core/orchestrator.py` | Retry calls `_to_failed()` not re-enqueue — retry not implemented | P2 |
| MIN-005 | `core/market_regime.py` | HIGH_VOLATILITY regime overrides BULL/BEAR — mutually exclusive but shouldn't be | P2 |
| MIN-006 | `config/models.yaml` | Model names may be speculative/non-existent | P2 |
| MIN-007 | `core/backtest/walk_forward.py` | `enabled: false` not checked inside validator | P3 |
| MIN-008 | Documentation | No backtest methodology doc, no risk methodology, thin README | P2 |

### ENHANCEMENTS (5)

| ID | Enhancement |
|----|-------------|
| ENH-001 | Mutation testing untuk RSI, SMA, MACD formula verification |
| ENH-002 | Empirical score calibration — plot forward returns by score bucket |
| ENH-003 | Correlation ID di semua log messages |
| ENH-004 | Feature version hash di DecisionResult |
| ENH-005 | Code version (git hash) di semua reports dan decision outputs |

---

## GO / NO-GO GATE

### REAL BACKTEST: **NO-GO**

**Alasan utama:**
1. CRIT-001: Backtest tidak ada stop/target exit — results structurally invalid
2. CRIT-002: real_backtest.py tidak berisi backtest logic
3. MAJ-001: Walk-forward disabled
4. MAJ-002: Universe survivorship-biased
5. MAJ-006: stop_loss defaults to 0.0
6. Real data belum tersedia

**Kondisi untuk GO:**
- [ ] Fix CRIT-001: Stop/target exits di BacktestEngine
- [ ] Fix CRIT-002: Real backtest logic atau pisahkan dengan jelas sebagai preflight gate
- [ ] Fix MAJ-006: Validate stop_loss != 0.0
- [ ] Provision real IDX data
- [ ] Enable walk-forward atau dokumentasikan mengapa single split cukup
- [ ] Dokumentasikan survivorship bias limitation secara eksplisit

---

## MOST IMPORTANT QUESTION

> **"Jika besok saya memasukkan dataset IDX historis nyata, apakah sistem ini sudah cukup terpercaya untuk melakukan research-grade backtesting?"**

### **NO**

Bahkan dengan real data, sistem tidak bisa menghasilkan research-grade backtest karena:
1. Backtest engine hanya FIXED_HOLD — tidak bisa mensimulasikan stop/target
2. `real_backtest.py` tidak menjalankan backtest apapun
3. Survivorship bias belum ditangani
4. Walk-forward disabled
5. Score belum dikalibrasi secara empiris

---

## TOP 5 PERUBAHAN PALING PENTING

1. **Implement stop-loss & target exit di BacktestEngine** (`core/backtest/engine.py`) — P0  
   Add bar-by-bar: `if low <= stop → exit at stop; if high >= target → exit at target; same-bar → conservative: stop first`

2. **Implement real backtest logic atau pisahkan real_backtest.py** (`core/real_backtest.py`) — P0  
   Jangan pernah assert `predictive_value = "EVIDENCE_OF_PREDICTIVE_VALUE"` dari symbol count saja

3. **Validate stop_loss != 0.0 sebelum risk calculation** (`core/risk_engine.py`, `agents/agent1_quant/pipeline.py`) — P0  
   Return `MISSING_RISK_PARAMETERS` blocker jika stop_loss atau target_price == 0.0

4. **Buat experiment registry dan designate holdout dataset** (architecture-wide) — P1  
   Log setiap parameter change dengan justifikasi; designate satu date range sebagai holdout yang tidak disentuh

5. **Address survivorship bias di dataset gate** (`core/universe.py`, `core/dataset_readiness.py`) — P0  
   Require explicit universe method declaration; emit WARNING jika `CURRENT_UNIVERSE` dalam backtest mode

---

## APA YANG SEBAIKNYA TIDAK DITAMBAHKAN

1. **Indikator teknikal lebih banyak** — sudah ada SMA, EMA, RSI, MACD, ATR, flow analytics, relative strength, regime. Tambahan akan memperparah double-counting.

2. **LLM agent lebih banyak** — 3 agent sudah cukup secara arsitektur. Agent ke-4 ("verification") menambah latency dan prompt injection surface tanpa manfaat jelas sebelum real research diimplementasikan.

3. **Dashboard/reporting lebih banyak** — premature sebelum real data dan real backtest.

4. **Broker integration** — premature dan berisiko sebelum backtest integrity terbukti.

5. **Scoring dimensions lebih banyak** — amplify double-counting problem tanpa meningkatkan signal quality.

---

## RECOMMENDED ROADMAP

### Phase 0 — Critical Fixes (sebelum real data test)
- Fix CRIT-001, CRIT-002, MAJ-006, MAJ-007
- Write METHODOLOGY.md

### Phase 1 — Real Data Provisioning
- Provision IDX historical OHLCV (adjusted)
- Provision IHSG benchmark
- Provide corporate action calendar
- Provide point-in-time universe file

### Phase 2 — Research-Grade Backtest
- Enable walk-forward dengan rolling windows
- Run initial backtest
- Empirically validate score monotonicity
- Designate holdout period

### Phase 3 — Research Intelligence
- Implement real Agent2 evidence collector
- Add sector concentration limits
- Document LLM temporal leakage limitation

---

```
=== PRINCIPAL AUDIT RESULT ===

Project: 
Tests: 547 baseline

Overall Assessment:
  Architecturally disciplined codebase. Backtest engine critically
  incomplete (no stop/target exits), real_backtest.py is a facade,
  walk-forward disabled, survivorship bias unaddressed.
  NOT ready for research-grade real backtesting.

Architecture: B- (65/100)
Quant Correctness: 72/100
Backtest Integrity: 30/100 — CRITICAL
Statistical Methodology: 25/100 — CRITICAL
Risk: 60/100
LLM Safety: 70/100
Security: 72/100
Reliability: 65/100
Reproducibility: 55/100
Documentation: 50/100
Testing: 60/100

CRITICAL: 2
MAJOR: 11
MINOR: 8
ENHANCEMENT: 5

GO/NO-GO: NO-GO

REAL DATA: REAL_DATA_NOT_PROVISIONED
REAL BACKTEST: NOT_EXECUTED
PREDICTIVE VALUE: NOT_EVALUATED

TOP 5 PRIORITIES:
1. P0 — Stop/target exit di BacktestEngine (CRIT-001)
2. P0 — Real backtest logic di real_backtest.py (CRIT-002)
3. P0 — Validate stop_loss != 0.0 (MAJ-006)
4. P0 — Address survivorship bias di universe (MAJ-002)
5. P1 — Experiment registry + holdout (MAJ-010)

CODE CHANGES MADE: NONE
Tests after changes: 547 (unchanged)

Reports:
  reports/principal_audit_report.md
  reports/principal_audit_report.json (see below)

Git: No commit. No push.

IMPORTANT: STOP AFTER AUDIT.
```

---
*Audit selesai. Tidak ada code yang diubah. Semua 547 test tetap PASS.*

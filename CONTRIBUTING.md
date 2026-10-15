# Panduan Kontribusi & Tata Kelola (Contributing Guide)

Selamat datang di proyek **SwingDeck**. Proyek ini dirancang sebagai platform riset kuantitatif dan simulasi trading desk berbasis 3 AI Agent untuk pasar saham Indonesia (IDX). 

Dokumen ini adalah **panduan tata kelola resmi (Governance & Contribution Guide)** untuk seluruh pengembang, quant researcher, data engineer, dan AI engineer yang bekerja secara kolaboratif pada repositori ini.

---

## 1. Prinsip Utama & Aksioma Non-Negosiasi (Non-Negotiable Invariants)

Setiap kontributor **WAJIB** memahami dan mematuhi batas-batas arsitektur dan tata kelola berikut:

1. **Tepat 3 Runtime Decision Agents (Strict 3-Agent Pipeline)**:
   - Sistem hanya memiliki 3 runtime agent: **Agent 1 (Quant)**, **Agent 2 (Market Intelligence & Red Team)**, dan **Agent 3 (Investment Committee & Risk)**.
   - Dilarang membuat Agent 4 (`AGENT_4 = FORBIDDEN`). Seluruh kapabilitas analisis relasional dan entitas merupakan fondasi data bersama (Knowledge Data Platform) yang dikonsumsi oleh Agent 2.
2. **Local-Only & Paper Trading Only**:
   - Sistem beroperasi secara lokal dan simulasi paper trading (`LIVE_EXECUTION = BLOCKED`, `PAPER_ONLY = TRUE`).
   - Tidak ada koneksi API broker atau eksekusi riil otomatis ke pasar bursa langsung.
3. **Scientific Branch Frozen & Immutable**:
   - Cabang riset saintifik historis `COBA_001` hingga `COBA_018` telah resmi **DITUTUP DAN BEKU SECARA PERMANEN**.
   - Dilarang membuat eksperimen alpha baru (`COBA_019 = NONE`) atau melakukan optimasi parameter strategi secara berulang pada data out-of-sample (`STRATEGY_OPTIMIZATION = BLOCKED`).
4. **Aksioma Non-Kausalitas (Non-Causality Axiom)**:
   - Bukti sebelum keputusan tidak sama dengan kepastian hasil pasca keputusan: $\text{PRE\_DECISION\_EVIDENCE} \neq \text{POST\_DECISION\_OUTCOME}$.
   - Dilarang mengklaim hubungan kausal (causality) atau standalone alpha tanpa pengujian out-of-sample yang terverifikasi dan beku.
5. **Integritas Point-in-Time (PIT) & Anti-Halusinasi**:
   - Agent dan modul analisis **DILARANG** mengarang (hallucinate) data kepemilikan, relasi entitas, atau katalis berita.
   - Jika bukti faktual tidak ada dalam basis data kanonikal: kembalikan status `UNKNOWN`, bukan `FALSE` atau data karangan.
   - Semua data relasi dan kejadian wajib memiliki batas waktu yang valid (`valid_from <= AS_OF` dan `publication_time <= AS_OF`) untuk mencegah *lookahead bias*.

---

## 2. Struktur Repositori Kanonikal (Single Source of Truth)

Repositori SwingDeck dijaga ketat oleh *Architecture Enforcement Gate*. Seluruh file dan folder harus berada di lokasi kanonikal berikut:

```text
SwingDeck/
├── .github/            # GitHub Actions CI workflow, PR, dan Issue templates
├── agents/             # Logika inti ketiga agen (agent1_quant, agent2_intelligence, agent3_committee)
├── configs/            # Konfigurasi deklaratif YAML (universe, risk, models, backtest)
├── core/               # Shared runtime engines (Knowledge Data Platform, Risk Engine, Simulation)
├── dashboard/          # Antarmuka monitoring (Streamlit UI & FastAPI backend)
├── data/               # Data store kanonikal (DuckDB graph & Parquet market lakes)
├── docs/               # Dokumentasi arsitektur data dan spesifikasi sistem
├── gates/              # Bukti evaluasi dan artefak gate saintifik yang telah ditutup
├── governance/         # Peta arsitektur, change control, dan catatan tata kelola
├── knowledge/          # Memori sistem, taksonomi ontologi, dan panduan domain
├── logs/               # Telemetri eksekusi dan log audit
├── positions/          # Buku besar posisi paper trading aktif (terisolasi)
├── queue/              # Antrean pesan antar-agen dan transaksional job queue
├── reports/            # Laporan audit formal dan deliverable gate
├── research/           # Eksperimen riset historis yang telah dibekukan
├── runtime/            # Status runtime mutable trading desk
├── scratch/            # Ruang kerja temporer untuk skrip diagnostik
├── scripts/            # Skrip otomasi, pemeliharaan, truth gate, dan audit scanner
├── state/              # Status persisten engine
├── tests/              # Test suite (Unit, Integrasi, Metamorphic, Adversarial, Enforcements)
├── .env.example        # Template konfigurasi variabel lingkungan lokal
├── .gitignore          # Aturan penyaringan file sensitif dan cache
├── CODE_OF_CONDUCT.md  # Pedoman perilaku komunitas & kontributor
├── CONTRIBUTING.md     # Panduan kontribusi dan tata kelola kolaborasi ini
├── LICENSE             # Lisensi resmi proyek (MIT License)
├── main.py             # Entry point CLI interaktif SwingDeck
├── pytest.ini          # Konfigurasi runner pengujian Pytest
├── README.md           # Panduan onboarding dan dokumentasi utama proyek
├── requirements.txt    # Daftar dependensi resmi Python
└── SECURITY.md         # Kebijakan pelaporan kerentanan dan perlindungan rahasia
```

> **Catatan Penting**: Dilarang membuat file acak atau direktori "ghost" di root folder. Setiap penambahan file baru di root wajib didaftarkan pada whitelist `tests/test_00_architecture_enforcement.py`.

---

## 3. Standar Penulisan Kode (Coding Standards & Style Guide)

Untuk menjaga kode tetap bersih, mudah dibaca, dan konsisten bagi seluruh tim:

### Standar Python (PEP 8 + Type Hints)
- **Nama File & Folder**: Gunakan format `snake_case` (contoh: `trading_desk_simulation.py`, `agent1_quant/`).
- **Nama Class**: Gunakan format `PascalCase` (contoh: `KnowledgeDataPlatform`, `RiskEngine`).
- **Nama Fungsi & Metode**: Gunakan format `snake_case` (contoh: `evaluate_setup()`, `synthesize()`).
- **Nama Variabel**: Gunakan format `snake_case` (contoh: `target_price`, `portfolio_risk`).
- **Nama Konstanta & Enum**: Gunakan format `UPPER_CASE` (contoh: `MAX_CONCURRENT_POSITIONS = 5`, `DecisionAction.BUY`).
- **Type Hinting**: Gunakan type hints (`typing`) pada setiap fungsi publik untuk kejelasan tipe data.

Contoh implementasi standar:
```python
from typing import Dict, Any, List, Optional
from core.decision import DecisionResult, PortfolioContext

class RiskValidator:
    """Memvalidasi batas risiko portofolio untuk kandidat setup."""
    
    def __init__(self, max_risk_pct: float = 0.005) -> None:
        self.max_risk_pct = max_risk_pct

    def validate_allocation(self, context: PortfolioContext, setup: Dict[str, Any]) -> bool:
        # Implementasi deterministik
        ...
```

### Standar Dokumentasi
- Gunakan bahasa yang ringkas, jelas, dan lugas.
- Berikan docstring pada setiap modul, class, dan fungsi utama.
- File dokumentasi berformat Markdown (`.md`) dengan penamaan uppercase untuk dokumen kanonikal (contoh: `README.md`, `GOVERNANCE.md`, `DATA_ARCHITECTURE.md`).

---

## 4. Alur Kerja Pengembangan (Git & Development Workflow)

### A. Konfigurasi Lingkungan Lokal
1. **Clone Repositori**:
   ```bash
   git clone <repository_url>
   cd SwingDeck
   ```
2. **Buat & Aktifkan Virtual Environment**:
   ```bash
   # Menggunakan Python 3.12+
   python -m venv .venv
   
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. **Instal Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```

### B. Strategi Percabangan (Branching Model)
- Branch `main`: Branch utama yang stabil, terproteksi, dan selalu dalam kondisi 100% test pass.
- Format penamaan feature branch:
  - `feat/nama-fitur`: Untuk penambahan modul atau kapabilitas baru.
  - `fix/nama-perbaikan`: Untuk perbaikan bug atau refactoring komponen.
  - `docs/nama-dokumen`: Untuk pembaruan dokumentasi atau panduan.
  - `test/nama-pengujian`: Untuk penambahan regression/adversarial test suite.

### C. Alur Pembuatan Fitur Baru
1. Buat branch baru dari `main`:
   ```bash
   git checkout -b feat/tata-kelola-data
   ```
2. Implementasikan perubahan secara minimalis dan deterministik.
3. Tambahkan unit test / integration test di direktori `tests/`.
4. Jalankan seluruh uji validasi wajib sebelum mengajukan Pull Request.

---

## 5. Checklist Pra-Commit & Validasi Wajib (Pre-Commit Checklist)

Sebelum melakukan commit dan membuat Pull Request, pastikan seluruh pengujian berikut **100% LULUS (GREEN)** di lingkungan lokal Anda:

- [ ] **1. Architecture Enforcement Check**:
  ```bash
  pytest tests/test_00_architecture_enforcement.py -v
  ```
  *(Memastikan tidak ada file liar/ghost files di root)*

- [ ] **2. Operational Test Suite**:
  ```bash
  pytest -m operational
  ```
  *(Memastikan seluruh alur operasional 3-agent dan data platform berjalan 100% sukses)*

- [ ] **3. Semantic & Evidence Truth Gate Scan**:
  ```bash
  python scripts/run_truth_gate.py
  ```
  *(Memastikan zero integrity findings pada basis data pengetahuan dan entitas)*

- [ ] **4. Tidak Ada Hardcoded Secrets**:
  *(Pastikan tidak ada API key, token, atau kredensial rahasia yang ter-commit ke Git)*

---

## 6. Prosedur Review Pull Request (PR Review Criteria)

Setiap Pull Request akan ditinjau oleh Senior Architect dan Tim Pengembang berdasarkan kriteria berikut:
1. **Kepatuhan Invarian Arsitektur**: Tidak melanggar aturan 3-Agent, tidak mengubah branch riset beku (`COBA`), dan tidak menambahkan live execution.
2. **Kualitas Pengujian**: Memiliki cakupan test yang memadai (termasuk skenario adversarial & edge cases).
3. **Deterministik & Replayability**: Output sistem harus dapat direproduksi secara persis melalui timestamp / replay snapshot.
4. **Dokumentasi Lengkap**: Setiap perubahan konfigurasi atau skema data wajib dicatat pada `knowledge/canonical/PROJECT_MEMORY.md` dan dokumen terkait di `docs/`.

---
*Tata kelola ini berlaku untuk seluruh kontributor SwingDeck demi menjaga standar profesional, keamanan, dan keberlanjutan sistem.*

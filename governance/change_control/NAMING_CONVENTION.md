# NAMING CONVENTION GOVERNANCE

## 1. Historical Research Lineage
Semua identifier penelitian historis (seperti `AU`, `AW`, `AX`, `AY`, `AZ`, dan seri `ZZZ.*`) adalah **bagian permanen dari lineage ilmiah**.
- **JANGAN** merename file `batch_au_*`, `batch_aw_*`, atau `batch_zzz_*` menjadi skema nama yang baru.
- Nama-nama ini mempertahankan traceability menuju evidence dan gate conclusions aslinya.
- *Lineage > Cosmetic Consistency.*

## 2. New Experiments & Tests (COBA Rule)
Mulai Node ZZZ.14.9, SEMUA test, experiment, dan validasi BARU wajib menggunakan aturan penamaan `COBA`:
- Format: `COBA_<KODE_URUT>` (Contoh: `COBA_001`, `COBA_002`).
- Nomor harus sequential dan increment dari nomor COBA tertinggi yang ada di seluruh repository.
- **JANGAN** menggunakan tanggal, bulan, atau batch untuk experiment baru (e.g., `batch_xx` is deprecated for new experiments).
- Test script diletakkan di `tests/coba/COBA_001/` dan evidence/report diletakkan di `research/experiments/COBA_001/` atau `gates/evidence/COBA_001/`.

## 3. New Research Gates
- Research gates baru menggunakan identifier gate yang ditetapkan oleh governance architecture.
- **JANGAN** merename gate formal menjadi COBA. COBA adalah bagian dari eksperimentasi menuju suatu gate.

## 4. System Artifacts
- Modul sistem, utilitas, dan skrip core menggunakan penamaan yang deskriptif dan operasional (misal: `ablation_engine.py`).

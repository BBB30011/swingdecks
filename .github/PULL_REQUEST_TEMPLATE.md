## 📋 Ringkasan Perubahan (Summary)
<!-- Jelaskan secara ringkas perubahan atau fitur yang diajukan dalam Pull Request ini -->

## 🎯 Jenis Perubahan (Type of Change)
- [ ] 🐛 Bug fix (perbaikan non-breaking untuk masalah yang ada)
- [ ] ✨ New feature (penambahan fitur baru yang mematuhi arsitektur 3 agen)
- [ ] 📝 Documentation (pembaruan atau penambahan dokumentasi)
- [ ] ⚡ Performance improvement / Refactoring (tanpa mengubah fungsionalitas)
- [ ] 🧪 Tests (penambahan atau perbaikan unit/integration tests)
- [ ] 🛡️ Security / Governance (peningkatan keamanan atau penegakan tata kelola)

## 🏛️ Kepatuhan Arsitektur (Architectural Invariants Checklist)
- [ ] **Strict 3-Agent Pipeline**: Tidak ada inisialisasi atau penambahan Agent 4 (`AGENT_4 = FORBIDDEN`).
- [ ] **Paper Trading Only**: Eksekusi live tetap diblokir (`LIVE_EXECUTION = BLOCKED`).
- [ ] **Point-in-Time (PIT) Integrity**: Tidak ada lookahead bias atau kebocoran data masa depan.
- [ ] **Anti-Hallucination**: Data yang tidak ditemukan mengembalikan status `UNKNOWN`.
- [ ] **Architecture Whitelist**: Tidak ada file liar di root folder (`test_00_architecture_enforcement.py` lulus 100%).

## 🧪 Hasil Pengujian (Testing Done)
<!-- Tuliskan tes apa saja yang telah dijalankan di lingkungan lokal -->
```bash
pytest tests/test_00_architecture_enforcement.py -v
pytest tests/test_agent2_semi_manual_news.py -v
```

## 🔒 Pemeriksaan Keamanan Kredensial
- [ ] Saya memastikan **TIDAK ADA** token, API key, password, atau data sensitif yang terunggah dalam commit ini.

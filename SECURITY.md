# Kebijakan Keamanan (Security Policy)

Keamanan informasi, model, dan lingkungan eksekusi adalah prioritas utama dalam ekosistem **SwingDeck**.

---

## 🛡️ Kebijakan Kredensial & Rahasia (Credential & Secret Protection)

1. **Dilarang Melakukan Commit Token / API Key**:
   - Kontributor **DILARANG KERAS** menyertakan GitHub Personal Access Token (PAT), OpenAI/Anthropic/Gemini API Key, kredensial broker, atau private keys ke dalam commit git, PR, issue, atau file kode apa pun.
   - Gunakan selalu file `.env` lokal yang telah terdaftar di `.gitignore`.
2. **Environment Template**:
   - Salin [`.env.example`](.env.example) menjadi `.env` di lokal Anda untuk mengisi kredensial.
3. **Penyaringan Otomatis (Pre-Commit / Secret Scanner)**:
   - Repositori dilengkapi dengan aturan `.gitignore` ketat untuk memblokir file rahasia (`.env`, `*.pem`, `*.key`, `*.cert`).

---

## 🔒 Perlindungan Integritas Keputusan & Data

1. **Firewall MNPI (Material Non-Public Information)**:
   - Data internal atau bocoran non-publik dilarang masuk ke dalam pipeline keputusan. Semua informasi harus bersumber dari pengumuman bursa publik atau rilis media resmi berintegritas.
2. **Prompt Injection Firewall**:
   - Input berita teks dan analitik eksternal disaring untuk mencegah instruksi adversarial yang dapat memanipulasi keputusan Agent 2 atau Agent 3.
3. **Isolasi Paper Trading**:
   - Sistem secara default beroperasi dalam mode paper trading saja (`LIVE_EXECUTION = BLOCKED`).

---

## 🚨 Melaporkan Kerentanan Keamanan (Reporting a Vulnerability)

Jika Anda menemukan potensi celah keamanan (security vulnerability) pada repositori ini:

1. **JANGAN** membuat issue publik di GitHub.
2. Laporkan secara bertanggung jawab (Responsible Disclosure) melalui fitur **GitHub Security Advisory** pada repositori [https://github.com/BBB30011/swingdecks/security/advisories/new](https://github.com/BBB30011/swingdecks/security/advisories/new).
3. Sertakan deskripsi terperinci, langkah-langkah untuk mereproduksi celah keamanan, dan potensi dampaknya.
4. Tim pengelola akan meninjau laporan dalam waktu 1x24 jam kerja dan memberikan pembaruan status perbaikan secara berkala.

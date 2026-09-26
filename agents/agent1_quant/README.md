# Agent 1: Quantitative Engine

> **NOTE:** This agent operates strictly under the core constraints defined in the master constitution: [AGENTS.md](../../AGENTS.md).
## Tanggung Jawab
Menyaring ribuan saham menjadi kandidat unggulan (Top N) secara deterministik menggunakan *technical scanner*, indikator momentum, filter likuiditas, penilaian _price action_ dan membandingkannya terhadap Benchmark pasar.

## Output
Agent 1 tidak menghasilkan keputusan BUY atau SELL. Hasil dari Agent 1 di-*push* ke dalam queue untuk Agent 2.

### Komposisi Fitur Kunci
* **Market Regime & Stock Regime**
  Sistem menghitung kondisi tren dan volatilitas pada masing-masing saham, lalu mengukur kondisi tersebut terhadap acuan indeks utama (seperti IHSG). Status yang diakui:
  * `BULL`: Harga > SMA20 > SMA50 dan Return 20 hari > 0
  * `BEAR`: Harga < SMA20 < SMA50 dan Return 20 hari < 0
  * `SIDEWAYS`: Tertahan dalam rentang tanpa arah pasti
  * `HIGH_VOLATILITY`: Fluktuasi tidak wajar (contoh ATR melebihi 5% harga tutup)
  * `UNKNOWN`: Data riwayat insufisien atau terjadi kekosongan.

* **Regime Alignment**
  Arah pasar diuji sinkronisasinya:
  * `REGIME_ALIGNED`: Saham dan indeks mengarah ke rezim yang sama
  * `REGIME_CONTRARY`: Divergensi yang berlawanan (e.g. Saham BULL saat Market BEAR)
  * `REGIME_MIXED`: Salah satu berada di persimpangan SIDEWAYS atau belum teridentifikasi.

* **Benchmark Returns & Relative Strength**
  Agent 1 memisahkan performa nominal versus performa relatif. Saham yang melesat 5% dalam 20 hari patut diuji: apakah indeks (IHSG) juga naik 5% atau ternyata malah anjlok?
  ```text
  Contoh:
  BBCA Stock 20D = +12%
  IHSG 20D = +4%
  
  Relative Return 20D = +8%
  Relative Strength State = OUTPERFORMING
  ```
  _Catatan: Outperformance bukan jaminan kenaikan berikutnya. Metrik ini murni merupakan landasan analisis._

* **Flow Analytics (Price-Volume Relationship)**
  Agent 1 juga memindai keterkaitan antara pergerakan harga dan partisipasi volume untuk mendeteksi proxy jejak akumulasi atau distribusi:
  * **Price-Volume Confirmation**: `CONFIRMED` jika return 20 hari positif divalidasi dengan peningkatan volume berbanding 20 hari sebelumnya. Sebaliknya bisa menandakan `DIVERGENCE`.
  * **Accumulation/Distribution (AD)**: Menggunakan metodologi Marc Chaikin (*Money Flow Multiplier*) untuk memetakan kekuatan penutupan harga (*close*) relatif terhadap rentang harian (*high-low*). Tren AD dihitung via kemiringan (*slope*).
  * **Up/Down Volume Ratio**: Rasio perbandingan total volume saat harga naik berbanding saat harga turun selama 20 hari ke belakang.
  * **Buying/Selling Pressure Proxy**: Volume di setiap bar disortir berbasis pergerakan _Close_ vs _Open_ (Candle-based) untuk meraba persentase dominasi pembelian vs penjualan.
  * **Flow State**: Kesimpulan empiris (`ACCUMULATION`, `DISTRIBUTION`, atau `NEUTRAL`).

  > **DISCLAIMER TEKNIS**: Flow analytics berbasis OHLCV merupakan *proxy statistik* dan TIDAK dapat digunakan untuk memastikan identitas, intervensi, atau kepastian aktivitas pelaku pasar tertentu ("bandar" / "smart money"). Sistem tidak melontarkan jaminan pergerakan masa depan atau garansi likuiditas.

* **Anti Look-Ahead System**
  Kesesuaian timestamp diproses *strictly backward-looking*. Observasi perbandingan indeks hari ini HANYA menengok observasi indeks maksimum hingga hari yang sama, dan menolak indeks di hari-hari esok meskipun tabel CSV mencatatnya.

* **Evidence Quality Layer (Batch T)**
  Mekanisme deterministik untuk mengevaluasi kelengkapan data (evidence) yang mendasari sebuah *Quant Score*. Fitur kuantitatif diklasifikasikan ke dalam grup (Trend, Momentum, Price Action, Volume, dsb) dan ketersediaan nilainya (`AVAILABLE` vs `MISSING`) dievaluasi objektif tanpa menilai "baik" atau "buruknya" fitur tersebut.
  * **Quant Score vs Quant Confidence**:
    * **Quant Score**: Mengukur kekuatan setup dari kandidat berdasarkan indikator (Contoh: seberapa kuat trennya?).
    * **Quant Confidence**: Mengukur kelengkapan *evidence* yang menyokong *Quant Score*, bukan mengukur probabilitas arah harga atau probabilitas profit.
    * *Contoh A*: Score = 90, Confidence = 95 (Setup sangat kuat, fitur lengkap).
    * *Contoh B*: Score = 90, Confidence = 45 (Setup terlihat kuat, tetapi banyak fitur penting seperti MACD atau Relatif Volume berstatus *Missing* / `UNKNOWN`).
  * **Candidate Quality**: Kategorisasi akhir (`HIGH`, `MEDIUM`, `LOW`, `INSUFFICIENT`) yang ditentukan dari matriks *Score* dan *Confidence*. Hal ini dikonversi menjadi `research_priority` (`P1`-`P4`) sebagai acuan pendalaman riset bagi agen berikutnya.

## Arsitektur Aliran Data
```text
Historical CSV -> MarketSnapshot -> Liquidity Analyzer -> QuantFeatureEngine & FlowFeatureEngine -> MarketScanner (Score + Evidence) -> Research Queue
```

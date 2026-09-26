# Quant Feature Engine & Market Scanner

Pembaruan pada Batch Q meningkatkan _QuantFeatureEngine_ dan _MarketScanner_ untuk menghasilkan pengukuran yang jauh lebih kaya dan presisi tanpa perlu bantuan model AI prediktif, dengan menjamin kompatibilitas _backward_.

## 1. Fitur Baru

`QuantFeatureEngine` kini menghasilkan puluhan komponen baru di luar Trend/Momentum/Volume dasar:

- **Relative Strength:** Return aset historis dalam periode `5D`, `10D`, `20D`, dan `60D`.
- **Price Action Quality:** Ekstraksi struktur pergerakan jarak harga terhadap `HIGH_20D`, `LOW_20D`, posisi penutupan (`close_position_in_range`), hingga indikator `breakout` level resistensi sebelumnya tanpa *future leak* (mengambil nilai observasi _rolling_ dari _t-1_).
- **Trend Quality & Divergence:** Jarak persentase antara harga aset dengan garis moving average (`SMA20_DISTANCE`, `EMA50_DISTANCE`, dsb.).
- **Volume Trend:** Peningkatan rata-rata 5 hari terakhir diuji terhadap rata-rata 15 hari sebelumnya untuk menemukan _Volume Expansion_.
- **Volatility Status:** Rasio `ATR_PERCENT` digunakan untuk mendeduksi state market (`LOW`, `NORMAL`, `HIGH`, `EXTREME`) yang akan dioper ke _Agent 2 Research_.
- **Data Sufficiency:** Pipeline mendeteksi bila ada aset minim riwayat (<200 hari), menolak _crash_ (_graceful degradation_), melaporkan fitur `None`, dan mengisi status kecukupan data.

## 2. Peringkat & Skor Scanner Terkini

Batas bawah kandidat adalah `60 poin` yang direpresenetasikan dengan skor batas maksimal *100*.

1. **Trend Score** (Max 35)
2. **Momentum Score** (Max 25)
3. **Volume Score** (Max 15)
4. **Price Action Score** (Max 20) — Poin dicetak dengan posisi harga tinggi di rentang konsolidasi, positive return, breakout di atas resistensi t-1, dan volume expansion.
5. **Relative Strength Score** (Max 15) — Akselerasi nilai pada 20-hari dan periode panjang.
6. **Data Quality Score** (Max 10) — Freshness data.

`MarketScanner` menjumlahkan keenam metrik di atas secara deterministik, lalu memastikan bahwa total di-_cap_ pada `min(total, 100)`.

## 3. Sistem Anti Look-Ahead Bias

Keseluruhan *Quant Engine* bertumpu pada _Strict Timestamp Validation_:
1. Input Data masuk ke `pandas`.
2. Pipeline menghapus _(drop)_ bar mana pun yang waktu berjalannya melampaui waktu valid (_as_of_timestamp_ atau waktu operasional *snapshot*).
3. Parameter seperti `breakout` tidak membandingkan harga hari ini dengan rekor tertinggi yang melibatkan harga hari ini, melainkan harga hari ini dibandingkan dengan puncak harga teratas t-1 mundur hingga t-20.
4. *Look-Ahead Test* dalam set regresi menjustifikasi bahwa kalkulasi dengan parsial limit waktu ekuivalen persis tanpa selisih koma dengan proses dataset penuh.

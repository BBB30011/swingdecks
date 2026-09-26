# CSV Market Data Source

`CSVMarketDataSource` merupakan implementasi pembaca historical data pasar dari file CSV lokal secara offline (tanpa API internet). Modul ini bertugas sebagai batu loncatan transisi dari _Synthetic Mock Data_ menuju data asli, menguji ketangguhan arsitektur Agent 1 Pipeline dengan data dunia nyata yang lebih fluktuatif.

## Mode Provider

Project kini mendukung dua jenis provider:
1. **MOCK (`MockMarketDataSource`)**: Men-generate bar history sintetis berdasar fungsi matematis secara *on-the-fly*.
2. **CSV (`CSVMarketDataSource`)**: Membaca file `.csv` aktual dari direktori konfigurasi (default: `data/raw/`).

Pengaturan dapat diubah di `config/data_source.yaml`:
```yaml
data_source:
  provider: "CSV"  # atau "MOCK"
  csv:
    directory: "data/raw"
```

## Mode Operasi: HISTORICAL vs LIVE

Sejak Batch P, arsitektur `Agent1QuantPipeline` dan `LiquidityAnalyzer` membedakan _intent_ beroperasinya pipeline berdasarkan konfigurasi mode:

```yaml
data_source:
  mode: "HISTORICAL"  # atau "LIVE"
```

* **LIVE Mode (Default)**: Snapshot data dituntut untuk mutlak `FRESH` (berumur lebih muda dari `max_age_minutes`). Bila data CSV yang dipasok adalah riwayat tahun lalu, status kualitasnya akan divonis `STALE` dan **akan ditolak (rejected)** oleh tahapan Liquidity Filter demi alasan keamanan sistem real-time trading.
* **HISTORICAL Mode**: Mode ini khusus untuk riset dan *backtesting*. Data akan tetap diberi label `STALE` oleh enjin utama (karena waktu sistem yang nyata lebih maju jauh dari bar CSV terakhir), **namun sistem Liquidity Analyzer diizinkan meloloskan bar STALE ini**. Ini menjaga ketepatan _data quality constraints_ tanpa memblokir pipeline untuk memproses simulasi sejarah.

> **Peringatan**: Historical data dapat digunakan untuk research/backtest secara luas, tetapi **tidak otomatis dianggap fresh untuk live decision support**. Anda diwajibkan menggunakan mode `LIVE` untuk memastikan Agent tidak salah ambil posisi akibat data usang.

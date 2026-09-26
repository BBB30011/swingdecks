# DATASET IMPORT INSTRUCTIONS

## Required Dataset

Place compliant IDX historical CSV files into:
`data/raw/historical/`

Minimal required columns (case-insensitive, customizable order):
- symbol (usually derived from filename)
- date/timestamp
- open
- high
- low
- close
- volume

Recommended:
- `IHSG.csv` for benchmark
- Several years of daily history across multiple sectors
- Historical universe information
- Corporate action metadata
- Suspension/delist metadata
- Source provenance

**Warning:**
A dataset that only contains currently active stocks may suffer from severe survivorship bias.
Please provide `dataset_metadata.yaml` describing the provenance.

## Recommended Directory Structure

```text
data/
└── raw/
    └── historical/
        ├── dataset_metadata.yaml
        ├── BBCA.csv
        ├── BBRI.csv
        ├── BMRI.csv
        ├── BBNI.csv
        ├── TLKM.csv
        ├── ASII.csv
        ├── ...
        └── IHSG.csv
```

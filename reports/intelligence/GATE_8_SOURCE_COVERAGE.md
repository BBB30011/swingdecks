# SWINGDECK — GATE 8: SOURCE COVERAGE AUDIT REPORT

## 1. SCOPE & OBJECTIVE

This document provides a detailed breakdown of the 12 observed source classes across the canonical Gate 8 scale cohort (`COHORT_GATE8_CANONICAL_V1`).

---

## 2. SOURCE CLASS TAXONOMY & COVERAGE MATRIX

| Source Class | Publisher Type | Observed Real-World Sources | Ingestion Protocol | Integrity Status |
|---|---|---|---|---|
| `IDX_EXCHANGE` | Exchange Authority | PT Bursa Efek Indonesia Official Announcements | Structured PDF / JSON API | `READY` |
| `OJK_REGULATOR` | Capital Market Regulator | Otoritas Jasa Keuangan Statutory Circulars | PDF Direct Capture | `READY` |
| `COMPANY_ISSUER` | Listed Corporates | IDX Issuer Filings (ADRO, BBRI, ANTM, etc.) | Canonical PDF / E-Filing | `READY` |
| `GOVERNMENT_MINISTRY` | Government Ministries | Kementerian ESDM, Kemenkeu, Kemendag Decrees | Official Gazettes | `READY` |
| `CENTRAL_MACRO_AUTHORITY` | Central Bank | Bank Indonesia Monetary Decisions & 7D RR | Press Releases / Statements | `READY` |
| `CORPORATE_DISCLOSURE` | Listed Corporates | Statutory Material Information Disclosures | Exchange Feeds | `READY` |
| `FINANCIAL_REPORT` | Listed Corporates | Audited Quarterly & Annual Reports | Tabular Disclosures | `READY` |
| `CORPORATE_ACTION` | Listed Corporates | Dividend, Spinoff, Rights Issue Announcements | Exchange Disclosures | `READY` |
| `REGULATORY_DOCUMENT` | Statutory Authority | State Gazettes (Lembaran Negara) | PDF Direct Capture | `READY` |
| `REPUTABLE_MEDIA` | Financial News Media | Bisnis Indonesia, Kontan, Bloomberg Technoz | HTML Article Scraping | `READY` |
| `WIRE_SERVICE` | News Wires | LKBN Antara Syndicated Feeds | Syndication Feed Ingestion | `READY` |
| `OFFICIAL_PDF_GAZETTE` | State Publisher | Berita Negara RI / JDIH Portals | Official Legal Gazettes | `READY` |

---

## 3. PROVENANCE & AUTHENTICITY ENFORCEMENT

- Every ingested document computes a raw SHA-256 binary hash upon ingestion.
- The hash is linked to the verified source identity before entering the canonical DuckDB platform.
- Unverified publishers or orphan payloads without cryptographic provenance are assigned `UNVERIFIED` and excluded from clean intelligence retrieval.

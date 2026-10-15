# SWINGDECK — TEMPORAL TRUTH HARDENING REPORT (GATE 1)

## EXECUTIVE SUMMARY

This report documents the architectural hardening of temporal semantics and Point-in-Time (PIT) isolation in SwingDeck under Gate 1 of the Intelligence Upgrade V1.1+.

Prior to this upgrade, naive timestamp representations posed systemic risks of lookahead bias, timezone misalignment (e.g., mixing Jakarta local time WIB with UTC), and implicit collapsing of publication time into availability time. Gate 1 introduces an explicit 4-timestamp model, Indonesian timezone normalization engine, derivation method provenance tracking, and explicit temporal confidence grading.

---

## 1. THE 4-TIMESTAMP MODEL

Every piece of information, claim, and evidence in SwingDeck is bound to four strictly differentiated temporal dimensions:

```
  REAL WORLD OCCURRENCE         DISCLOSURE / PUBLISHED        SYSTEM AVAILABILITY           SYSTEM INGESTION
 ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
 │      event_time      │ ───► │     published_at     │ ───► │     available_at     │ ───► │     observed_at      │
 └──────────────────────┘      └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
  When the real-world           When the source               When the information          When SwingDeck engine
  corporate/economic action     disclosed/published the       became publicly queryable     ingested and recorded
  occurred (e.g. AGM vote,      document (e.g. portal         (e.g. feed push /             the record in DB.
  MoU signing).                 timestamp).                   index availability).
```

### Table Representation (`evidence` & `information_items`)

```sql
ALTER TABLE evidence ADD COLUMN event_time VARCHAR;
ALTER TABLE evidence ADD COLUMN published_at VARCHAR NOT NULL;
ALTER TABLE evidence ADD COLUMN available_at VARCHAR NOT NULL;
ALTER TABLE evidence ADD COLUMN observed_at VARCHAR NOT NULL;
ALTER TABLE evidence ADD COLUMN timestamp_source VARCHAR DEFAULT 'SOURCE_METADATA';
ALTER TABLE evidence ADD COLUMN derivation_method VARCHAR DEFAULT 'SOURCE_ARTICLE_METADATA';
ALTER TABLE evidence ADD COLUMN temporal_confidence VARCHAR DEFAULT 'EXACT';
```

---

## 2. INDONESIAN TIMEZONE NORMALIZATION ENGINE

The normalization engine (`core/source_authenticity.py:normalize_timestamp_to_utc`) handles all standard Indonesian timezones, ISO offsets, and fallback modes, converting all internal representations to canonical UTC ISO-8601 strings (`YYYY-MM-DDTHH:MM:SSZ`) while preserving original provenance:

### Supported Timezone Offsets

| Timezone Code | Standard Offset | Region Coverage | Normalization Logic |
| :--- | :--- | :--- | :--- |
| **WIB** | UTC+7 | Western Indonesia (Jakarta, Sumatra, West/Central Java) | $T_{\text{UTC}} = T_{\text{WIB}} - 7\text{ hours}$ |
| **WITA** | UTC+8 | Central Indonesia (Bali, Kalimantan, Sulawesi) | $T_{\text{UTC}} = T_{\text{WITA}} - 8\text{ hours}$ |
| **WIT** | UTC+9 | Eastern Indonesia (Maluku, Papua) | $T_{\text{UTC}} = T_{\text{WIT}} - 9\text{ hours}$ |
| **ISO Offset** | $\pm\text{HH:MM}$ | Explicit numerical offsets (e.g. `+07:00`, `Z`) | Native standard timezone parsing |
| **Missing / Malformed** | Fallback | Unparseable or absent raw timestamps | Handled via `RETRIEVAL_CLOCK_FALLBACK` with `TEMPORAL_CONFIDENCE = FALLBACK` |

---

## 3. DERIVATION METHODS & AVAILABILITY CONFIDENCE

### Timestamp Derivation Methods (`TimestampDerivationMethod`)
1. `EXCHANGE_METADATA`: Extracted directly from official IDX disclosure metadata fields.
2. `ISSUER_METADATA`: Formally published in issuer prospectus / filing header.
3. `SOURCE_ARTICLE_METADATA`: Extracted from news article header or meta tags.
4. `HTTP_HEADER`: Derived from HTTP `Last-Modified` or `Date` response headers.
5. `RSS_METADATA`: Extracted from RSS/Atom `pubDate` XML tags.
6. `ARTICLE_BODY_PARSE`: Parsed from in-text date references within the article body.
7. `STRUCTURED_FEED`: Ingested from real-time API or webhook payload.
8. `RETRIEVAL_CLOCK_FALLBACK`: Derived from local retrieval timestamp when source metadata is missing.
9. `INFERRED`: Derived via cross-referencing related event clusters.
10. `UNKNOWN`: Unverifiable timestamp derivation.

### Availability Confidence Levels (`TemporalConfidence`)
- `EXACT`: Timestamp is directly verified from primary source metadata with exact second precision.
- `DERIVED`: Timestamp is computed from HTTP headers or reliable secondary metadata.
- `ESTIMATED`: Timestamp is inferred from body text or neighboring cluster events.
- `FALLBACK`: Source timestamp was missing or corrupted; system retrieval clock was used as upper bound.
- `UNKNOWN`: Insufficient evidence to establish timing confidence.

---

## 4. POINT-IN-TIME (PIT) RETRIEVAL INVARIANT

All knowledge retrieval operations (`core/knowledge_retrieval.py`) strictly enforce the PIT rule:

$$\text{decision\_time} \ge \text{available\_at}$$

No information with $\text{available\_at} > \text{as\_of}$ can ever be returned to Agent 2 or Agent 3.

```python
# Canonical PIT Filter
query = """
    SELECT * FROM information_items
    WHERE available_at <= ?
    ORDER BY available_at DESC
"""
```

---

## 5. TEST VERIFICATION EVIDENCE

The temporal truth hardening implementation was verified across multiple rigorous test classes in `tests/test_intelligence_upgrade_v11.py` and `tests/test_natural_information_ingestion.py`:

- `test_gate1_temporal_truth_and_timezone_normalization`: Verified WIB (UTC+7), WITA (UTC+8), WIT (UTC+9), missing timezone fallback, and derivation method propagation.
- `test_gate1_pit_isolation_and_future_leak_prevention`: Proved that documents with future `available_at` are completely invisible to retrieval at `as_of`.
- `test_metamorphic_temporal_monotonicity`: Verified that expanding query time horizons monotonically non-decreases the visible information set without leaking future records.

**Status: CERTIFIED & COMPLIANT**

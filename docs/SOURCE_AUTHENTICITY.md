# SwingDeck Source Authenticity Model V1

## 1. Governance Axiom: Source Registry != Source Authenticity

A fundamental principle of SwingDeck's information architecture is that **a matching domain or source registry entry is necessary but NOT sufficient proof of source authenticity**. 

```text
HOSTNAME == EXPECTED_DOMAIN  ≠  DOCUMENT_IS_AUTHENTIC
```

Document-level authenticity must be dynamically evaluated across cryptographic, structural, temporal, and semantic dimensions.

---

## 2. Formal Source Authenticity Record

Every ingested external document receives a structured `SourceAuthenticityRecord` containing the following evaluated dimensions:

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `source_id` | `str` | Deterministic canonical source identifier (e.g. `SRC_IDX_PRIMARY`, `SRC_CNBC_ID`) |
| `publisher_name` | `str` | Verified canonical publisher legal name |
| `publisher_type` | `str` | `EXCHANGE`, `REGULATOR`, `CENTRAL_BANK`, `MINISTRY`, `NEWS`, `MEDIA`, `AGGREGATOR` |
| `canonical_domain` | `str` | Registered primary authority domain |
| `canonical_url` | `str` | Canonical normalized URL |
| `retrieval_url` | `str` | Exact network endpoint requested |
| `protocol` | `str` | Network protocol (`https`, `http`) |
| `tls_verified` | `bool` | True if retrieved over valid, verified TLS/HTTPS session |
| `retrieval_timestamp`| `str` | ISO-8601 UTC timestamp of retrieval execution |
| `publication_timestamp`| `str` | Extracted or declared publication timestamp |
| `last_modified_timestamp`| `str` | HTTP `Last-Modified` or article update timestamp |
| `content_hash` | `str` | SHA-256 cryptographic digest of raw byte payload |
| `mime_type` | `str` | Verified MIME type (`text/html`, `application/pdf`, `application/xml`) |
| `http_status` | `int` | Network response status code |
| `redirect_chain` | `List[str]` | List of intermediate redirect hops |
| `content_length` | `int` | Payload size in bytes |
| `encoding` | `str` | Detected character encoding (e.g. `utf-8`) |
| `document_identifier` | `str` | Deterministic fingerprint combining domain, path, and hash |
| `source_identity_evidence` | `Dict[str, Any]` | Detailed evidence payload (e.g. registry matches, security flags) |
| `authenticity_status` | `AuthenticityStatus`| `VERIFIED`, `PARTIALLY_VERIFIED`, `UNVERIFIED`, `REJECTED`, `UNKNOWN` |
| `authenticity_reason` | `str` | Explanatory audit justification |
| `origin_class` | `OriginClass` | Categorical source authority tier |
| `access_class` | `AccessClass` | Classification for trading decision eligibility |

---

## 3. 26-Vector Source Authenticity & Adversarial Attack Suite

SwingDeck subjects every ingestion candidate to a comprehensive 26-vector verification and attack matrix:

1. **Protocol Insecurity**: Non-TLS plain HTTP requests are downgraded or rejected.
2. **Open Redirect Abuse**: Divergence in domain hops during redirection triggers rejection.
3. **Domain Lookalike / Typo-Squatting**: Unregistered domains claiming official identity fail closed.
4. **Empty / Null Payload**: Content lengths below minimum thresholds are rejected.
5. **Oversized / Bomb Payloads**: Documents exceeding safety bounds (>25MB) are dropped.
6. **HTTP Error Responses**: 4xx / 5xx HTTP responses are rejected without state mutation.
7. **Future Publication Timestamps**: Timestamps ahead of UTC retrieval clock are marked `REJECTED`.
8. **Missing Mandatory Timestamps**: Documents with zero temporal metadata are restricted.
9. **Impossible / Anachronistic Dates**: Dates preceding domain creation or canonical era bounds fail validation.
10. **Altered / Corrupted Content**: SHA-256 mismatch against raw disk payload triggers immediate invalidation.
11. **Hash Collision / Truncation**: Hash verification enforces complete 256-bit digests.
12. **MIME Type Mismatches**: Executables or binary payloads claiming text status are blocked.
13. **Prompt Injection inside Article**: Injection markers (`IGNORE ALL PREVIOUS INSTRUCTIONS`, `SYSTEM OVERRIDE`) are flagged as untrusted inert data.
14. **Decision Hijack Payloads**: Malicious text instructing buy/sell commands is neutralized.
15. **System Prompt Leak Probes**: Text querying agent system instructions is sanitized.
16. **Suspected Material Non-Public Information (MNPI)**: Leaked memos or insider drafts are classified `MNPI_SUSPECTED` and blocked from trading eligibility.
17. **Unauthorized Private Data**: Internal private documents without explicit authorization are blocked.
18. **Missing Publisher Attribution**: Articles lacking attributable publisher identity default to `UNVERIFIED`.
19. **Entity Impersonation**: Erroneous ticker assignments are caught by the 5-tier semantic entity resolver.
20. **Semantic Mismatches**: Classifying `IDX` as regulator or `OJK` as exchange fails ontology validation.
21. **Syndicated Duplicate Masking**: Wire copies are linked to original sources rather than counted as independent corroboration.
22. **Silent Revision Overwrites**: Document changes produce new versioned records (`DOC_..._REV_N`), preserving historical baseline.
23. **Poisoned HTTP Headers**: Malformed headers or spoofed server tokens are stripped.
24. **Path Traversal Filenames**: Filenames containing `../` or invalid characters are sanitized before storage.
25. **Decompression / ZIP Bombs**: Compressed streams are inspected before extraction.
26. **Untrusted Fallback Classification**: Unknown source categories default to `UNKNOWN` and fail closed.

---

## 4. Origin & Authority Hierarchy

Sources are categorized categorically based on legal and institutional authority:

- `PRIMARY_OFFICIAL`: Direct statutory body (e.g. Government Gazette, Central Bank).
- `PRIMARY_REGULATORY`: Financial regulator disclosures (e.g. Otoritas Jasa Keuangan / OJK).
- `PRIMARY_EXCHANGE`: Market operator filings (e.g. PT Bursa Efek Indonesia / IDX).
- `PRIMARY_CORPORATE`: Official issuer investor relations disclosures.
- `SECONDARY_REPUTABLE`: Regulated institutional financial press (e.g. Bloomberg, Reuters, CNBC Indonesia).
- `SECONDARY_MEDIA`: General mass media publications.
- `AGGREGATOR`: News aggregators and RSS feeds (e.g. Yahoo Finance).
- `SOCIAL`: Public social discourse and discussion boards (strictly unverified).
- `UNKNOWN`: Unclassified origin (Fail-Closed).

# SWINGDECK — GATE 8: EVENT, LINEAGE & SYNDICATION REPORT

## 1. EVENT CLUSTERING & SYNDICATION CONTROL

A fundamental principle of SwingDeck is:

$$\text{SOURCE\_COUNT} \ne \text{INFORMATION\_INDEPENDENCE}$$

Multiple media portals repeating a single news wire or multiple filings concerning a single corporate action must not artificially inflate corroboration counts.

---

## 2. POPULATION SUMMARY

| Dimension | Count | Description |
|---|---|---|
| **Raw Documents** | **120** | Ingested text payloads and filings |
| **Unique Events** | **94** | Distinct real-world event occurrences |
| **Event Clusters** | **94** | Canonical event aggregation nodes |
| **Independent Lineages** | **76** | Independent factual origin lineages |
| **Revisions (Errata)** | **24** | Linked correction filings modifying prior documents |
| **Syndications (Wires)** | **24** | Verbatim wire reproductions collapsed to 1 corroboration |

---

## 3. NON-INFLATION INVARIANTS

- **Syndication Inflation Rate:** **0.00%** (0 / 120). Wire syndications never increase the corroboration count beyond 1.
- **Revision Link Rate:** **100.00%** (24 / 24 revisions correctly reference `prior_document_id`).

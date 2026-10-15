# SWINGDECK — GATE 8: REPRODUCIBILITY & DETERMINISM AUDIT

## 1. REPRODUCIBILITY INVARIANT

$$\text{RUN\_A} \equiv \text{RUN\_B} \quad \land \quad \text{REBUILD\_A} \equiv \text{REBUILD\_B}$$

Every Gate 8 observation, metric, entity resolution, and exposure graph path must be 100% bitwise deterministic across independent runs.

---

## 2. DETERMINISM AUDIT RESULTS

Across independent engine runs:
- `dataset_hash` match: **100.00%** (`d720b0808a38545e8fbe58fd8c5ec1231ea7ea8269e80b272f2323ef4545d656`)
- `manifest_hash` match: **100.00%** (`645856ebbc7e383187cceb3724c979c09930ba79f2fe12999e04fc197bbf2234`)
- Float differences: **0**
- Ordering discrepancies: **0**

---

## 3. GRAPH DERIVATION DETERMINISM

Dropping and re-deriving the exposure graph directly from the canonical DuckDB platform yields bitwise identical adjacency matrices, cycle detections, and path weights.

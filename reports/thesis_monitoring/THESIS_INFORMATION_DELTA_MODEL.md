# THESIS INFORMATION DELTA MODEL

The Information Delta Engine computes changes sequentially:
1. **BASELINE (T0)**: The array of string descriptors representing information known at position entry.
2. **CURRENT (Tn)**: The array of string descriptors known now.
3. **DELTA**: Array subtraction (`CURRENT - BASELINE`) reveals newly added information. Contradictions are mathematically compared (e.g. `0 -> 2`).

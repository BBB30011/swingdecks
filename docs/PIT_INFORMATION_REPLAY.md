# SwingDeck Point-in-Time (PIT) Information Replay V1

## 1. Temporal Integrity & Lookahead Elimination

A core requirement for quantitative research and production backtesting in SwingDeck is strict Point-in-Time (PIT) information safety. Information that was published or made available after a decision timestamp $T_0$ must NEVER appear in the context available at $T_0$.

$$\text{Decision Time } (T_0) \ge \text{Information Availability Time } (T_{\text{avail}})$$

---

## 2. Six Distinct Temporal Dimensions

SwingDeck explicitly tracks six discrete timestamps for every natural information item:

| Timestamp Field | Semantic Meaning | Usage in PIT Engine |
| :--- | :--- | :--- |
| `event_time` | Time when real-world event occurred | Contextual reference only |
| `publication_time`| Time when document was published by original source | Base availability estimate |
| `availability_time`| Time when document became publicly accessible | **Primary PIT Filter Invariant** |
| `retrieval_time` | Time when SwingDeck pipeline fetched the document | Audit & observation clock |
| `valid_from` | Beginning of entity/relationship validity interval | Temporal graph filtering |
| `valid_to` | Expiration of entity/relationship validity interval | Temporal graph filtering |

---

## 3. Deterministic Historical Replay Protocol

To verify that the system is immune to future information leakage, the engine executes metamorphic replay testing (Test M3 & `test_pit_temporal_replay_and_future_leakage_isolation`):

```text
STEP 1: Retrieve state at T0 (2026-09-15)
        -> Output: Snapshot A (e.g. 1 evidence item)

STEP 2: Inject future document published at T2 (2026-09-20)
        -> Canonical store updated with future record

STEP 3: Re-execute query at T0 (2026-09-15)
        -> Output: Snapshot B

STEP 4: Invariance Verification
        -> Assert Snapshot A == Snapshot B (Bitwise & semantic equality)

STEP 5: Query at T3 (2026-09-25)
        -> Output: Contains both T0 and T2 records
```

---

## 4. Revision Replay Safety

When documents are edited or revised post-publication:
- Document V1 is preserved with its original `published_at` and `available_at` timestamps.
- Document V2 is stored as a distinct revision (`DOC_..._REV_2`) with a later `available_at` timestamp.
- A replay query as of $T_0$ (prior to V2 release) strictly retrieves V1, ensuring perfect historical reconstruction of what market participants knew at $T_0$.

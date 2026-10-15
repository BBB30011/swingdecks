# COBA_003 — PROTOCOL

## 1. INGESTION
1. Load `COBA_002_EMPIRICAL_OUTCOMES.csv` containing raw historical future returns.
2. Load predefined static `EXPOSURE_GROUPS` from core parameters.

## 2. CROSS-SECTIONAL MAPPING
For each setup record `[Ticker T, Date D]`:
1. Identify macro exposure group $G$.
2. Select $Peers = [P \in G \mid P \neq T]$.
3. For $H \in \{H1, H3, H5, H10, H20\}$:
   a. Query concurrent raw return for each $P \in Peers$ at Date $D$.
   b. Exclude missing (NaN) concurrent observations.
   c. Compute arithmetic mean $\mu_H = \text{mean}(Peers_H)$. If $Peers$ is empty, $\mu_H = 0$.

## 3. EXCESS CALCULATION
Subtract computed peer baseline:
$Excess_H = Return_{T, H} - \mu_H$

## 4. VALIDATION
1. Write point-in-time calculation to `COBA_003_EMPIRICAL_PEER_EXCESS.csv`.
2. Compute `SHA256` hashing on dual-run to guarantee deterministic extraction algorithm output.
3. Establish coverage matrix for unpopulated variables.

# SwingDeck

**SwingDeck** is an autonomous, quantitative swing trading research desk operated by three specialized AI Agents. The system is designed to discover swing trading opportunities in the IDX market with positive expected value through superior timing, asymmetric risk/reward setups, downside protection, and rapid invalidation.

## Architecture

The system operates with **EXACTLY 3 AGENTS**:
- **Agent 1 (Quant & Market Scanner)**: Quantitative features, relative strength, liquidity, market regime, flow accumulation, and candidate ranking.
- **Agent 2 (Market Intelligence & Red Team)**: Contextual Peers, Specificity, Asymmetric Beneficiaries, and Contradiction Analysis.
- **Agent 3 (Investment Committee & Risk Engine)**: Final synthesis, opportunity assessment, timing validation, R/R calculation, and position sizing.

## Repository Map

The repository follows a strict **One Purpose → One Canonical Location** rule.

- `agents/`: Core logic for Agent 1, 2, and 3.
- `core/`: Reusable runtime engines and shared interfaces.
- `research/`: Current research state and standalone experiments (`research/experiments/COBA_XXX/`).
- `gates/`: Immutable evidence and closed research artifacts.
- `knowledge/`: Shared organizational memory, failures, patterns, and agent-specific indexes.
- `tests/`: Scientific historical tests and infrastructure validation.
- `data/`: Canonical datasets and database stores.
- `scripts/`: Operational tools and maintenance audits.
- `reports/`: Generated human-readable summaries.
- `archive/`: Historical artifacts preserved strictly for lineage.
- `scratch/`: Ephemeral workspace (temporary only).

## Quick Start
```bash
# Run the entrypoint
python main.py

# Run the test suite
pytest -ra
```

## Scientific Guardrails

- `STRATEGY_OPTIMIZATION = BLOCKED`
- `STRATEGY_READINESS = NOT_READY`
- `NO_AUTO_ADVANCE = TRUE`
- **Scientific Immutability**: No methodology, dataset definition, estimand, or historical scientific state (ZZZ.14.9) may be altered without explicit validation.

## Governance & Knowledge

- **Governance Rules**: See `knowledge/canonical/GOVERNANCE.md`
- **Agent Knowledge**: See `knowledge/agent/AGENT_KNOWLEDGE_MAP.md`
- **Knowledge Registry**: See `knowledge/index/KNOWLEDGE_INDEX.md`

---
*Disclaimer: SwingDeck is an experimental research project. Do not consider its outputs as investment advice.*

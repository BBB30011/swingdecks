# SWINGDECK MARKET INTELLIGENCE & INFORMATION GRAPH
## CAPABILITY GAP ANALYSIS

| Capability | Existing | Gap | Action |
| --- | --- | --- | --- |
| Market | Partial (market_scanner.py, quant_features.py) | No link to intelligence graph | Refactor to link quant features to event edges |
| News | Basic (live_news_ingestion.py) | Lacks structured taxonomy, source quality tracking, deduplication | Implement Information Object Model, Clustering |
| Policy | None | No policy extraction or mapping | Build taxonomy, policy->sector mappings |
| Politics | None | No political entity or event tracking | Build political event taxonomy & entity models |
| Macro | None | No structured macro indicators | Integrate macro data to graph (interest rate, fx) |
| Social | None | No social sentiment/event ingestion | Build social event adapters and unverified firewall |
| Ownership | None | No ownership graph | Build ownership graph schema, entity relation `OWNS` |
| Corporate | Partial (dataset parsing) | No discrete event triggers | Extract discrete corporate events (management, dividends) |
| Entity | None (just symbol strings) | No deterministic entity resolution (aliases, hierarchy) | Build `EntityRepository`, resolution logic |
| Relationship | None | No edge definitions (OWNS, COMPETITOR_OF) | Build `RelationshipRepository`, graph traversal |
| Exposure | None | No mechanism linking policy/news to company | Build Exposure Mapping |
| Mechanism | None | No explicit hypotheses of impact | Build `MechanismHypothesis` structure |
| Provenance | Basic (decision_trace) | Lacks deep tracing from source to mechanism | Enhance provenance tracking on every node |
| PIT | Basic (replay_firewall) | Missing PIT limits on relationships & entity states | Add validity intervals (`valid_from`, `valid_to`) |
| Contradiction | Basic (red_team) | Not automated per-cluster | Build `ContradictionEngine` to cross-validate clusters |
| Information freshness | None | No decay models | Implement information validity windows |
| Intelligence graph | None | Flat JSON models | Build `InformationGraphEngine` (DuckDB backed) |
| Decision linkage | Basic | Needs to consume full graph state | Update Agent 2 & Agent 3 integration |
| Dashboard | Partial (Control Plane) | No Graph/Why did this move? view | Add Market Intelligence Map to dashboard |

## NEXT STEPS
1. Design canonical `Information`, `Entity`, and `Relationship` models.
2. Implement DuckDB backed `InformationGraphEngine`.
3. Design Taxonomies (Mechanism, Information).

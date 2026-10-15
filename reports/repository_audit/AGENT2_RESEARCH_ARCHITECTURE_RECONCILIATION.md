# AGENT 2 RESEARCH ARCHITECTURE RECONCILIATION

## 1. Current Architecture
Previously, the architecture attempted to shoehorn two distinct execution environments (the Python runtime and the IDE session) into a single runtime abstraction. The `Agent2ResearchProvider` in Python falsely assumed it could invoke `google.antigravity.Agent` to perform IDE-like web searches without passing API credentials, which led to a runtime crash because the Python SDK explicitly requires `GEMINI_API_KEY`. 

## 2. Capability Discovery Evidence
A rigorous capability discovery revealed the following facts:
- **IDE-Native Antigravity Agent**: `search_web`, `read_url_content`, `browser_subagent`, and reasoning are **AVAILABLE** natively within the IDE without external API keys.
- **Python Runtime (`google.antigravity` SDK)**: Available as a library, but strictly **REQUIRES** `GEMINI_API_KEY`. It does not magically bridge to the IDE authorization.
- **External API**: `GEMINI_API_KEY` and `OPENAI_API_KEY` are currently **UNAVAILABLE** in the environment.

## 3. Semantic Mismatch Found
The major semantic mismatch was treating `--mode web` as something the Python runtime could execute natively. Because the Python runtime cannot perform a web search without an API provider, executing `--mode web` natively in Python is structurally flawed. It forced a `ValueError: A Gemini API key is required` crash, masking it behind synthetic failovers rather than acknowledging the hard capability boundary between IDE tools and Python runtime.

## 4. Final Architecture
We have explicitly decoupled the execution layer into two distinct capability zones while strictly uniting them under a single downstream persistence layer.

- **IDE-Assisted WEB Mode**: The IDE Agent performs the research utilizing its free, built-in capability. It synthesizes a canonical `ResearchResult` payload and hands it off to Python via `AGENT2 INGEST NEWS <SYMBOL> <PATH>`.
- **API Runtime Mode**: The Python runtime operates purely as an API client. It routes `AGENT2 UPDATE NEWS <SYMBOL>` to Gemini or OpenAI. If no API key is found, it immediately and gracefully fails (`SOURCE_ACCESS_FAILURE`), without executing fake requests.

## 5. Command Contract
The command structure now honestly reflects the capabilities of the runtime:

- **IDE Request**: `AGENT2 UPDATE NEWS BBCA` (The IDE Agent does the research and saves a JSON payload).
- **Python Request**: `python main.py "AGENT2 UPDATE NEWS BBCA [--mode api]"` (Strictly API provider execution. Fails without credentials).
- **IDE Handoff (Python)**: `python main.py "AGENT2 INGEST NEWS BBCA data/cache/ide_payload.json"` (Python natively ingests the IDE's completed research).
- **Python Rejection**: If the user tries `AGENT2 UPDATE NEWS BBCA --mode web` in Python, Python actively rejects it with instructions to use the IDE Handoff command.

## 6. ResearchResult Contract
Both the API mode and the IDE-assisted WEB mode generate the exact same deterministically validated `ResearchResult` object containing:
- `mode`, `sources`, `evidence`
- `knowledge_delta` (ADDED, CONTRADICTED)
- `pit_status`

## 7. Provider Boundary
- `Agent2ResearchProvider` strictly governs the Python-runtime API integration. It no longer contains dead IDE SDK code.
- `LiveNewsIngestionEngine` strictly governs the downstream entity mapping, deduplication, and DuckDB storage, utterly agnostic to whether the payload was injected via the IDE or fetched via the API.

## 8. Security/Credential Boundary
- No API keys are hardcoded.
- IDE session credentials do not leak into the Python runtime.
- The Python runtime strictly adheres to `os.environ` for capability negotiation.
- `MOCK_FALLBACK = DISABLED`. `STATIC_INJECTION = DISABLED`.

## 9. PIT Boundary
All real-time or semi-manual research ingested through this pathway retains strict Point-in-Time (PIT) isolation.
- `is_pit_valid = True`
- `pit_reason = 'LIVE_ISOLATED'`
- `status = 'LIVE_ISOLATED'`
This permanently firewalls live data from historic replay runs.

## 10. Test Evidence
Unit testing was completely rewritten in `tests/test_agent2_semi_manual_news.py` to prove:
- `AGENT2 UPDATE NEWS BBCA` fails gracefully with `SOURCE_ACCESS_FAILURE` when no API capability exists.
- `AGENT2 UPDATE NEWS BBCA --mode web` is explicitly rejected by Python.
- `AGENT2 INGEST NEWS BBCA <filepath>` correctly parses and integrates the JSON payload via the unified Common Downstream Pipeline.
All tests currently **PASS**.

## 11. Remaining Blockers
- **API Mode Execution Test**: Because we lack a `GEMINI_API_KEY` / `OPENAI_API_KEY`, we cannot test the live end-to-end API mode over HTTP. The test validates the graceful failure instead.
- **IDE Payload Handoff Automation**: Currently, the IDE Agent must write the JSON to disk and call the command. We must rely on IDE tool invocations for this workflow.

## 12. COBA_001 Readiness
**READY**.
*Reason:* The architecture is now fundamentally honest. The capability boundaries are respected. We can confidently execute research via IDE handoff, knowing the Python runtime will enforce schema integrity, deduplication, and PIT firewalling perfectly. The research can safely proceed without risking the scientific integrity of the SwingDeck engine.

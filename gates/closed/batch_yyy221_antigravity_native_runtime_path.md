# Batch YYY.2.2.1 — ANTIGRAVITY NATIVE RUNTIME PATH INVESTIGATION

## 1. Mission
Determine whether SwingDeck can use the user's authenticated Antigravity environment as the reasoning runtime for Agent 2 WITHOUT requiring a separate `GEMINI_API_KEY`.

## 2. Environment Inspected
`google.antigravity` SDK in `.venv\Lib\site-packages\google\antigravity`, specifically the configuration handlers (`LocalAgentConfig`), connection logic (`LocalConnectionStrategy`), and endpoint validators (`GeminiAPIEndpoint`, `VertexEndpoint`).

## 3. SDK Version
Installed `google-antigravity` package version.

## 4. Official Authentication Modes
- `GeminiAPIEndpoint`: Requires `GEMINI_API_KEY` (via explicit arg or env var).
- `VertexEndpoint`: Requires either `GEMINI_API_KEY` OR explicit `project` + `location` (via explicit args or env vars `GOOGLE_CLOUD_PROJECT`/`GOOGLE_CLOUD_LOCATION`), relying on Vertex Application Default Credentials (ADC).

## 5. Tested Runtime Paths
- `LocalAgentConfig()` default invocation.
- `LocalAgentConfig(vertex=True)` invocation.
- Static analysis of SDK connection and validation modules.

## 6. IDE → Python SDK Bridge
**NOT SUPPORTED / NOT DOCUMENTED**. The Python SDK operates entirely standalone. It validates credentials locally via `validate_endpoint()` *before* spawning the Go-based `localharness` subprocess. There is no supported bridge to inherit the IDE's authenticated entitlement.

## 7. CLI Bridge
**NOT SUPPORTED / NOT DOCUMENTED**. The `localharness` binary is launched programmatically by the SDK over stdin/stdout config passing. It does not authenticate via the CLI.

## 8. Vertex / ADC
**BLOCKED**. Vertex authentication is officially supported by setting `vertex=True` and supplying a `project` and `location`. However, the current host environment does not possess configured Application Default Credentials (ADC) for a GCP project.

## 9. Local Runtime
**AVAILABLE**. The SDK supports local execution via LiteRT (`LiteRTAgentConfig`) and local OpenAI-compatible endpoints (`LocalOpenAIAgentConfig`). However, this is local execution of `.litertlm` models (e.g. Gemma), which is fundamentally different from executing the Gemini Cloud reasoning model.

## 10. Authentication Matrix

| Path                     | API Key | GCP Project | Existing Login | Local | Officially Supported | Current Environment | Result |
| ------------------------ | ------: | ----------: | -------------: | ----: | -------------------: | ------------------: | ------ |
| Default LocalAgentConfig |       ? |           ? |              ? |     ? |               NO     |   BLOCKED           |        |
| Gemini API               |     YES |          NO |             NO |    NO |               YES    |   BLOCKED           |        |
| Vertex + ADC             |      NO |         YES |            ADC |    NO |               YES    |   BLOCKED           |        |
| IDE Session Bridge       |       ? |           ? |            YES |     ? |               NO     |   N/A               |        |
| CLI Bridge               |       ? |           ? |            YES |     ? |               NO     |   N/A               |        |
| Local LiteRT             |      NO |          NO |             NO |   YES |               YES    |   AVAILABLE         |        |
| Local OpenAI-compatible  |     NO* |          NO |             NO |   YES |               YES    |   AVAILABLE         |        |

## 11. Security Findings
No credentials were created, extracted, or leaked. The SDK inherently fails closed, raising `ValueError` in Python when authentication conditions are not met, preventing the RPC harness from even launching.

## 12. Evidence
- Output of `minimal_auth_test.py` throwing `google.antigravity.types.AntigravityValidationError: A Gemini API key is required...`
- Source code in `google/antigravity/models.py` explicitly enforcing `if not (self.api_key or os.environ.get("GEMINI_API_KEY")):`
- Source code in `google/antigravity/connections/local/local_connection.py` executing `m.endpoint.validate_endpoint()` locally prior to `localharness` invocation.

## 13. What Worked
The Antigravity SDK correctly and cleanly boots its configuration stack and accurately validates the environment.

## 14. What Did Not Work
The pipeline could not acquire a valid credential without a manually supplied API key or explicit GCP project configuration. 

## 15. What Is Officially Supported
- Supplying a `GEMINI_API_KEY`.
- Using Vertex AI with Application Default Credentials (ADC).
- Running local models via LiteRT/OpenAI-compatible endpoints.

## 16. What Is NOT Supported / NOT Documented
- Bridging the Antigravity IDE authenticated session to the Python SDK.
- Extracting the session token to bypass the API key validator.

## 17. Architectural Impact
SwingDeck Agent 2 cannot execute Gemini Cloud reasoning autonomously within this exact environment constraint (no external API keys allowed, relying entirely on IDE authentication). 

## 18. Final Decision
**NATIVE_RUNTIME_BLOCKED**
No supported cloud bridge exists in the current environment that permits skipping explicit API Keys or Vertex ADC configuration.

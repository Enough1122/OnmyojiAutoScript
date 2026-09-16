> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Well-scoped fix with sensible precedence (pool-entry URL > config regional URL > default) and good fail-closed tests. A few points worth a look:

- **hermes_cli/runtime_provider.py:530-535 — scheme not validated.** `base_url_host_matches(cfg_base_url_or, "openrouter.ai")` checks the host but not the scheme, so a config value like `http://eu.openrouter.ai/api/v1` would be honored and the pooled OpenRouter credential would be sent over plaintext HTTP. Why it matters: this path attaches a pool token to a config-controlled URL, and the PR's own second test treats off-domain leakage as the threat. Suggestion: parse the URL and require `https` (allow plain http only for localhost) before applying the override.

- **hermes_cli/runtime_provider.py:524-525 — override gated on an explicit `provider: openrouter` key.** Users who reach OpenRouter via implicit provider inference (no `provider` key in their model config) still hit the original #91591 symptom, because `cfg_provider_or != "openrouter"` short-circuits the entire block. Why it matters: the bug report likely comes from users who never set that key. Suggestion: consider relaxing the gate to "configured base_url exists and is on-domain," or document the restriction so the partial fix is intentional.

- **hermes_cli/runtime_provider.py:526,533 — case sensitivity of the host check.** The provider string is lowercased, but `cfg_base_url_or` is matched with its original casing. If `base_url_host_matches` compares literally, `EU.OpenRouter.AI` would be silently rejected and the override skipped. Suggestion: normalize/lowercase the host before matching, or add a test pinning the helper's case-insensitivity so the assumption is explicit.

- **tests/hermes_cli/test_runtime_provider_resolution.py:442-561 — coverage gaps.** The three new tests cover regional-honored, off-domain-rejected, and entry-url-wins. Worth adding: (a) an on-domain `http://` URL to pin whatever scheme policy lands from point 1, (b) uppercase / trailing-slash variants of the regional host, (c) empty-string `base_url` falling back cleanly to the default endpoint.

Nit: hermes_cli/runtime_provider.py:524-526 — `cfg_provider_or` / `cfg_base_url_or` read ambiguously (`_or` scans like the `or` operator); `cfg_provider_openrouter` / `cfg_base_url_openrouter` would read more clearly beside the surrounding `cfg_base_url`.

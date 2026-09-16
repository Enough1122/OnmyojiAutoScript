> AI code review — automated review for reference; please use your judgment.

The simplification is coherent (one global Kimi endpoint, prefix sniffing deleted, tests rewritten to match). Points worth addressing:

- hermes_cli/auth.py:626 — issue — `_resolve_kimi_base_url` keeps the `api_key` parameter but never reads it anymore — why it matters — every caller must still thread the key through, and linters/dead-code analyzers will flag the unused arg, inviting drive-by cleanups that change the signature later anyway — suggestion — either drop the parameter and update the four call sites named in the docstring, or rename it `api_key_unused`/`_api_key` with a comment stating it is retained deliberately.

- hermes_cli/auth.py:637 — issue — the runtime resolver returns the raw `KIMI_BASE_URL` value, but the wizard (`model_setup_flows.py:2157`) computes `effective_base` with `.strip()`; a value like `" https://api.kimi.com/coding "` therefore survives the wizard untouched yet produces a malformed runtime URL with leading whitespace — why it matters — the two paths disagree on exactly the inputs users paste with stray spaces, yielding confusing connection errors only outside the wizard — suggestion — apply the same `.strip()` inside `_resolve_kimi_base_url` (and ideally validate the scheme) so wizard and runtime agree.

- plugins/model-providers/kimi-coding/__init__.py:117 — issue — the plugin base URL switches from an OpenAI-compatible `/v1` endpoint to the Anthropic-Messages-style `/coding` endpoint, but nothing in this diff shows the plugin's client construction/path building changing to match (the auth.py comment notes the SDK appends the path) — why it matters — if the plugin still builds OpenAI-style URLs it will 404 against the new host — suggestion — confirm/extend the plugin to construct the Anthropic-protocol client (or append the correct path) and add one integration-style assertion of the final request URL.

- hermes_cli/model_setup_flows.py:2160 — issue (error handling/migration) — existing users with legacy `platform.moonshot.ai` keys and no env override are silently rerouted to `api.kimi.com/coding` and will start failing auth with an opaque 401 — why it matters — nothing at failure time tells them why it broke or that `KIMI_BASE_URL=https://api.moonshot.ai/v1` restores the old behavior — suggestion — when a request against the coding endpoint returns 401/403 and the key lacks the `sk-kimi-` prefix, emit a one-line doctor/status hint about the legacy endpoint escape hatch.

- tests/hermes_cli/test_api_key_providers.py:690 — issue (coverage/lint) — `MOONSHOT_DEFAULT_URL` appears to lose its last uses in this rewrite; check the module-level import doesn't become dead, and the resolver suite no longer covers the empty-key path explicitly — why it matters — an unused import breaks lint gates and the removed branch was previously tested — suggestion — prune the import if unused and add a trivial `_resolve_kimi_base_url("", KIMI_CODE_BASE_URL, "")` case documenting the intended result.

No blocking issues found — the first three items are the ones I'd want confirmed before merge.

— reviewer-b (automated review)

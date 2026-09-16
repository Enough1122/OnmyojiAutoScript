> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-guarded design: the exhaustion verdict is a single shared constant matched by the consumer (so producer/consumer can't drift), `force_keyed` is a ContextVar-scoped token-reset override that provably doesn't leak to other vendors or past exceptions, eligibility excludes keyed-failures (keyless rescue's domain) and the tests assert the two gates are mutually exclusive, failure of the keyed retry preserves the original ring error with a note, and non-stickiness plus partial-batch/policy-block exclusions are all pinned. The 359-line test file mirrors the rescue suite faithfully. Findings:

1. hermes_cli/config_defaults.py:510 — `keyed_backstop` defaults to **true**, which makes automatic paid-API spending a silent default for anyone with a vendor key on file: the first time the free ring exhausts, money moves without the operator having opted in (the config comment argues a `free` pin is itself a spending decision, but `auto`-tier users with stored keys didn't make one either). One annotated call is modest, but this deserves loud release-notes/docs treatment at minimum — and consider whether default-off with a picker prompt fits the project's usual consent posture better.

2. plugins/web/keyless_mcp.py:use_keyless — the override is checked before tier logic and inherited by anything running inside the backstop's `with` block; if a provider's keyed path ever performs its *own* nested `web_search_tool`/ring dispatch (re-search, enrichment), that nested call silently rides the forced-keyed path too and spends again. Either assert/document non-reentrancy, or clear-and-restore the ContextVar around any nested dispatch boundary.

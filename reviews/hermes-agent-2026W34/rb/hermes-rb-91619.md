> AI code review — automated review for reference; please use your judgment.

Reasonable extension — anonymous-tier vendors do reject with 401/403 where keyed tiers wouldn't, and the digit-boundary regex correctly refuses `1403`/`4031` neighbors. Items:

- plugins/web/keyless_mcp.py:70 — issue — eligibility is substring-matched over the *entire* error string, and these vendors echo request context into errors; a terminal failure whose text embeds user content ("extract failed for 'forbidden kingdom trailer': connection timeout") now classifies as failover-eligible because of the quoted word — why it matters — the walk exists precisely to skip non-recoverable errors fast; echoing-query false positives turn every such error into a full-ring retry, adding latency and masking the real cause in the final "(all keyless vendors unavailable)" suffix — suggestion — anchor the markers to provider-error shape rather than free text (e.g., check only the portion after a known `failed:` separator, or require both a marker *and* an HTTP-status/code token), and pin the echoed-query case with a test asserting it stays terminal.

- plugins/web/keyless_mcp.py:886 — issue (design confirmation) — in `extract_with_failover`, a target *site* that bot-blocks crawlers with 403s (extremely common) now reads as provider-unavailable when every URL in the batch is so rejected, walking the entire ring for a page problem no vendor can fix — why it matters — the docstring's old distinction ("partial failures are page problems") still holds for partial batches, but all-403 batches used to mean throttling and now conflate two unrelated causes — suggestion — either accept it explicitly (different crawler infrastructure sometimes does get through; say so in the docstring) or distinguish via vendor-reported error codes where available.

- tests/tools/test_web_keyless_fallback.py:452 — issue (coverage) — `_is_failover_eligible` is only exercised indirectly; the interesting boundaries (`"HTTP 2403"`, `"error 4031"`, uppercase `FORBIDDEN`, empty string) have no direct assertions — suggestion — add a small parametrized unit test over the predicate itself so future marker additions can't silently break the boundary logic.

No blocking issues found — item 1 is the one most worth tightening since it trades away the failover walk's original purpose.

— reviewer-b (automated review)

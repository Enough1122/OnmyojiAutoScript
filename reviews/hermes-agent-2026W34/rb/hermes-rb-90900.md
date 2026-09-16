> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-scoped trust extension: mirroring the Portal allowlist's `loopback_http` carve-out is the right consistency argument, the bearer-to-your-own-machine exfiltration reasoning holds, and the fail-closed shape is preserved — prod-over-http and arbitrary hosts stay rejected, with tests pinning both positives *and* the carve-out's own boundaries (`http://attacker.com` stays None). Findings:

1. hermes_cli/auth.py:2378 — `::1` (IPv6 loopback) is missing from both the host allowlist and the http carve-out set. Local dev stacks bind `::1` routinely (uvicorn/FastAPI defaults listen on both families, and many tools emit literal `http://[::1]:port/v1` URLs), so a local Portal handing out an IPv6-loopback endpoint will hit exactly the #90895 silent-heal-to-prod degradation this PR fixes for 127.0.0.1. Add `"::1"` to `_ALLOWED_NOUS_INFERENCE_HOSTS` and to the scheme-carve-out set, plus a test for `http://[::1]:3114/v1`.

2. hermes_cli/auth.py:2430 — the loopback set is spelled out twice (allowlist frozenset vs. inline `{"localhost", "127.0.0.1"}` in the scheme check); when #1's `::1` gets added there are now three places to remember. Hoist a single `_LOOPBACK_HOSTS` frozenset used by both so the carve-out can't drift from the allowlist.

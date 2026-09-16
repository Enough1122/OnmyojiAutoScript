> AI code review — automated review for reference; please use your judgment.

Review of "fix(cron): fail-open preflight for router-internal provider names (#90220)". Reasonable resolution of the false-positive preflight: probing `resolve_provider` distinguishes genuinely unknown names (router-internal aliases) from real built-ins whose credentials are missing, keeping the actionable warning only where it's true. Suggestions:

1. cron/scheduler.py:4308 (no tests) — this adds TWO new branches to a critical preflight path with zero test coverage in the diff — one test per branch is cheap and load-bearing: built-in provider + AuthError still returns the credential message; router-internal name returns None (job proceeds).

2. cron/scheduler.py:4310 (bare `except Exception`) — any BUG inside `resolve_provider` (TypeError, import failure) is indistinguishable from "unknown provider name" and silently fails the check open — catch the specific unknown-provider error type if hermes_cli.auth exposes one, or at least log at debug when an unexpected exception type shows up so resolver breakage isn't invisible.

3. cron/scheduler.py:4311 (nit, document the trade-off) — fail-open means misconfigured custom-provider jobs now surface their credential problem only at run time with the raw runner error; one sentence in the comment noting that accepted cost would help future readers weigh re-tightening.

No blocking issues found.

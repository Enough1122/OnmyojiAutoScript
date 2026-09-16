> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Right observability fix for a genuinely silent failure class: "request arrived and was rejected with 4001" vs "request never arrived" are now distinguishable, the warning carries both the stale \`session_id\` and the request id plus the recovery hint (resume the stored session), and the regression test pins message content and error shape together. Scope is correct too — found-sessions return untouched, so the happy path gains zero overhead.

Nit: a client retry-looping against a long-dead session will emit one warning per RPC; if that ever gets noisy in practice, a per-session_id rate-limit (first occurrence + counter) would preserve diagnosability without spam. Fine as-is today.

No blocking issues found.
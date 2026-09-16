> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Carefully engineered for a notification feature: request-fenced observation of only authoritative snapshots, silent hydration baseline on first sight/scope change/reconnect (so offline replay doesn't spam), monotonic watermark advancement that survives overlapping lookups resolving out of order, in-flight de-dup keyed by generation+job+timestamp, and click-through resolved to the run nearest the accepted completion time. The nine-test matrix — including the out-of-order watermark case and the not-yet-visible-run retry — is exactly right. Findings:

1. apps/desktop/src/store/cron-completion-notifications.ts:runFailed — `last_status && last_status !== 'ok'` classifies *any* non-"ok" status string as a failure. If the backend ever emits `"success"`, `"completed"`, or a localized/legacy variant, users get an alarming "failed" native notification for a run that succeeded (the type was just widened to arbitrary strings with no enum contract in this PR). Invert to an explicit failure set (`{'error', 'failed', 'timeout'}`) or require `last_error`, so unknown statuses label the toast neutrally instead of as a failure.

2. apps/desktop/src/store/cron-completion-notifications.ts:observe catch-path — when `getRuns` keeps rejecting (gateway route removed, permission issue), every subsequent refresh re-attempts the lookup for that job indefinitely: each poll cycle costs a doomed RPC plus log noise, forever. The comment's rationale (jobs file visible before session row) justifies *a* retry window, not an unbounded one — cap consecutive misses per job (e.g. drop after N attempts, resurface on next real timestamp change).

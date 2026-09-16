> AI code review — automated review for reference; please use your judgment.

Review of "fix(cron): unify inactivity timeout policy". Right consolidation: one `resolve_cron_inactivity_timeout()` resolver (env override > `cron.inactivity_timeout_seconds` > 600s default) now feeds the inactivity monitor, the cwd-lock bound, AND the one-shot claim TTL, so those safety horizons can't drift apart — with tests pinning env-over-config precedence and the zero-means-unlimited fallback floors across all three consumers. The failure-summary reclassification is equally valuable: the watchdog's explicit signature is matched FIRST so an agent-inactivity kill is no longer misdelivered as a "provider timeout" (the old generic "timed out" substring caught it), and provider-timeout detection gained the specific vendor phrasings. Suggestions:

1. cron/jobs.py:resolve_cron_inactivity_timeout (negative values) — `float(candidate)` happily returns -5.0; run_job maps 0 to unlimited but a NEGATIVE limit likely means instant/inverted timeouts downstream — clamp negatives to the default (or 0) alongside the existing ValueError handling.

2. nit (classification coupling) — the watchdog branch matches its own prose ("cron job" + "idle for" + "last activity:"); fine since it's your error contract, but a structured error code on the raise site would survive future rewording better than three substrings.

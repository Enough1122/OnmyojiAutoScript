> AI code review — automated review for reference; please use your judgment.

Review of "fix(cron): refuse terminal one-shot resurrection and add re-arm". Right model: terminal jobs are immutable through the generic update door (with an actionable "use cron resume --run-now/--at" message), `trigger_job` refuses them up front, the scheduler's three entry points (advance, fire-claim, due-scan) ALL skip terminal records so no path resurrects by accident, and the explicit `rearm_oneshot` does the resurrection properly — once-kind only, live run/fire claims rejected under lock, counters reset, state rebuilt atomically. The console resume command grows --at/--run-now cleanly. Suggestions:

1. cron/jobs.py:2112 + 2205 (duplicated guard) — the identical 10-line terminal-activation raise appears twice inside update_job (before and after invariant merging); extract a small `_ensure_not_reactivating(job_before, job_after)` helper called once at the final checkpoint so the rule lives in exactly one place.

2. cron/jobs.py:9285-ish (magic TTL) — `_claim_is_live(job.get("fire_claim"), now, 300)` hardcodes 300s while the run-claim path uses `_oneshot_run_claim_ttl_seconds()`; import/reuse the fire-claim TTL constant so the two stay in sync when tuning changes.

3. nit — rearm_oneshot resets `repeat.completed` to 0 but leaves any other repeat fields untouched; one docstring line stating which fields carry over (and that created/updated history is preserved) would set expectations for users re-arming long-lived jobs.

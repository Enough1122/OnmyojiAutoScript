> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-executed: the snapshot hash is passed invocation-scoped into `_run_job_script` and injected *after* `build_subprocess_env()`/`env_overlay`, so a stale ambient `HERMES_MONITOR_LAST_OUTPUT_HASH` can't win; the `isinstance` guards on `monitor_state`/`last_output_hash` keep malformed jobs.json from crashing the source runner; both the override and the first-run-clears-to-empty semantics are pinned by tests; and the new docs section spells out the cross-process single-flight contract clearly.

Nit (non-blocking): cron/scheduler.py:3873 — the variable is only sanitized for *monitor-script* invocations; a regular cron job script still inherits any ambient `HERMES_MONITOR_LAST_OUTPUT_HASH` from the parent environment, which could confuse a shared single-flight adapter that keys off it outside the documented monitor context. Consider unsetting it (or documenting it as monitor-only) for non-monitor runs so the contract in cron-internals.md holds unconditionally.

No blocking issues found.

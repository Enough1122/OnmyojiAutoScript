> AI code review — automated review for reference; please use your judgment.

Review of "feat(cron): defer monitor state commit until delivery succeeds". Well-engineered feature: `_write_last_output_strict` gives atomic snapshot writes, `commit_monitor_state` orders snapshot-then-hash with a compensating rollback, ownership/shutdown fencing around the commit (`_monitor_commit_in_progress`, interrupted-at-commit recheck) is careful, and the 25-test matrix covers retry markers, delivery failures, owner loss, and shutdown races. Findings:

1. cron/scheduler.py:~6760 (binding safety) — `delivery_failed` is only ever ASSIGNED inside exception/error branches (`if delivery_error is not None`, `except` handlers); on a fully successful delivery it may be unbound when later read by `if pending_requires_delivery and (unresolved_origin or delivery_failed)` and the commit gating — if an initializer exists further up outside these hunks, fine, but please make it explicit (`delivery_failed = False` next to `monitor_retry = False`) so a future edit can't reintroduce an UnboundLocalError on the happy path.

2. cron/scheduler.py:4994 (staging location) — the pending commit is staged onto the SHARED `job` dict (`job["_monitor_pending_commit"]`); a crash or hard kill between staging and the decision point leaves the stale key persisted with the job, where the next run's `job.get("_monitor_pending_commit")` fallback could adopt an old observation — prefer treating the defer list as the only live channel (or pop the key at the start of run_job) so state can't survive the process boundary.

3. cron/scheduler.py:6695 (marker contract nit) — `deliver_content.strip().upper() == MONITOR_RETRY_MARKER` makes matching case-insensitive while the module docstring promises "the exact marker"; either compare exactly or update the doc so plugin authors know `[monitor_retry]` also trips it.

4. cron/monitor.py:247 (rollback completeness) — the compensating path restores the snapshot file but cannot restore `last_changed_at` semantics if `update_job` partially applied before failing; low risk given update_job is single-dict, but a one-line comment stating why hash+timestamp are assumed atomic in jobs.json would preempt future reordering.

Also nice: keeping the eager default as-is preserves back-compat, and plain-cron/default-monitor tests pin that `[MONITOR_RETRY]` from non-opted jobs stays ordinary output. No blocking issues found — items 1-2 deserve a look before merge.

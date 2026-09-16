> AI code review — automated review for reference; please use your judgment.

Correct contract enforcement: create/update/resume already reject will-never-fire schedules and recovery never resurrects them, so the due-scan dispatching hours-late wall-clock one-shots was the last inconsistent path. The gate's three-way split (retire+diagnose when never dispatched / keep when claimed so mark_job_run can still land / within-grace stays due) is exactly right, and the Run-button re-trigger test proves the escape hatch survives. Points:

1. cron/jobs.py:~3430 — a once-job beyond grace with `repeat.completed >= 1` (crash between execution and mark_job_run removal) gets retired with a diagnostic saying "removed **without running**" — factually wrong for that record and confusing during incident review. Consider branching the diagnostic text on `_completed`/`last_run_at` ("already executed at X; stale record retired").
2. Same hunk — the retire loop mutates `raw_jobs` while iterating but breaks immediately after removal, so it's safe today; a comment noting the break-dependency would prevent a future multi-removal edit from introducing a skip bug. (nit)
3. The gate runs before the #38758 dispatch-limit guard; a claimed-and-stale record now `continue`s past that guard every scan forever (record kept indefinitely while its claim never resolves). If claims have their own TTL/reaper this is fine — otherwise these rows accumulate. One sentence on claim lifetime would settle it. (nit)
4. Diagnostic content is genuinely operator-actionable (id, name, scheduled time, grace, removal time, recreate instructions) — exactly what a silent-drop should leave behind. (positive)

No blocking issues found.

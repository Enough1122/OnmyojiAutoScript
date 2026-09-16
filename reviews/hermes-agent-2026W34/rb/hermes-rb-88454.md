> AI code review — automated review for reference; please use your judgment.

Correct fix for #88443's observability gap, and the first-wins note about SessionDB's `ended_at IS NULL` update is an important detail handled at the right place. The dual-path regression tests with a recording SessionDB are well isolated. One coverage gap dominates everything else:

1. cron/scheduler.py:~5730 — `_cron_run_failed` is only set in the **exception** handler. But Hermes runs frequently fail *without raising*: `run_conversation` returns a result dict with `"failed": True` / `completed: False` (provider 401s, protocol violations, kanban fail-closed exits — several of this cycle's other PRs). Those runs currently fall through to the finally block with the flag still False and get stamped **"cron_complete"**, which is precisely the masking this PR exists to remove. After the result is inspected, set `_cron_run_failed = bool(result.get("failed"))` (plus any equivalent turn-exit signal), and add the matching test — the current fixtures only exercise the raise path.
2. Same region — confirm every *other* exit between session creation and the finally (lock fail-closed fires before creation per #79768, but audit-write or post-processing failures?) leaves the flag correctly False rather than defaulting to success-by-omission. A short comment enumerating intended outcomes would help.
3. Naming nit: consider `_cron_run_outcome` holding the reason string directly ("cron_failed"/"cron_complete") so adding future reasons isn't another boolean-plus-mapping. (nit)

No blocking issues found beyond item 1 — as written, the most common failure shape still lands as "complete".

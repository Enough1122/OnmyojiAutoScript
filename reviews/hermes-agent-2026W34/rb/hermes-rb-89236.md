> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good operational-hardening pair under one roof: `TaskHasActiveRunError` turns silent worker-orphaning into an explicit refusal with an actionable message (`--force` documented as the stuck-worker escape hatch that still lands the run as `reclaimed`), the active-run predicate correctly ignores stale rows whose `ended_at` is set so old work never trips the refusal, and triage decomposition gains sensible three-tier priority inheritance (per-child > caller flag > root's stored value, NULL→0 matching the column contract). The CLI reports per-id failures and refuses with distinct guidance. Findings:

1. hermes_cli/kanban_db.py:archive_task:7240 — the refusal relies on raising inside `write_txn` to undo the already-executed `UPDATE tasks SET status='archived'`. If `write_txn`'s context manager rolls back on exception this is exactly right — please add one test asserting `task.status` is *unchanged* after a refused archive (not just that the exception fired), since a non-rollback wrapper would leave the card archived while the caller believes nothing happened, which is worse than the original bug.

2. hermes_cli/kanban_db.py:7110 — `isinstance(child_pri, int)` admits booleans: YAML `priority: true` in a child spec becomes priority 1 silently. The codebase elsewhere guards `isinstance(x, bool)` before int handling (e.g. the synchronous-level resolver); mirror that here or coerce explicitly.

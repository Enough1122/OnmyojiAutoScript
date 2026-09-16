> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Strong worker-safety semantics: `TaskHasActiveRunError` (carrying task/run ids plus an actionable message) guards all three destructive paths — `archive_task` refuses without `--force` (which still lands the run as `reclaimed`), while `delete_task`/`delete_archived_task` refuse unconditionally since deletion has no graceful close path; the active-run predicate correctly ignores stale rows with `ended_at` set. Priority inheritance in triage decomposition (per-child > caller flag > root stored value) plus the LLM prompt's explicit priority discipline (inherit by default, never invent 0 under a high-priority parent) address real burial-of-work failures. Findings:

1. hermes_cli/kanban_db.py:7210 — the refusal raises inside `write_txn` after the `UPDATE ... status='archived'` has executed; correctness depends entirely on `write_txn` rolling back on exception. Add a test asserting the task's status is *unchanged* after a refused archive (not merely that `TaskHasActiveRunError` fired) — if any wrapper variant commits despite the raise, the operator sees an error yet the card disappears from the board anyway.

2. hermes_cli/kanban_decompose.py:91 — the prompt *promises* that "a lower priority with no reason is rejected and clamped back up to the parent's." Prompts are advisory; if the parser doesn't actually enforce the clamp, models that skip `priority_reason` silently demote children and the documented contract is fiction. Make sure the decomposition validator implements the clamp (drop invalid low priorities to the inherited value) and add a test for the no-reason-low-priority case.

3. Coordination — open #89236 ships the same archive-guard + priority-inheritance core on overlapping files (`kanban_db.py`, `kanban.py`). Whichever merges second needs a deliberate consolidation pass, or the board gains two divergent guard implementations.

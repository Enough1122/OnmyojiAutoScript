> AI code review — automated review for reference; please use your judgment.

Solid fail-closed design overall: classification at decompose time plus a re-block guard at dispatch covers both new children and stale/manual writers. Findings:

1. hermes_cli/kanban_db.py:10186 — no code path in this PR (or on main) ever sets `audit_status = 'approved'`. Combined with the dispatch guard that re-blocks any `external` task moved back to `ready`, a consequential child is permanently stuck unless someone hand-edits the DB. If the dedicated approval command ships separately, fine — otherwise consider adding at least an operator-facing `approve` action here so the state machine is completable.
2. kanban_db.py:7305 — classifier false positives are likely: `\b(send|email|message|notify)\b` and `\bmerge\b` also match read-only intents ("investigate the merge conflict", "draft the incident email for review"). Fail-closed is the right bias for a trust boundary, but worth documenting that over-blocking is expected and recording *which* pattern matched in the blocked event so tuning is possible later.
3. kanban_db.py:7461 — the child's `side_effect_class` is a binary label derived from the same regex hit that triggers blocking; a "comment on the Sentry issue" child becomes `external` even though the eventual action might be scoped read-only by a human. Storing the matched category in the blocked event would make triage much easier.
4. tests/hermes_cli/test_kanban_decompose_db.py:130 — good coverage of block-at-create and re-block-at-dispatch, but there is no test for the happy path of the new guard: an `external` task with `audit_status='approved'` should dispatch normally. That assertion is what pins the intended release mechanism.
5. kanban_db.py:10190 — under `dry_run`, external/unapproved tasks are skipped silently and never appear in the result, so a dry run understates what a live dispatch would do. Consider recording them (e.g. `result.would_block`) for operator visibility.
6. kanban_db.py:7319 — the pattern tuple is rebuilt on every call; hoisting it to a module-level constant is trivial and keeps the trust-boundary rules in one visible place. (nit)

No blocking issues found.

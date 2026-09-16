> AI code review — automated review for reference; please use your judgment.

Both halves solve real operational pain and the tests encode the incident details (1400 events/day from one card; a retired `upx-*` role deadlocking a dependency chain silently). The streak walk's reason-change reset and the backdated-seed test setup show unusual care. Items:

- hermes_cli/kanban_db.py:8159 — issue — the nonspawnable-alert dedupe uses `payload LIKE '%"assignee": "{assignee}"%'` without escaping LIKE metacharacters — why it matters — an assignee containing `%` or `_` (legal in a typo'd string) makes the pattern over-match, suppressing a *new* alert for a genuinely different assignee; also the JSON-serialized payload may contain escaped sequences that break naive substring matching for exotic names — suggestion — escape via `assignee.replace("%", "\\%").replace("_", "\\_")` with `ESCAPE '\\'`, or store/dedupe on a structured column instead of a LIKE scan.

- hermes_cli/kanban_db.py:10390 — issue (verification) — after escalation calls `block_task(...)`, the card leaves ready/review so the branch won't refire — but confirm `block_task` inside this path can't silently fail (e.g., sticky-block guard treating it as a duplicate) while the task *stays* ready; then every subsequent tick re-runs the escalation arm (`should_escalate` remains true) and re-benches it — suggestion — assert post-condition (`task.status == 'blocked'`) after calling, log when it didn't take.

- hermes_cli/kanban_db.py:10405 — nit — the ~40-line dedupe/escalation block is duplicated verbatim between the ready lane and the review lane; extracting `_handle_respawn_guard(conn, row_id, guard_reason, lane)` would halve the surface these future policy changes must touch.

No blocking issues found — item 1 is the one I'd fix before merge.

— reviewer-b (automated review)

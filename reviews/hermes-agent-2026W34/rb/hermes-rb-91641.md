> AI code review — automated review for reference; please use your judgment.

Strong design: deriving the hold purely from durable machine-state events (comments can't clear it), enforcing it at recompute/claim/specify/decompose layers, and the stale-writer demotion inside the claim transaction is exactly right. The test file covers the racy-promotion and exactly-once-recovery cases well. Items:

- hermes_cli/kanban_specify.py:242 — issue (design verification) — `recover_block_loop_hold=True` is passed unconditionally by `specify_task`, so *any* caller of that API — including programmatic/tooling flows, not just an interactive operator — clears the hold as a side effect — why it matters — if any automation ever calls specify (scripts, future auto-triage), it will silently release loop-escalated tasks and the block→loop→hold→recover cycle can resume, defeating this PR's purpose through a legitimate-looking door — suggestion — confirm every current caller is operator-facing, and consider gating recovery on the author identity (e.g., refuse when author matches the known auto-decomposer profile) or exposing the flag only on the CLI layer.

- hermes_cli/kanban_decompose.py:471 — issue (performance) — `list_triage_ids` now runs `has_block_loop_hold` once per candidate row (up to the 1000-row limit), i.e., up to 1000 extra SELECTs per poll tick on a busy board — why it matters — this function runs repeatedly from the auto-decomposer loop; the cost scales linearly with triage depth and most rows won't be held — suggestion — fold the predicate into the main query (`NOT EXISTS (SELECT 1 FROM task_events e WHERE e.task_id = tasks.id AND e.kind IN ('block_loop_detected','block_loop_recovered') ORDER BY e.id DESC LIMIT 1 ...)`-style latest-event filter, or a single aggregate join).

- hermes_cli/kanban_db.py:4660 — nit — every claim attempt on a held task appends a `claim_rejected` event; an aggressive dispatcher ticking every few seconds against a long-held task will accumulate hundreds of identical rows, bloating `task_events` and burying useful history — suggestion — suppress duplicates within a short window (e.g., only record when the previous event of that kind is older than N minutes) or coalesce counts into the payload.

- tests/hermes_cli/test_kanban_block_loop_hold.py:44 — issue (coverage) — the stale-writer scenario is pinned at the claim layer but not at `recompute_ready` (a held row forced to `todo`/`ready` should be skipped/demoted there too) — why it matters — recompute is the other writer that could resurrect a held task, and its branch currently has no regression test — suggestion — mirror the `UPDATE tasks SET status='ready'` trick against recompute_ready and assert it leaves the row non-dispatchable.

No blocking issues found — item 1 wants an explicit answer before merge; the rest are hardening.

— reviewer-b (automated review)

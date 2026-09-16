> AI code review — automated review for reference; please use your judgment.

1. **hermes_cli/kanban_db.py:10250-10255 and :10382-10387 (fix core)** — syncing `claimed.branch_name` before persisting is the right call: the spawned worker now observes exactly the branch written to the DB, closing the first-dispatch mismatch. **Why it matters:** previously the DB held the resolved fallback (`wt/<id>`) while the in-memory task still carried `None`/stale value, so the first worker could spawn on the wrong base. **Suggestion:** none needed for logic; see item 2 for keeping the two copies honest.

2. **hermes_cli/kanban_db.py (both lanes)** — the corrected five-line block is duplicated verbatim between the ready-lane and review-lane dispatchers. **Why it matters:** this codebase already shows the cost of lane drift — the bug being fixed here existed because two near-identical dispatch blocks must stay in sync manually. **Suggestion:** extract a helper, e.g. `_persist_resolved_branch(conn, claimed, resolved_branch_name)`, and call it from both lanes so the invariant lives in exactly one place.

3. **tests/hermes_cli/test_kanban_worktree_isolation.py:129-176 (new tests)** — good parametrized coverage of both lanes plus the negative directory-workspace case, but every scenario exercises only the `f"wt/{id}"` terminal fallback (resolver monkeypatched, `branch_name` unset at creation). **Why it matters:** the precedence chain `resolved_branch_name > stripped existing > wt/<id>` is the actual contract, and its first two links are untested. **Suggestion:** add a case where the task is created with `branch_name="existing"` and the resolver returns a different branch — assert the spawn sees the resolver's branch and the DB agrees; and one where the resolver returns `None` to prove the existing name survives.

4. **tests/hermes_cli/test_kanban_worktree_isolation.py (negative test)** — consider also asserting that a directory-workspace task gets no row-level branch write at all (e.g. via `set_branch_name` spy), since "no invented branch" is currently only observed through the task object's field. **Why it matters:** a regression that writes branches for dir tasks would still pass today if only the field stayed `None`. **Suggestion:** wrap `kb.set_branch_name` with a recorder and assert zero calls for the dir lanes.

Nit: a whitespace-only stored branch (`"   "`) silently collapses to `wt/<id>` — reasonable, but worth a comment since it is the only place stripping changes persistence semantics.

— Reviewed by Hermes AI reviewer (reviewer-f2)

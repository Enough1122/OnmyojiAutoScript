> AI code review — automated review for reference; please use your judgment.

Review of "feat(kanban): add guarded admin archive workflows". This is careful destructive-operation engineering: layered authorization (toolset check → allowlist with normalization → handler-level recheck → delegated-child refusal), actor derived from runtime profile rather than model args, read-only planner shared by dry-run and execution, refusal-before-write everywhere, transactional archive/unarchive with persisted actor+reason, and a genuinely impressive test suite (~3.4k lines across three files). Findings:

1. hermes_cli/kanban_db.py:7690 (TOCTOU window) — the closure/active-run snapshot is computed read-only, workers are terminated, and only then does `write_txn` begin without re-validating: a run that STARTS between planning and the transaction gets its DB rows archived/claims cleared (`_end_run`, NULLed pointers) while its worker PROCESS was never SIGTERMed — it survives as an orphan writing to an archived task — cheap fix: re-run the `_task_active` scan inside the transaction and refuse/extend termination on new actives.

2. hermes_cli/kanban_db.py:8095 (silent global recompute on no-op restore) — `admin_unarchive` runs `recompute_ready(conn)` unconditionally after commit, including group-mode restores where every member was skipped (restored_ids empty) — recompute is documented (in the archive path's own warnings!) as globally promoting unrelated eligible tasks — skip it when `restores` is empty, or gate it behind a flag symmetric to `allow_promotions`.

3. hermes_cli/kanban_db.py:4473 (scope note) — the payload-aware `_has_sticky_block` change alters EXISTING behavior for every normal `recompute_ready` flow, not just admin archives: dependency/review resumption blocks without a `reason` now auto-recover where they were previously sticky forever — correct for the feature, but it deserves an explicit line in the PR description/changelog since operators will experience it outside kanban admin workflows.

4. hermes_cli/kanban.py:746 (verify the advertised guard) — config docs promise the CLI verbs "still refuse in delegated-child contexts", but no such refusal is visible in the `_cmd_archive_graph`/`_cmd_unarchive` hunks; presumably the guarded-command list at kanban.py:1270 enforces it centrally — please confirm those two verbs actually flow through it (a test asserting the refusal exists would pin it).

5. hermes_cli/kanban_db.py:7620 (mirror drift) — `_task_would_promote` hand-mirrors `recompute_ready`'s promotion predicate (sticky block, failure limit, parent states); when recompute evolves this quietly diverges and dry-run plans lie about promotions — add a property-style test asserting plan.`would_promote` matches actual post-archive `recompute_ready` outcomes, plus a pointer comment binding the two.

No blocking issues found — items 1-2 are the ones I'd want addressed before this ships to real boards.

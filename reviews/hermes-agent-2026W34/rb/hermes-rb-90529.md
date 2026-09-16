> AI code review — automated review for reference; please use your judgment.

Careful, well-attacked hardening: ownership is now proven (path shape *and* checked-out branch) before any removal, ambiguous targets fail closed instead of silently running one task on another task's branch, and the cross-repo anchor trap (a linked checkout living inside an unrelated repo) is resolved through the verified common dir rather than filesystem adjacency. The integration tests — including the genuinely nasty "anchor inside source repo" and "plain dir masquerading as worktree" cases — are exactly right. Items:

- hermes_cli/kanban_db.py:7858 — issue — materializing `.worktrees/<task-id>` *inside* an anchored linked checkout leaves an untracked directory in the anchor's working tree for the task's whole lifetime — why it matters — every `git status`/`_worktree_is_dirty` style check on that anchor (other tasks' guards, `cli._prune_stale_worktrees`, user tooling) now reports it dirty, which can suppress legitimate cleanups or trip dirty-guards far away from this code — suggestion — either teach the dirty/untracked checks to ignore the reserved `.worktrees/` name, or set `--git-dir`-style exclusion via `.git/info/exclude` when materializing under an anchor, and pin it with a test asserting `_worktree_is_dirty(anchor)` stays False while a nested task worktree exists.

- hermes_cli/kanban_db.py:7762 — issue (verification) — several previously-tolerated shapes now raise `RuntimeError`; please confirm every dispatch caller wraps `_resolve_worktree_workspace` so the error becomes a per-task failure/block event rather than killing the dispatch tick — why it matters — fail-closed at the resolver only helps if the failure lands on the task, not the scheduler loop; a test asserting dispatch records the failure for an ambiguous workspace would close the loop.

No blocking issues found — item 2 is a quick trace-and-confirm.

— reviewer-b (automated review)

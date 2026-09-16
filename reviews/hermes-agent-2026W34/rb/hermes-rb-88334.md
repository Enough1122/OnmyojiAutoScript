> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good fix for a silent-degradation class: `worktree_isolation` failing to produce a worktree (unresolvable parent cwd, non-local backend, unborn HEAD) previously dropped to `logger.debug` — invisible in normal operation — while children quietly shared the parent checkout and committed to its branch. Upgrading those paths to actionable warnings with the usual causes spelled out (`--in` doesn't move the process cwd; orphan branches can't branch), plus the configuration.md table documenting all three preconditions and the fallback behavior, makes the feature honest about when it isn't isolating.

Nit (non-blocking): tools/delegate_tool.py:2576 — the new warnings reach operators via logs, but the party that most needs to know it is *not* isolated is the child agent itself (it will commit straight to the parent branch). Consider also appending a one-line system note to the child ("worktree isolation unavailable; you are working in the shared parent checkout") so the model avoids destructive git operations it would otherwise safely run in its own worktree.

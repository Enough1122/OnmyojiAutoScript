> AI code review — automated review for reference; please use your judgment.

Correct diagnosis of a nasty silent-success: a shallow clone's `git fetch origin <branch>` returns rc=0 without crossing the shallow boundary, so reset aligns to a stale tip and the update badge never clears despite "success". `--unshallow` gated on `.git/shallow` presence is the right one-time cure, and both clone shapes are tested. One real gap:

1. hermes_cli/update_cmd.py:_fetch_command (~4212) — `.git/shallow` is checked under `repo_root/.git/`, which only exists for *primary* checkouts. Linked **worktrees** (exactly what kanban workspaces and some install layouts produce) have `.git` as a file pointing at a gitdir elsewhere, so `exists()` is False and a genuinely shallow source stays shallow — the stale-tip bug survives for those installs. Resolve the common dir first (`git rev-parse --git-common-dir`, then test `<common>/shallow`). The tests should gain a linked-worktree fixture.
2. First update on a big shallow clone now pays the full history download inside the updater's timeout window — if `NODE_DEPS_TIMEOUT`-style caps apply to the fetch step, verify the unshallow fetch can't time out mid-history and strand a partial state. Git is atomic per-ref here, so worst case is a failed update + retry, but worth confirming no caller treats non-zero fetch as fatal-with-cleanup that deletes anything.
3. Nice docstring: the failure signature ("badge never clears though updater reported success") is exactly what an operator needs to recognize old instances. (positive)

No blocking issues found beyond item 1's worktree blind spot.

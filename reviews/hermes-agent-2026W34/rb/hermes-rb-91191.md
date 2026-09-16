> AI code review — automated review for reference; please use your judgment.

1. `hermes_cli/projects_cmd.py:~337–339` (`_sync_board_binding`) — when the board slug doesn't exist (or equals DEFAULT_BOARD) the function silently `return`s while the Project side has already recorded the binding — why it matters: `create Widget ... --board widgey` (typo) yields a project claiming a board that has no reciprocal `project_id`, so board-bound task inheritance never engages and nothing tells the user why — suggestion: emit a warning ("board %r not found; binding recorded but tasks won't inherit") before the early returns, or validate the slug at argument-parse time.

2. `hermes_cli/projects_cmd.py:~345–349` — unbind clears `project_id` but deliberately leaves `default_workdir` anchored to the old primary repo (the new test pins this), so tasks created on the now-unbound board still inherit the ex-project's workdir — why it matters: that's a defensible choice (workdir is an operator-set anchor, not ownership), but it will surprise someone whose fresh tasks keep landing in the old repo — suggestion: print a note on unbind ("board keeps default_workdir=%s") or add a `--clear-workdir` flag.

3. `hermes_cli/projects_cmd.py:~349–356` — the whole body is wrapped in `except Exception: pass`, so genuine bugs (wrong kwarg name, schema drift in `write_board_metadata`) vanish without a trace — why it matters: best-effort should mean non-fatal, not invisible; this exact swallowing is how item 1's silent no-op survived — suggestion: downgrade to `logger.debug(..., exc_info=True)`.

4. Nit (`~310–318`): the rebind path reads then conditionally writes board metadata without any lock; concurrent `bind-board` invocations from two processes could interleave the reciprocal updates. Realistically a single-user CLI, but worth one sentence in the docstring stating the sync is last-writer-wins.

Overall: correct bidirectional-sync design — the ownership guard before clearing `project_id` (only clear what this project owns) is exactly right, and the integration tests assert both directions plus preservation of unrelated metadata. Items 1–3 are observability polish on an otherwise solid fix.

— reviewer-a · automated agent review (Hermes week-review)

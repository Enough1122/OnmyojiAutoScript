> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Good fail-closed guard: verifying `skill_dir` is actually gone after a "successful" archive closes the false-ledger-entry hole from #91442, and the two tests cover both the mis-resolved case (patched archive leaves the live dir) and the happy path. Note for maintainers: this hunk sits right where #91464 also edits `_delete_skill`'s archive call, so whichever merges second will need a quick rebase.

Nit (non-blocking): tools/skill_manager_tool.py:1284 — on this fail-closed path, whatever `archive_skill` *did* move (the mis-resolved entry) is left sitting in `.archive` with no acknowledgment or rollback, so collisions can quietly accumulate orphaned archives. Consider embedding the actual archived destination from `archive_msg` in the error text, or best-effort restoring it, so operators can reconcile the collision in one step.

No blocking issues found.

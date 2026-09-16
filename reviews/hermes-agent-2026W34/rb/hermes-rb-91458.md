> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Clean, well-motivated fix: `.git` belongs next to `.curator_backups`/`.hub` in `_EXCLUDE_TOP_LEVEL`, the comment explains the 24GB runaway-growth mechanism clearly, and the new test verifies both inclusion of real skills and exclusion of `.git` inside the produced tarball.

Nit (non-blocking): agent/curator_backup.py:63 — the fix is forward-looking only; snapshots already on disk that contain `.git` keep their bloat and still count against the keep-count pruning budget. Consider a one-time sweep that drops `.git` members from existing snapshots (or at least a doc note telling affected users to delete old snapshots), since users hit by #91449 won't reclaim space until they do.

No blocking issues found.

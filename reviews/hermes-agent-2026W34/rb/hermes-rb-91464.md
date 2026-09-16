> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

The fix correctly addresses the mismatch where `archive_skill(name)` re-resolved the directory by name and could miss/mis-archive when the frontmatter name differs from the directory name; passing the already-resolved `skill_dir` from `_delete_skill` is the right call, and the regression test covers exactly that scenario. The keyword-only `skill_dir` parameter keeps backward compatibility for other callers.

Nit (non-blocking): tools/skill_usage.py:1080 — when an explicit `skill_dir` is supplied, there is no validation that the path still exists (or contains SKILL.md) before moving it; a stale path surfaces only as a generic exception mapped to "failed to archive" upstream. A cheap `.is_dir()` check with a clearer message would make failures easier to diagnose.

No blocking issues found.

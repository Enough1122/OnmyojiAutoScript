> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Both halves are right: an independent gateway explicitly clearing `served_profiles` at startup closes the stale-coverage hole created by `write_runtime_status`'s preserve-omitted-fields semantics (with the write failure correctly tolerated as diagnostic-only), and `_shared_gateway_profile_names` grants liveness to named profiles only from a *validated* live multiplexer record (PID+home checked, entries normalized, `default` excluded), so a dead global record confers nothing — pinned by the stale-PID test alongside served/unserved list outcomes. Findings:

1. Coordination — this PR and open #89773 implement adjacent halves of the same feature on the same function (`_check_gateway_running`): that one adds an inline root-status fallback inside the checker, this one adds a separate `_shared_gateway_profile_names` helper consumed by `list_profiles`. Merging both as-is leaves two code paths answering "is this named profile served by the shared gateway?" with slightly different rules (e.g. `_PROFILE_ID_RE.match(...)` here vs `fullmatch` there). Pick one predicate — ideally this PR's validated helper, reused inside `_check_gateway_running` — before either lands, or the second merge needs a deliberate consolidation commit.

2. gateway/run.py:14936 — the cleanup runs only when `multiplex_profiles` is falsy; a multiplex gateway that *stops serving* a profile while staying up updates its own record presumably elsewhere, so coverage is fine — but worth one comment noting where that shrink happens, since readers of this hunk will look for it.

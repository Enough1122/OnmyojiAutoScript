> AI code review — automated review for reference; please use your judgment.

Review of "fix(state): one literal grammar for session-title lineage resolution and allocation". Centralizing admission in `_numbered_title_variant_value` (ASCII-only digits, exact `base + " #" + N` shape) and making near-misses inert is the right fix; the test matrix (fullwidth digits, `#2x`, deeper chains, wildcard/CJK bases, leading zeros) is thorough. Suggestions:

1. hermes_state.py:8530 (allocation back-compat) — under the old Unicode-`\d` regexes, titles like `foo #２` were legitimate continuations and consumed a lineage number; under the new grammar they become literals, so `get_next_title_in_lineage("foo")` on a DB that already holds `foo #２` will happily allocate `foo #2` — two sessions a user reads as the same slot — consider a one-time normalization/migration pass (or a release-note callout) for existing databases.

2. hermes_state.py:8527 (determinism) — the resolve loop returns the first strict-valid row in cursor order; if the underlying lineage query orders only by `started_at`, sessions created within the same second resolve nondeterministically across runs — add a stable tiebreaker (e.g. rowid) to that query's ORDER BY so "newest wins" is reproducible.

3. hermes_state.py:8482 (hardening) — `_numbered_title_variant_value` accepts arbitrarily long digit strings (`foo #` + 500 nines → int fine, allocation yields an absurd successor) — a modest length cap (say <= 9 digits) keeps `max_num + 1` meaningful and bounds pathological titles.

4. hermes_state.py:8553 (doc clarity) — the strip step uses `rfind(" #")` + strict validation, so `foo #2 #5` passed AS the input base is reinterpreted as a direct child of `foo #2` — consistent with the grammar but easy to misread given the docstring emphasizes it is *not* a child of `foo`; one explicit sentence about parent-chain reinterpretation would prevent future confusion.

5. tests/test_hermes_state.py:1908 (coverage gap) — there is no case resolving a base whose exact session does not exist while valid children do (`resolve_session_by_title("foo")` with only `foo #2` seeded) — that pins the preserved variants-over-exact-absence path through the refactored control flow; cheap to add.

No blocking issues found — items 1 and 2 are worth a follow-up before the grammar change ships to existing installs.

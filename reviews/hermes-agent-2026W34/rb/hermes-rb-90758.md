> AI code review — automated review for reference; please use your judgment.

Review of "fix(state): strip the caller-appended prefix wildcard from CJK queries (#90636)". Correct diagnosis and fix: none of the three CJK routes can honor `*` (bigram/trigram quote tokens before MATCH; LIKE has no `*`), so the appended wildcard turned every UI CJK search into a literal-asterisk hunt. Per-token stripping that preserves boolean operators, keeps non-CJK queries untouched, and refuses to become an empty match-all term is exactly right, and the test set covers both trigram/LIKE routes plus the lone-star edge. Suggestions:

1. tests/test_search_cjk_prefix_wildcard.py:66 (weak assertion) — `assert _hits(db, "秃发* nimby*") or _hits(db, "秃发*")` passes even if the MIXED-query path regresses entirely, because the second disjunct doesn't exercise it — assert each side explicitly (mixed query hits, and separately that the CJK-only part of the mixed query matched) so this test can't silently stop testing what its name says.

2. hermes_state_search.py:1860 (documented trade-off) — because the gate is query-level (`is_cjk`), ANY CJK character disables prefix widening for the query's pure-ASCII tokens too ("秃发* nimby*" searches literal "nimby", not "nimby*"); consistent across all three routes, so correct here — but worth one comment line (and a changelog note) since bilingual users will notice English partial-match quietly stopping working inside mixed queries.

3. hermes_state_search.py:1855 (sibling surfaces) — this normalizes `_search_messages_impl` only; please verify no other entry points receive the caller-appended wildcard (session/title search, any plugin-facing search API) — otherwise the web/desktop box fixes for messages but keeps returning zero rows elsewhere.

4. hermes_state_search.py:1866 (nit) — the `or token` fallback exists so an all-stars token ("**") isn't dropped into an empty term, but the survivor then matches a literal asterisk and returns nothing (pinned by the lone-star test); one comment explaining "keep it literal rather than match-all" would prevent future readers from 'improving' it.

No blocking issues found.

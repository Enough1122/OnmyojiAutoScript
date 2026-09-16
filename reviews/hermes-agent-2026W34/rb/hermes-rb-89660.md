> AI code review — automated review for reference; please use your judgment.

Review of "fix(tools): stop line-based match strategies emitting overlapping spans". Right fix, correctly motivated: #56211 patched only _strategy_exact, and this extends the same non-overlapping whole-match advance to _find_normalized_matches and _strategy_trimmed_boundary — the strategies that actually fire when a model quotes code without leading indentation. The failure mode being prevented (reverse-order splicing against ORIGINAL offsets indexing into shifted text under replace_all=True, silently deleting neighbors) is documented precisely, and the tests cover the 1-match-in-3, 2-matches-in-4, and unaffected-content cases. Suggestions:

1. tools/fuzzy_match.py (audit siblings) — these are two of several match producers; please sweep the remaining strategies (unicode_normalized, any block-anchor fallbacks) for the identical one-line-at-a-time advance — the test file's own "Bug 5" history suggests they've each been fixed piecemeal once already, and a shared non-overlapping window-scan helper would end that series permanently.

2. nit — the behavior change is observable by design (patterns that previously "matched" k overlapping times now replace floor-count non-overlapping occurrences); one line in the changelog noting replace_all semantics under self-overlap would pre-empt user surprise.

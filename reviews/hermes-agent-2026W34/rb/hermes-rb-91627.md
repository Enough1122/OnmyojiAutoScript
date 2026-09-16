> AI code review — automated review for reference; please use your judgment.

Excellent statistical fix: the sign-reversal regression test is exemplary (it even encodes the old wrong number so the failure mode stays documented), pairing by `(task, rep)` is correct for a fully crossed battery, and the `pair` column plus footer note make the denominator change legible instead of mysterious.

- evals/browser_use/report.py:38 — nit — `ok_by_cell[...][_cell_key(r)] = ...` makes duplicate `(task, rep)` rows a silent last-wins overwrite, where the old code averaged every ok row; a duplicated jsonl record now quietly changes which single value counts — suggestion — either count occurrences and warn on collision, or aggregate duplicates deliberately so malformed input can't flip a delta unnoticed.

- evals/browser_use/report.py:47 — nit — `shared` sorting is unnecessary for correctness (means are order-invariant); harmless, but dropping it removes an O(n log n) and one lambda that readers will puzzle over. Alternatively keep it if you plan per-cell output later.

No blocking issues found — the end-to-end `main()` test covering the real index-building path is exactly why this fix can be trusted.

— reviewer-b (automated review)

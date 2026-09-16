> AI code review — automated review for reference; please use your judgment.

Genuinely nice addition: stdlib-only, seeded/reproducible, the paired-delta framing is statistically right for these harnesses, and `test_the_no_effect_arm_is_not_called_a_win` is exactly the tripwire this kind of code needs. Items:

- evals/compaction/report.py:74 — issue — the printed MDD pools the SD of differences from the *best vs worst* arms (`scored[0]` vs `scored[-1]`) but the number is captioned as what "{n} questions could detect" generally; adjacent mid-table pairs usually have different (often smaller) difference spread — why it matters — a reader comparing two close middle policies against an optimistic detectability floor may accept a gap the data can't actually support — suggestion — compute MDD per adjacent pair (you already iterate them) or pool the *maximum* adjacent-pair SD and label it as the conservative bound.

- evals/_stats.py:30 — issue — `stdev` is imported by `report.py` but missing from `__all__` — why it matters — star-imports silently skip it and linters flag the import in report.py as undefined-by-contract; the public/private split should match actual usage — suggestion — add `"stdev"` to `__all__`.

- evals/_stats.py:96 — issue (performance) — the bootstrap resamples with a nested Python loop (`reps × n` `rng.randrange` calls); at the default 10k reps and a future 500-question bank that's 5M interpreter-loop iterations per arm — why it matters — eval runs in CI will feel it, and someone will "fix" it by lowering reps rather than the loop — suggestion — `total = sum(rng.choices(values, k=n))` per rep (same RNG stream semantics change slightly — re-seed is fine since results are reproducible per version) for roughly an order-of-magnitude speedup.

- evals/test_stats.py — issue (coverage) — `compaction/report.py` itself is untested: tie-marking, the mismatched-bank NOTE path, `[n/a]` cells for unscored policies, and the markdown verdict block all render unverified — why it matters — the whole point of the PR is what the report *says*; a formatting regression that drops the TIED markers would pass CI today — suggestion — add a small golden-output test driving `main()` against a synthetic `scorecard.json` (one tied pair, one separated pair, one policy missing `scores`, two banks of different length).

- evals/compaction/report.py:17 — nit — `sys.path.insert` plus importing a generically-named `_stats` invites shadowing if any other `_stats` lands earlier on path; harmless today inside this tree, but a uniquely-named module (`eval_stats.py`) or proper package-relative import would remove the footgun.

No blocking issues found — item 1 is the one that affects how the numbers get read.

— reviewer-b (automated review)

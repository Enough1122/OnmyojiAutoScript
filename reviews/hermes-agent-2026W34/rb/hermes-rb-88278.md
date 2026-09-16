> AI code review — automated review for reference; please use your judgment.

Excellent guard design: discovering valid toolset names from `registry.register(...)` calls instead of freezing a literal means the test can't go stale on renames, the static scan avoids import-order/optional-dependency flakiness with the trade-off stated, and the scan self-test prevents vacuous passing. The docstring's failure-mode explanation (typo ⇒ skill silently hidden for everyone) is exactly what a future maintainer needs. One nit:

- tests/agent/test_skill_toolset_names.py:29 — nit — `_REGISTER_TOOLSET` matches only the keyword form and stops at the first `)`; a registration using a positional toolset argument or nested parens in earlier kwargs would be missed, shrinking the discovered set and *false-failing* valid skill references (fail-loud, so acceptable for CI — worth one comment noting the under-approximation direction).

No blocking issues found.

— reviewer-b (automated review)

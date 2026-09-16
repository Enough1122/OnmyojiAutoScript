> AI code review — automated review for reference; please use your judgment.

Precisely scoped fix, and the test pair is exactly right: one pinning the false-positive elimination (`ecoSYSTEM`, `misystemo`) and one protecting the underscore-directive recall that a naive `\b` would have silently broken (since `_` is a word character) — the comment explaining that trap is the kind that prevents regressions for years.

— reviewer-b (automated review)

No blocking issues found.

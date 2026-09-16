> AI code review — automated review for reference; please use your judgment.

Correct one-liner: the filter predicate now resolves unprojected sessions to the same `NO_PROJECT_ID` sentinel the grouping lane uses, so selecting the "no project" bucket keeps those rows visible instead of filtering them out — and the comment notes it reuses the exact membership function, so the two can't drift.

— reviewer-b (automated review)

No blocking issues found.

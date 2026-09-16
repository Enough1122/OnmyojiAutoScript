> AI code review — automated review for reference; please use your judgment.

Supplement to the earlier review of "fix: fix(run_agent): acquire lock in IterationBudget.used property" (posted concurrently from a parallel review pass — apologies for any duplication):

1. run_agent.py (sibling gap) — the `remaining` property still reads `_used` WITHOUT acquiring the budget lock; it has exactly the same race shape this PR fixes for `used` (and derives from the same field), so acquire the lock there too or compute both inside one locked helper — otherwise the next race report is one property away.

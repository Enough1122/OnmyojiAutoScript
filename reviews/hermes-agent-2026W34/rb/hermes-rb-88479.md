> AI code review — automated review for reference; please use your judgment.

This is an **exact duplicate** of #88480 — identical diff (lock acquisition in the `used` property) and identical test file. The fix itself is correct: `used` was the one unguarded accessor on a lock-protected counter, and the stress test pins the race. Items:

- PR hygiene — issue — two open PRs for the same patch will both show green independently and whoever merges second gets a no-op conflict — suggestion — close one of these (keeping whichever has the cleaner title — neither should ship as `fix: fix(run_agent): …`) and reference it from the other.

No blocking issues found on the code itself.

— reviewer-b (automated review)

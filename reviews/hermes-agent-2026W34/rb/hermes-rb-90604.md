> AI code review — automated review; please use your judgment.

Correct one-line fix: cron jobs aren't members of any worktree group, so gating the section on `!worktreeGroupingActive` made them vanish exactly when users grouped by project; dropping only that condition keeps search-time suppression (`!trimmedQuery`) intact while making the always-relevant jobs visible in every grouping mode.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)

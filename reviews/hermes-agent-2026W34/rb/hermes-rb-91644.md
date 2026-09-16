> AI code review — automated review for reference; please use your judgment.

One-line curated-picker addition, correctly formatted and aligned with its neighbors. Nothing to flag beyond one nit:

- hermes_cli/models.py:139 — nit — unlike some sibling entries there's no corresponding `usage_pricing` entry; if free models aren't short-circuited by their `:free` suffix downstream, cost reporting for this ID will show "unknown" instead of $0 — worth confirming (or adding a zero-cost `PricingEntry`) in a follow-up.

No blocking issues found.

— reviewer-b (automated review)

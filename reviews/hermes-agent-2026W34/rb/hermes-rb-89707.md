> AI code review — automated review for reference; please use your judgment.

Correct aggregation fix with the two assertions that matter: one card per (model, provider) pair even across multiple aux tasks, and per-model session sums staying reconcilable with `totals.total_sessions` after the fold — while the #23270 aux-only visibility case is explicitly regression-guarded. The avg-tokens recomputation and last-used max-merge show the fold was thought through beyond just deduping keys. One nit:

- hermes_cli/web_server.py:15433 — nit — when aux rows fold into a sessions-derived pair, their `aux_task` labels are dropped entirely (the field stays whatever the main row had); if operators use that column to see *which* aux work consumed tokens, folding vision+compression+titles into one row loses that attribution — consider an aggregated label (`"vision,compression,…"`, capped) or dropping the column from folded rows deliberately.

No blocking issues found.

— reviewer-b (automated review)

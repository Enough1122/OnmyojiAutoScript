> AI code review — automated review for reference; please use your judgment.

Thoughtful dedup: exact-normalized matching keeps it conservative, the all-duplicates fallback avoids inventing a promote-root-with-no-children path, and the dependent-on-a-duplicate case is correctly refused rather than losing or misredirecting a dependency edge — the comment explaining the schema limitation is exactly why this decision will survive review later. Index remapping after removal and the best-effort link-with-logged-failure are both right. One nit:

- hermes_cli/kanban_decompose.py:447 — nit — `existing_by_title` silently keeps the *last* card when several open cards share one normalized title; picking the oldest (first) or logging the collision would make the rare triple-title case deterministic and visible.

No blocking issues found.

— reviewer-b (automated review)

> AI code review — automated review for reference; please use your judgment.

Clean helper extraction with tests covering the merge/dedupe and toggle semantics. One nit:

- apps/desktop/src/plugins/kanban/new-task-form.ts:47 — nit — `Number(input.priority) || 0` lets fractional input through (`"2.5"` → 2.5); if the API expects an integer, `Math.trunc` or a round-trip through `parseInt` would match the server contract exactly.

No blocking issues found.

— reviewer-b (automated review)

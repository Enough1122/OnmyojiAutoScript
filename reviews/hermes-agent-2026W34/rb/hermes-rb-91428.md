> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Well-engineered: routing deletion through the existing `removeSession` action instead of adding a parallel REST path keeps confirmation, tombstoning, runtime-close, and unread-watermark handling in one place; the explicit-profile parameter solves the real problem that cron run rows live outside `$sessions`; the rollback path evicts *and* restores the cron-store entry correctly (with a duplicate guard); and both the component and the hook got genuine tests covering success, RPC-failure rollback, and profile passthrough. Findings:

1. apps/desktop/src/app/cron/cron-run-row.tsx:78 — accessibility: in the sidebar variant the clickable row's accessible name is only the time string ("Aug 21, 10:00"), same as before, but the row now also carries a destructive action menu keyed off that name. Add an `aria-label` combining title + time (`aria-label={`${title} — ${time}`}`) so screen-reader users can tell rows apart and understand what they're deleting.

2. apps/desktop/src/app/chat/sidebar/index.tsx:300 — the `onDeleteSession` prop type has grown into `boolean | Promise<boolean | void> | void`, and callers now interpret it three different ways (`!== false`, awaited wrapper that discards, raw pass-through). Consider converging the prop on `Promise<boolean>` in a follow-up so success/failure isn't inferred by each consumer; today's `(await ...) !== false` silently treats a swallowed exception as success.

No blocking issues found.

> AI code review — automated review for reference; please use your judgment.

1. apps/desktop/src/store/composer-queue.ts:210 — reorderQueuedPrompts validates only cardinality (next.length !== queue.length), so a list with a DUPLICATED id passes ([a, a, b] against queue [a, b, c] maps to length 3) and silently drops entry c while duplicating a. Why it matters: reorderQueuedPrompts is a public store API — today dnd-kit always supplies a clean permutation, but any future caller (undo stack, sync merge, a test helper) that hands it a malformed list corrupts durable queue state without error. Suggestion: also require new Set(ids).size === queue.length before writing.

2. Nit: package-lock.json carries ~30 unrelated peer-flag removals from a registry metadata refresh. Keep dependency-file churn out of feature PRs so bisection and review diffs stay meaningful.

Good shape otherwise: the store-level API fails closed and is unit-tested for both the happy permutation and the drop/extra-id rejections, StatusRow gained style/ref passthrough instead of leaking dnd-kit internals into it, the drag handle gets proper i18n labels in all five locales plus the Translations interface update, and dnd-kit's default keyboard sensor keeps reordering reachable without a pointer.

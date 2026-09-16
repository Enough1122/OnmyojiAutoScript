> AI code review — automated review for reference; please use your judgment.

Correct and minimal: an orphan error row that isn't the live tail has by definition been superseded by a newer user turn, so dropping it during reconciliation is exactly right, and excluding `hidden` user turns from the superseding check correctly keeps internal/plumbing turns from erasing a failure the user never got past. The chained-failure edge works out properly too (each earlier orphan drops, only the newest survives). Nits:

1. apps/desktop/src/lib/chat-messages/reconciliation.ts:~166 — the supersession scan is O(errors × tail-length); fine at chat scale, but if this runs per hydration over long threads consider walking once from the end recording "lastVisibleUserIndex" and comparing indices instead of slicing per row. Not worth it today. (nit)
2. tests — the new case covers drop-when-superseded and existing cases cover keep-at-tail; one gap: **later user turn whose reply ALSO failed** (two stacked orphans) to pin that exactly one error survives — the most confusing real-world variant of this bug. (nit)
3. A one-line comment on why `!candidate.hidden` matters (plumbing turns must not count as user follow-ups) would save the next reader an archaeology trip into the hidden-turn semantics. (nit)

No blocking issues found.

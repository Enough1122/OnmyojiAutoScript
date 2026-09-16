> AI code review — automated review for reference; please use your judgment.

1. apps/desktop/src/store/session-states.ts:394 — restorePinnedSessionStates hand-builds a full 20-field ClientSessionState literal. Why it matters: when the real event-driven path grows a field with a non-empty default (a new flag defaulting true, a sentinel string), this placeholder silently diverges from what live sessions look like, producing pinned-only UI quirks that are miserable to trace. Suggestion: export a makeEmptySessionState(storedSessionId) factory from this module and use it in BOTH the placeholder path and wherever live states are initialized, so defaults have one home.

2. No tests accompany the function despite being ideal unit-test material: pinned-without-state creates one; existing state / stored-id match / lineage-root match each skip; unpinned rows are ignored; and an empty entries set must not touch the store at all (the current code correctly avoids the set call — pin it before someone 'simplifies' it into a spurious re-render).

The skip logic is thoughtfully layered \u2014 checking runtime-id states, direct stored-id matches, AND lineage-root aliases prevents the placeholder from clobbering a live rotation sibling \u2014 and gating on $pinnedSessionIds keeps the repair scoped to exactly the sessions whose blank chat users would actually click.

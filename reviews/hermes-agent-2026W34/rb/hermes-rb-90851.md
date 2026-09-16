> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Right call on both halves: scaffolding that only existed to drive the retry (partial-fragment assistant rows and the `[System: ...]` continuation nudge) must not survive into the durable transcript where it renders as phantom user bubbles and steers replay, and stitching the recovered answer onto the single final assistant row gives replay consumers one clean turn. Scoping the purge to `current_turn_user_idx + 1` correctly mirrors the ceiling-exit path, and both new tests pin the important behaviors including the crash-reloaded prior-turn marks surviving. Findings:

1. agent/conversation_loop.py:8057 — the fallback direction of the turn anchor is fail-open: if `current_turn_user_idx` is somehow missing/non-int/negative, `_turn_start = 0` scans the **entire** transcript and deletes every marked row — precisely the "a mark reloaded from a PRIOR turn's message must never be deleted" outcome the comment above it forbids. The safe default is the opposite: when the anchor isn't trustworthy, log and skip the row-deletion (keep only the old pop-markers behavior), since leaving two cosmetic fragment rows beats destroying real prior history on an invariant violation.

2. agent/conversation_loop.py:8068 — `agent._session_messages = messages` assumes the agent's durable session list is this same list object (alias) rather than a snapshot copy; if any code path assigned a copy earlier in the turn, this rebinding silently swaps identity mid-loop. If aliasing is guaranteed by construction, a one-line comment saying so would prevent future refactors from breaking persistence quietly; otherwise reconcile by mutating in place.

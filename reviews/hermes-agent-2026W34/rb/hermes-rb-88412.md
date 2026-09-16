> AI code review — automated review for reference; please use your judgment.

Correctly scoped dedup: restricting to *adjacent* same-role+text plain rows (kind undefined both sides) catches exactly the snapshot+tail-replay race while leaving trail/tool-shelf merging and non-adjacent genuine repeats intact — all four behaviors are tested. The docstring citing #59634/#59673 as the assistant-side ancestors of this pairwise variant is good lineage. Points:

1. ui-tui/src/lib/messages.ts:~14 — the "a user cannot legitimately submit the same text twice in a row" justification holds only while the busy-gate is airtight. An interrupted/cancelled turn frees the composer without an assistant reply landing between two identical submissions — that real sequence now silently drops the second message. Consider tagging replay-origin events (the re-activate path knows it's replaying) and deduping on that flag instead of text equality, so live submits always append. At minimum document the accepted false-positive.
2. `prev.at(-1)` + field comparison runs before `appendToolShelfMessage`; if a future kind gains its own repeat semantics, the `kind === undefined` guard already excludes it — good forward shape. (positive)
3. nit: the four new tests duplicate fixture shapes; a tiny `row(role, text)` builder would tighten them. Very minor.

No blocking issues found beyond item 1's accepted tradeoff.

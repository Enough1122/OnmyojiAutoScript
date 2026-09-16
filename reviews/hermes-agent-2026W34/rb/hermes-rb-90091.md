> AI code review — automated review; please use your judgment.

Precise fix for a false-refusal class: when a **bound integer** `row_id` is in hand it's the authoritative address, so dropping the renderer-visible user ordinal and synthetic message-id eliminates the 4030 cross-check mismatch (observed 75 vs 102 divergence) without weakening safety — an unknown/dead row_id still fails closed with 4018, the `Number.isInteger` guard keeps malformed values on the old reconciling path, message-id-only addressing is untouched, and `confirm_empty_truncate` survives for ordinal-0 restores. All three behaviors have tests, and the previously pinned expectation was flipped *with* its rationale documented inline citing the gateway's own reconciliation comment.

No blocking issues found.

— reviewer-a · automated agent review (Hermes week-review)

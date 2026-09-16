> AI code review — automated review; please use your judgment.

Correct and well-targeted repair pass: enforcing *causal adjacency* (results must immediately follow their own batch, matched per-batch rather than by global id sets) closes a real gap where compression could reorder a result ahead of its synthetic call, satisfy the old set-checks, then get deleted by the outstanding-call deduper — leaving strict providers to reject the entire request. The implementation is clean: single O(n) wire-order walk, `id`/`call_id` alias handling, bounded placeholder stubs synthesized per unanswered call before the next non-tool message, persisted history untouched (API copy only), and both the reordered-result case and a 7-call partial batch are tested down to exact stub counts and sequence shape.

No blocking issues found.

Nit (`agent/agent_runtime_helpers.py` stub content): ````"[Result unavailable — see context summary above]"```` presumes a compaction summary actually precedes the stub; on recovery-glitch paths with no summary above, the pointer is slightly misleading — consider the neutral `"[Result unavailable]"` or conditionally appending the summary clause only when a compaction marker exists in the transcript.

— reviewer-a · automated agent review (Hermes week-review)

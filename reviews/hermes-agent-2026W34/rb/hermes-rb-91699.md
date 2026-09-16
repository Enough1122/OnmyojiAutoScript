> AI code review — automated review for reference; please use your judgment.

The fix lands in the right place (marker appended *last*, so more specific size messages keep precedence) and the test pins both the routing decision and `retryable`. The self-limiting design noted in the comment — shrink returns `False` when no image part exists, surfacing the original error unchanged — means the broad match costs at most one wasted downscale attempt rather than a wrong-outcome loop, which is the right risk profile for a heuristic classifier.

No blocking issues found.

Nit: ````"failed to read request body"```` is generic enough to fire on non-image malformed-body 400s from any provider; since the classifier already receives `provider`, consider gating this marker to providers known to emit it (`ollama-cloud` and friends) or matching it only when the conversation actually contains image parts — either keeps unrelated providers' genuine bad-request errors classified honestly while preserving the shrink-on-reject path where it matters.

— reviewer-a · automated agent review (Hermes week-review)

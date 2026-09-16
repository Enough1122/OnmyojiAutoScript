> AI code review — automated review for reference; please use your judgment.

Excellent feature design: `session_key` cleanly separates conversation identity from delivery identity, per-delivery `deliver_extra` storage means an overlapping second POST cannot redirect an in-flight turn's response target (proven by the two-event interleaving test with exact `send` args), the busy-input path deliberately FIFOs persistent deliveries instead of interrupting/merging, fallback one-shot deliveries keep their own lifecycle including session-close, profile multiplexing namespaces automatically, and the docs' behavior-notes section (idempotency unchanged, sender-controlled keys scoped to route+HMAC, ordering-vs-concurrency guidance) is genuinely thorough.

1. `gateway/platforms/webhook.py` (`send` resolution chain, ~380–386) — for persistent turns the chain is ContextVar delivery-id → `reply_to` → `chat_id`, but `chat_id` is now ````webhook:<route>:session:<key>```` which is **never a key in `_delivery_info`** — why it matters: any `send()` that runs outside the ContextVar's async context and without `reply_to` (e.g., an interim status emitted from a different task, or after context teardown) finds nothing and silently downgrades to `deliver="log"` — suggestion: enumerate the gateway's send paths for webhook sessions and add a test where the final response fires from a fresh task; alternatively fall back to scanning `_delivery_info_order` for this session's most recent entry.

2. `~928–931` — unresolved-template detection is ````"{" in session_key````; a *successfully rendered* key whose value legitimately contains `{` also degrades to one-shot — safe direction, but worth documenting next to the fallback bullet since it's non-obvious.

3. Nit (`:~1003–1005`): `_active_delivery_id.set(...)` is never reset in `on_processing_complete`; task contexts are usually discarded, but a pooled/reused task would carry a stale delivery id into an unrelated turn — consider resetting with the ContextVar token in a `finally`.

— reviewer-a · automated agent review (Hermes week-review)

> AI code review — automated review for reference; please use your judgment.

1. `hermes_cli/proxy/sse_done.py:~95–113` (`_consume_line`) — a spec-legal **multi-line `data:` field** (one JSON event split across consecutive `data:` lines, allowed by the SSE spec) parses as two malformed fragments and permanently disables synthesis for that response — why it matters: the failure mode is silent (client keeps seeing a "truncated" stream), and the tracker's own docstring claims general correctness — suggestion: either join continuation `data:` lines before parsing (accumulate until an empty line, per SSE dispatch semantics) or explicitly document the OpenAI-dialect-only assumption next to `saw_malformed_event`.

2. `hermes_cli/proxy/server.py:~247–250` — the `[DONE]` append sits inside the same `try` whose handler catches `(aiohttp.ClientError, asyncio.CancelledError)`; a client that disconnects right at EOF commonly surfaces as plain `ConnectionResetError`/`OSError`, which that tuple misses — why it matters: the new write adds one more place where a routine client hangup can escape as unhandled task noise — suggestion: wrap the append (or widen the except) so post-stream cleanup failures stay at debug level like the rest of this path.

3. `agent/chat_completion_helpers.py:~4126–4133` — `lastOne` detection requires exactly `is True` (attribute or `model_extra`); a provider sending `"lastOne": 1` would be missed and the stream still misread as dropped — why it matters: this half of the fix targets third-party quirks, and integer-truthy sentinels are precisely the kind of quirk that appears across relabelled upstreams — suggestion: normalize once (`last_one in (True, 1, "true")`) or keep strict but note the assumption where the Portal shape is documented.

4. Nit (`sse_done.py:~60–66`): `should_append_done()` mutating state (flushing `_buf`) makes it non-idempotent under repeated calls; fine for the single call site, but naming it `finalize_and_check()` or splitting the flush into `feed_eof()` would prevent surprises in tests/future callers.

Overall: genuinely careful treatment of a real interoperability wart — byte-exact pass-through, split-chunk-safe scanning, error-shaped finish-reason exclusion, and an unusually complete test matrix including TCP-split frames. Items 1–2 are edge hardening; nothing blocking.

— reviewer-a · automated agent review (Hermes week-review)

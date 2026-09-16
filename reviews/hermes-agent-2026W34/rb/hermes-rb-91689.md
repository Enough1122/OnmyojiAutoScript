> AI code review — automated review for reference; please use your judgment.

1. `tools/mcp_tool.py:~620–626` (`response_hook`) — detection works by **reassigning `response.aclose`** on the live httpx response object; nothing asserts the patch took (`httpx` could grow `__slots__`, or a future SDK/httpx version could close through an internal handle instead of calling `aclose`) — why it matters: silent patch failure degrades to today's behavior (undetected half-dead sessions), i.e. the bug returns invisibly — suggestion: verify the assignment stuck (`if getattr(response, "aclose", None) is original_close: logger.debug(...)` warn otherwise) and add a pinned-version regression note/test so an upgrade that breaks the seam fails loudly.

2. `tools/mcp_tool.py:~600–640` — the state machine only observes *graceful* `aclose` paths; an abrupt stream death (TCP reset mid-SSE) never invokes `aclose`, so it relies entirely on the separate ExceptionGroup/reconnect handling — why it matters: worth writing down, because someone debugging "why didn't the tracker fire?" will otherwise assume it covers all stream loss — suggestion: one boundary comment above the class listing covered vs out-of-scope failure modes.

3. Test gap (`tests/tools/test_mcp_http_notification_stream.py`): no case for `aclose()` being invoked twice on one response (the `_closed_generation` guard) nor for a close arriving *after* a replacement generation bump (the `generation != self._generation` branch) — why it matters: those two guards are the subtlest code in the class and are currently untested — suggestion: two small unit cases locking them in.

4. Nit (`~3648`): `notification_reconnect_grace = max(5.0, float(connect_timeout))` silently converts a configured 0/negative connect timeout into the 5s floor — fine, but a debug log of the effective grace value would help field diagnosis when tuning reconnect behavior.

Overall: sharp diagnosis of a genuinely nasty failure mode (POST pings healthy while the notification channel is dead) and a clean escalation design — SDK gets its cheap reconnect window, then Hermes rebuilds the whole transport with a visible state transition. Items 1–3 harden the seams; none block.

— reviewer-a · automated agent review (Hermes week-review)

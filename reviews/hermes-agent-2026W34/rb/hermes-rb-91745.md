> AI code review — automated review for reference; please use your judgment.

1. `acp_adapter/server.py:~1893` (`close_session`) — `asyncio.to_thread(state.idle_event.wait)` wrapped in `asyncio.wait_for(..., 30)`: on timeout the await is cancelled but the executor thread keeps blocking in `Event.wait()` with no timeout — why it matters: every timed-out close pins one thread-pool thread indefinitely, and repeated close attempts (the retry story this PR builds) stack blocked threads — suggestion: call `state.idle_event.wait(_CLOSE_SESSION_TIMEOUT_SECONDS)` inside the thread and derive the timeout outcome from its bool result, dropping the outer `wait_for`.

2. `acp_adapter/server.py:~1880` — `close_session` does `state.queued_prompts.clear()` but nothing visible resolves the callers whose prompts were queued — why it matters: if queued prompt coroutines wait on turn completion to emit their responses, clearing strands them and the client hangs exactly when it asked for an orderly close — suggestion: drain the queue into a rejection path that sends each waiter a terminal `PromptResponse(stop_reason="cancelled")` (and add a regression test for a queued prompt racing a close).

3. `acp_adapter/server.py:~2028` (`prompt`) — a missing session still returns `PromptResponse(stop_reason="refusal")` while every other lifecycle method now raises `-32002` — why it matters: clients can't distinguish "session gone" from a genuine model refusal, undercutting the wire-contract alignment this PR ships — suggestion: raise `_session_not_found(session_id)` here too (the two `closing` checks immediately below already do).

4. `acp_adapter/server.py:~1852–1866` — `resume_session` silently drops the previous replay-on-resume behavior (tests flipped from "replays" to "does not replay") — why it matters: existing clients that resumed and expected the transcript inline will render empty sessions after upgrade; this is a behavioral breaking change dressed as a fix — suggestion: call it out in the changelog/user docs explicitly, and/or honor a client capability hint so replay-capable clients keep today's behavior.

5. `acp_adapter/server.py:~1143–1300` (`_register_session_mcp_servers`) — the compensating-transaction logic (~120 lines, three near-duplicate rollback blocks, mutable sets shared between success/failure paths) is correct as far as I can trace, but it is at the edge of reviewability — why it matters: the next editor will almost certainly desynchronize one of the duplicated refcount-adjustment loops — suggestion: extract a single `_apply_ownership_delta()` helper used by both commit and rollback, and add a stress test interleaving `new_session`/`load_session`/`close_session` on a shared server name.

6. `tools/mcp_tool.py:~7262` — `_run_on_mcp_loop(..., timeout=15)` hardcodes the shutdown window while `close_session` allows 30s for turns; a well-behaved but slow server (>15s shutdown) permanently fails `close_session` with "MCP resource release failed" even though nothing is wrong — why it matters: the session becomes unclosable in practice despite the retryable design — suggestion: bump the release timeout toward the close budget (or make it configurable) and include the failing server name in the surfaced error data.

Nit: the `HERMES_ACP_SKIP_CONFIGURED_MCP` escape hatch (`~1159`) has no test and isn't mentioned in either doc file — worth a line in `acp-internals.md`.

Overall: strong PR — capability advertisement, typed wire errors, refcounted MCP ownership with genuinely tricky rollback handling, and unusually good race-conscious tests. Items 1–3 are the ones I'd want addressed before merge.

— reviewer-a · automated agent review (Hermes week-review)

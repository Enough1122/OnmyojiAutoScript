> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Excellent root-cause documentation and fix: pre-accept `ws.close(44xx)` is answered by uvicorn with a bare HTTP 403, so every app-level rejection code was invisible in production while Starlette's TestClient masked it — and the new test file states exactly that testing trap and adds a **real-uvicorn** fail-before test. `_ws_reject` (accept → close with code/reason) is applied consistently across console/pty/pub/events/speak_stream plus the kanban dashboard plugin, with peer-gone errors swallowed by design. The deliberate exception at `gateway_ws` is well-reasoned and self-documenting: its client resolves connect() on `open`, so post-accept rejection would let boot complete on a dead socket — the comment correctly ties flipping it to a client-side change. The updated tests now also assert close *reasons*, which the old ones couldn't.

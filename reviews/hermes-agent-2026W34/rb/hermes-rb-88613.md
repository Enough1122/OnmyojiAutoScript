> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Same correct root cause as #88607/`_ws_reject`: pre-accept `ws.close(44xx)` never reaches the peer (uvicorn answers the upgrade with bare HTTP 403), so every 44xx-keyed dashboard path died behind a `1006`. Accept-then-close fixes it, applied consistently across console/pty/pub/events/speak_stream, the TestClient-masking trap is explicitly documented, and the new **real-uvicorn** test (real `websockets` client against a live server, including a proxy=None note for macOS scutil environments) is exactly the fail-before this class needs. Findings:

1. Coordination — open PR **#88619** implements the same `_ws_reject` fix on the same file. They differ in one important decision: #88619 *deliberately leaves* `gateway_ws` close-before-accept, documenting that `JsonRpcGatewayClient.connect()` resolves on `open`, so post-accept rejection would let the desktop boot path treat an already-closed socket as usable; this PR converts `gateway_ws` unconditionally. Please reconcile: either merge one into the other, or confirm the desktop client has been changed to settle connect() on the first frame (`gateway.ready`) before shipping the `gateway_ws` conversion — otherwise auth-rejected gateway sockets complete boot and then die.

2. Nit: unlike #88619, this variant doesn't cover the kanban dashboard plugin's `stream_events` rejection, which has the identical pre-accept bug — include it in whichever PR survives.

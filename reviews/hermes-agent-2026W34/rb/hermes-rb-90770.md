> AI code review — automated review for reference; please use your judgment.

Review of "fix(buzz): resume watched channels from a durable cursor across restarts (#90464)". Correctly closes the downtime black hole: restoring a saved cursor instead of reseeding means events that landed while the gateway was down still dispatch, and the design guards are all present — identity+relay binding against cross-bot cursor contamination, atomic never-raising writes, graceful degrade to seeding on any parse failure, seen-cap bounding that keeps the NEWEST ids, and a change-detector so idle channels don't rewrite the file. The test matrix is excellent (restart resume asserts both the skipped CLI call and the delivered mention; corrupt-file fallback; cap bounds; idle-poll mtime pinning). Suggestions:

1. plugins/platforms/buzz/adapter.py:894 (WS-path write amplification) — the WebSocket loop calls `_save_cursors()` after EVERY cursor-changing event, serializing the whole multi-channel state file per message on a busy relay, while the poll path sensibly batches per sweep — consider a dirty-flag + flush at most once per second (or per loop iteration batch); the at-least-once guarantee survives either way since dispatch precedes persistence.

2. plugins/platforms/buzz/adapter.py:893 (pin the delivery semantics) — dispatch happens BEFORE the cursor save, which makes crash-recovery at-least-once (a crash between dispatch and save re-delivers one event, deduped by `seen` when possible) — that's the right choice for chat, but it's exactly the kind of invariant a future refactor inverts; add a one-line comment stating "dispatch first, then persist: crash = possible duplicate, never a lost message".

3. plugins/platforms/buzz/adapter.py:957 (nit, relay matching) — the identity/relay guard compares the raw relay string, so `https://relay/` vs `https://relay` silently invalidates every saved cursor; normalizing (strip trailing slash, lowercase host) would make the binding robust without weakening it.

4. tests/gateway/test_buzz_adapter.py:541 (coverage gap) — the poll path's save-on-change is exercised via mtime, but the WebSocket branch's identical logic isn't; one test driving `_websocket_loop`'s message branch (or extracting its save decision into a helper) would keep the two paths from drifting.

No blocking issues found.

> AI code review — automated review for reference; please use your judgment.

This is the right architecture for PTY resume: absolute byte-offset cursors over a monotonic `total_appended` counter (immune to ring eviction misreporting via explicit `offset_rolled_out` resets), a per-session epoch that invalidates cursors across process incarnations, a single `_send_lock` making append→send and cut-over→replay mutually ordered so live output can never straddle a replay, strict server-side cursor parsing (canonical decimals, JS-safe-integer bound, paired epoch+offset, attach-token requirement), a stale-socket frame guard on the client (`wsRef.current !== ws`) so replaced sockets can't repaint or advance the new cursor, and delegate-subagent sessions excluded from continuation chains with tests covering literal-marker and nested-key traps plus the connectionless fallback path. The multibyte-boundary test (cursor advancing on a raw `0xc3` half of `é`) is exactly the detail most implementations get wrong. Items:

- hermes_cli/web_server.py:17040 — issue — `_parse_pty_replay_cursor` failures call `ws.close(4400)` *before* `ws.accept()`; under ASGI/Starlette a close-before-accept downgrades to an HTTP-level rejection, so the client never sees close code 4400 or your reason text — why it matters — the browser can't distinguish "invalid cursor" from any other handshake failure, degrading the very diagnostics this validation adds — suggestion — accept first, then close with the code (the standard pattern for post-handshake policy rejections), or keep pre-accept and adjust the comment to say clients will observe a generic handshake failure.

- hermes_cli/web_server.py:11921 — nit — the SQLite branch prunes delegates inside the CTE while the Python fallback filters the full 10k row list afterwards; equivalent today, but the fallback's O(n·parse) grows with session count — fine at current scale, worth a comment if `list_sessions_rich` callers grow.

No blocking issues found — item 1 only affects how legible the rejection is.

— reviewer-b (automated review)

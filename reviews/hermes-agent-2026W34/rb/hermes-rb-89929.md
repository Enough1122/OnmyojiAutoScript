> AI code review — automated review for reference; please use your judgment.

Reviewed the diff. Well-reasoned workaround with an honest docstring: black-holed IPs in msg-frontier's pool hang TLS handshakes with no RST, so one \`open_timeout\` over a sequential pool was doomed whenever a bad address sorted first. Per-IP deadlines via \`asyncio.wait_for\`, deduped resolved addresses, and first-handshake-wins is the right minimal shape, and the test's fake-module harness genuinely exercises attempt ordering through the patched \`websockets.connect\`.

Two points:

- **plugins/platforms/feishu/adapter.py:~1367 — \`_socket.getaddrinfo\` runs synchronously on the event loop.** DNS resolution is blocking; on the dedicated WS thread's fresh loop the blast radius is limited, but with a slow/broken resolver it can stall the loop for seconds and delay ping scheduling. Use \`await loop.getaddrinfo(...)\` (or \`run_in_executor\`) so resolution yields like every other await here.

- **The IP-override path leans on \`websockets.connect(host=ip, port=…)\` preserving SNI and certificate validation against the original hostname.** That is the documented behavior of the library's host/port overrides, but it's load-bearing for TLS security here — worth a comment naming the assumption (and the library version it was verified on), so a future websockets upgrade that changes override semantics gets caught rather than silently connecting with mismatched identity checks.

Nit: worst case is now sequential (N IPs × 4s) versus the old single budget; fine given ~12 IPs and typically ≤3 bad ones, but the docstring could note the bounded worst case as an accepted trade until RFC 8305 lands natively.

No blocking issues found.
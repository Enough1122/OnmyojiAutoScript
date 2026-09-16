> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Correct fix for the quick-reconnect staleness gap: delegating the already-registered case to `_refresh_tools()` means schema/description changes are picked up and removed tools are deregistered instead of lingering until a parked reconnect or manual `/reload-mcp`, and the test suite is unusually thorough — changed schema, changed description, identical contract staying single-entry, added/removed tools, include/exclude filters not producing phantoms, cross-server namespacing, plus regression coverage that the notification-driven `_refresh_tools` path still works. Findings are minor:

1. tools/mcp_tool.py:3655 — every quick reconnect now costs **two** `tools/list` round trips: `_discover_tools` fetches the list into `self._tools`, then `_refresh_tools()` immediately fetches it again itself. For chatty flapping servers this doubles discovery traffic during exactly the unstable window. Consider letting `_refresh_tools` accept the freshly discovered list (or short-circuiting when name+schema+description digests match), keeping correctness at half the chatter.

2. tools/mcp_tool.py:3647 — the function flipped sync→async; please double-check every caller now awaits it *and* none invoked it while holding a non-asyncio lock (e.g. inside a `with self._lock:` block elsewhere), since an await under a threading lock would serialize unrelated reconnects. The two shown call sites look fine, but the grep-audit is cheap insurance for a 4k-line module.

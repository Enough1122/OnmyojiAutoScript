> AI code review — automated review for reference; please use your judgment.

The failure mode is real and the fix targets it precisely: single-session hosts (Slack MCP) evict the live session when a health probe opens a second Streamable HTTP connection, so reusing the process-owned session — or refusing to second-connect while one is claimed — is correct. The claim-grace window for the gateway-open race and the two tests (live reuse without any connect; parked server raises rather than second-connects) pin both halves. Points:

1. hermes_cli/mcp_config.py:_wait_for_live_mcp_tools (~310) — the poll loop uses blocking `time.sleep(0.1)` with a deadline of up to `connect_timeout` (default 30s). If `_probe_single_server` is ever invoked on the event-loop thread rather than a worker thread, this freezes the whole gateway for that duration. The code checks `loop.is_running()` only in the later grace branch — please assert/document that all entry paths run in threads, or make the wait loop async-aware.
2. Same file — reaching into `tools.mcp_tool`'s `_lock`/`_servers`/`_server_connecting` privates couples two modules at their internals; a rename in mcp_tool breaks this silently at import (AttributeError inside try? No — import would fail loudly, fine) but more importantly future changes to those structures' shapes (e.g., `_servers` values gaining wrappers) break the duck-typed `.session`/`._tools` reads quietly. Expose `mcp_tool.get_live_session_snapshot(name)` instead.
3. Contract change worth documenting for other callers: `_probe_single_server` can now raise `TimeoutError` where it previously always connected. Grep for call sites beyond the health sweep/tests and confirm each handles it (the desktop presumably paints red — intended).
4. The URL-only scoping of the grace path is right — stdio servers can't be second-connected the same way. (positive)
5. `_truncate_mcp_tool_desc` dedupes the inline truncation nicely. (nit)

No blocking issues found.

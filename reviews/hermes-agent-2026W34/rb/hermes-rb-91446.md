> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Both halves are individually well-built — the tail-truncating continuity limit keeps "most recent report" visible with solid tests pinning the boundary, and the MCP `_meta` identity work snapshots ContextVars on the right thread, validates/reserves the meta key sensibly, and ships thorough tests plus docs. Findings:

1. tools/mcp_tool.py:1603 — privacy, default-on with no opt-out: once any messaging-gateway session is bound, the user's Telegram/Discord user id is attached as `params._meta` to *every* tools/call to *every* configured MCP server, including third-party remote ones. There is no config to turn the broadcast off (any `session_user_id_meta_key` value still sends the id). Why it matters: a per-user identifier quietly leaves the machine toward servers the user may not associate with their chat identity. Suggestion: make transmission opt-in (`send_session_user_id: false` default, or accept `false`/`null` for `session_user_id_meta_key` as "do not send"), and say so explicitly in mcp.md's privacy notes.

2. Scope — this PR bundles two unrelated features (cron `continuity_max_chars` and MCP session-identity `_meta`) plus what looks like a silent control-flow fix (see #5), across 8 files. Splitting them makes bisect/review/revert far easier; the shared test-file collision risk with other open MCP PRs (#91460/#91451) grows the longer it stays monolithic.

3. tools/mcp_tool.py:1660 — `_call_tool_accepts_meta` returns True when signature introspection raises, so an exotic `call_tool` whose params can't be inspected gets `meta=` anyway and dies with TypeError instead of degrading gracefully. Suggestion: wrap the first meta-bearing attempt in try/except TypeError → retry once without meta, or invert the fallback to False (omit meta) on introspection failure.

4. cron/scheduler.py:70 — `(config.get("cron") or {}).get(...)` then `int(value)`: YAML `continuity_max_chars: true` becomes `int(True) == 1`, silently clamping continuity to 1 character rather than rejecting the bad type like strings do. Add an `isinstance(value, bool)` guard (or reject bools) alongside the existing exception handling.

5. tools/mcp_tool.py:5854 — the pre-existing `return tool_error("MCP server ... is not connected")` is re-indented one level deeper, which changes *when* it executes (now presumably only inside the reconnect-message branch). If intentional, it deserves its own commit + test since today it rides invisibly inside a feature diff; if accidental, it's a regression risk for the generic not-connected path.

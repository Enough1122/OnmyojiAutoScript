> AI code review — automated review for reference; please use your judgment.

Complete feature slice: config surface, classification hook, catalog exclusion, docs with a worked example, and the three behaviors I'd have demanded tests for are all tested (CSV/list parity, junk-entry tolerance, activation-path visibility, and the subtle "pinned tools vanish from search results" invariant).

- tools/tool_search.py:837 — issue (verification) — `classify_tools` now takes `always_visible`, but only two call sites were updated (`assemble_tool_defs`, `dispatch_tool_search`); please grep for any remaining caller that feeds model-facing arrays (e.g., mid-session reassembly after a toolset/MCP change) — why it matters — a missed call site means pins hold at session start but silently drop out when tools are reclassified later, an intermittent bug shape users will report as "my pin works until it doesn't".

- tools/tool_search.py:166 — nit — non-string entries are coerced via `str(name)` (42 → `"42"`, `true` → `"True"`) and kept in the set; the test deliberately pins this, but a one-line `logger.warning` for non-string entries would turn silent config typos into diagnosable events instead of mystery pins that never match.

- website/docs/user-guide/features/tool-search.md:95 — nit — worth half a sentence noting that pinning a *core* (never-deferred) tool name is a harmless no-op, since "exact tool names ... stay directly visible" invites users to pin `terminal` too and wonder about interactions.

No blocking issues found — item 1 is a quick grep-and-confirm.

— reviewer-b (automated review)

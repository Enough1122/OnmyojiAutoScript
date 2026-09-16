> AI code review — automated review for reference; please use your judgment.

Review of "fix(desktop): use --query-file for bot-to-bot @mention handoff instead of unsafe -q". The core fix is right: moving the composed message out of an inline `-q "..."` into a file kills the quote-truncation and `$()` execution classes entirely, the cold-roster path now reuses resolveRosterMentions so renamed bots stay taggable, and the rewritten quoting tests pin the new invariant well. Findings:

1. apps/desktop/src/plugins/hermes-bots/plugin.js:~11090 (shared temp path) — every handoff writes/reads the SAME `/tmp/dm.txt`: two concurrent handoffs (two tabs, two sessions, or two bots mentioning each other) can race and one recipient reads the other's message; the fixed predictable path is also symlink-squattable by other local users on shared hosts, and if the agent ever skips the write step it silently forwards the PREVIOUS handoff's content — use a unique path per handoff (`/tmp/hermes-dm-<uuid>.txt`, or instruct mktemp) and ideally tell the agent to delete it after dispatch.

2. agent/tool_guardrails.py:270 (duplicate parse + early return semantics) — `safe_json_loads(result)` runs a second time even though `data` was already parsed earlier in this function; more importantly the new early `return False, ""` means dict-shaped results whose failure signal lives outside error/success/message keys (`{"ok": false}`) are now always classified as success where the old string heuristic sometimes caught them — please confirm that's the intended contract and fold the re-parse into the existing `data`.

3. hermes_cli/mcp_catalog.py:574 (merge precedence) — when an auth.env spec name collides with a transport.env key, auth silently overwrites transport (dict update order); the new merge test covers disjoint keys only — either document "auth wins" or add a colliding-keys case so the precedence is pinned.

4. agent/tool_guardrails.py:19 (lazy-global import) — the `_TRIM_ERROR = None` + `global` + conditional-import dance works but is easy to break in refactors (a plain `from agent.display import _trim_error` inside the branch assigned to a LOCAL would silently pass None to the f-string call site later); consider a tiny helper or importlib comment noting the global rebinding is load-bearing.

5. Scope/reviewability — the title advertises the mention-handoff fix, but the PR also lands the #91166 tool-failure false-positive fix, the #89316 MCP auth-env wiring, and ~4k lines of Bots-pane feature work (group rooms, avatars, pane layout repair); nothing wrong individually, but mixed-motive PRs of this size are hard to bisect and revert — worth splitting future iterations.

The mcp_catalog regression tests deserve a shout-out: asserting the raw config keeps `${VAR}` templates while load_config resolves secrets is exactly the right pair of invariants.

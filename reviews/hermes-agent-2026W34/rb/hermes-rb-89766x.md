> AI code review — automated review for reference; please use your judgment.

Reviewed by reviewer-e (AI automated review).

Reasonable dependency-hygiene call with the right guardrails: keeping the MCP SDK opt-in via `[mcp]` (and still default-on for termux) avoids pinning Hermes' chosen major onto third-party MCP *server* environments that bring their own `mcp`, the test pins both halves of the contract (`all` excludes it, the `mcp` extra still exists), and the comment explains the why for future extra-shufflers.

One thing to land alongside it:

1. Release notes — this changes what `pip install .[all]` / `uv sync --extra all` delivers: existing users who relied on `all` for MCP *client* tooling silently lose it on upgrade until they add `[mcp]`. That deserves an explicit upgrade-note ("MCP is now opt-in via the `mcp` extra") so the first broken MCP integration after update doesn't read as a bug.
